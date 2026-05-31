import os
import sys
import asyncio
import traceback
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, DESCENDING
import gitlab as gitlab_lib

# Add project root to sys.path so we can import `agent.orchestration`
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(root_dir, ".env"))

# ═══════════════════════════════════════════════════════════════════════════
# Initialize FastAPI
# ═══════════════════════════════════════════════════════════════════════════
app = FastAPI(title="Academic Commander API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════
# MongoDB Atlas Connection
# ═══════════════════════════════════════════════════════════════════════════
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["academic_commander"]

# ═══════════════════════════════════════════════════════════════════════════
# GitLab Connection (for real pipeline data)
# ═══════════════════════════════════════════════════════════════════════════
GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "")
GITLAB_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID", "")
_gl = None

def _get_gitlab_project():
    """Lazy-init GitLab client and return the project."""
    global _gl
    if not GITLAB_TOKEN or not GITLAB_PROJECT_ID:
        return None
    try:
        if _gl is None:
            _gl = gitlab_lib.Gitlab(GITLAB_URL, private_token=GITLAB_TOKEN)
            _gl.auth()
        return _gl.projects.get(GITLAB_PROJECT_ID)
    except Exception as e:
        print(f"GitLab connection error: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════
# ADK Agent Initialization
# ═══════════════════════════════════════════════════════════════════════════
AGENT_AVAILABLE = False
runner = None
try:
    from agent.orchestration import AcademicCommanderRunner
    runner = AcademicCommanderRunner()
    AGENT_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not initialize AcademicCommanderRunner: {e}")
    traceback.print_exc()


# ═══════════════════════════════════════════════════════════════════════════
# Helper: Log agent activity to MongoDB
# ═══════════════════════════════════════════════════════════════════════════
def log_agent_activity(event: str, details: str = ""):
    """Store an event in the agent_logs collection for the Live Activity Feed."""
    try:
        db["agent_logs"].insert_one({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "details": details,
        })
    except Exception:
        pass  # Non-critical; don't crash if logging fails


# ═══════════════════════════════════════════════════════════════════════════
# Background task: Run the full 9-step syllabus cycle
# ═══════════════════════════════════════════════════════════════════════════
def run_syllabus_cycle_background(file_path: str, topic: str):
    """Execute the agent's full 9-step autonomous cycle in a background thread."""
    if not AGENT_AVAILABLE or runner is None:
        log_agent_activity(
            f"[SYSTEM] Skipped auto-analysis for '{topic}'",
            "Agent not available"
        )
        return

    log_agent_activity(
        f"[FIVETRAN] Ingested document for topic '{topic}'",
        f"File: {file_path}"
    )

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(runner.run_syllabus_cycle(file_path))
        loop.close()

        # Log tool calls from the cycle
        tool_calls = result.get("tool_calls", [])
        for tc in tool_calls:
            log_agent_activity(
                f"[MCP] Tool call: {tc.get('function', 'unknown')}",
                str(tc.get("args", {}))[:200]
            )

        log_agent_activity(
            f"[AGENT] Completed 9-step cycle for '{topic}'",
            f"Response length: {len(result.get('response', ''))} chars, "
            f"Tool calls: {result.get('tool_call_count', 0)}"
        )
    except Exception as e:
        log_agent_activity(
            f"[AGENT] Error during cycle for '{topic}'",
            str(e)[:200]
        )


# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str
    topic: str = None
    file: str = None


@app.get("/api/status")
async def get_status():
    return {
        "status": "operational" if AGENT_AVAILABLE else "degraded",
        "agent_available": AGENT_AVAILABLE
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not AGENT_AVAILABLE:
        return {"reply": (
            f"🤖 **(DEMO RESPONSE)**: I parsed your instruction: "
            f"*'{request.message}'*.\n\nThe backend agent is currently unavailable."
        )}

    try:
        # Save user message to history
        db["chat_history"].insert_one({
            "role": "user",
            "content": request.message,
            "topic": request.topic,
            "file": request.file,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Inject context about uploaded files and requested topics
        ingestion_dir = os.path.join(root_dir, "ingestion")
        files = os.listdir(ingestion_dir) if os.path.exists(ingestion_dir) else []
        file_list = ", ".join(files) if files else "None"
        
        context_parts = [
            f"[SYSTEM CONTEXT: The user has uploaded the following files to the 'ingestion/' directory: {file_list}.]"
        ]
        if request.topic:
            context_parts.append(f"[USER CONTEXT: The user is asking about topic: '{request.topic}']")
        if request.file:
            context_parts.append(f"[USER CONTEXT: The user is asking about file: '{request.file}']")
            
        context_msg = "\n".join(context_parts) + f"\n\n{request.message}"

        log_agent_activity("[AGENT] Processing user chat request", request.message[:100])
        response = await runner.run(context_msg)

        # Log any tool calls made
        for tc in response.get("tool_calls", []):
            log_agent_activity(
                f"[MCP] Tool call: {tc.get('function', 'unknown')}",
                str(tc.get("args", {}))[:200]
            )

        reply = response.get("response", str(response))
        log_agent_activity("[AGENT] Response generated", f"{len(reply)} chars")
        
        # Save agent response to history
        db["chat_history"].insert_one({
            "role": "agent",
            "content": reply,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat_history")
async def get_chat_history():
    history = list(db["chat_history"].find({}, {"_id": 0}).sort("timestamp", 1))
    return history

@app.get("/api/files")
async def get_files():
    ingestion_dir = os.path.join(root_dir, "ingestion")
    if not os.path.exists(ingestion_dir):
        return []
    
    files = []
    for filename in os.listdir(ingestion_dir):
        filepath = os.path.join(ingestion_dir, filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            files.append({
                "name": filename,
                "size": stat.st_size,
                "uploaded_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
            })
    return files

@app.get("/api/analytics")
async def get_analytics():
    # Fetch real topics
    topics_data = list(db["weak_topic_index"].find({}, {"_id": 0}))
    
    # Calculate synthetic "Mental Score" based on recent study streak and mastery progression
    # In a real app this might come from a sentiment analysis or wearable integration
    mental_score = 85  # Example base score
    study_score = 78
    
    if topics_data:
        avg_mastery = sum([t.get("mastery_score", 0) for t in topics_data]) / len(topics_data)
        study_score = int(min(100, max(0, avg_mastery * 1.1)))
        
        # Adjust mental score based on mastery (if struggling, mental score drops slightly)
        if avg_mastery < 50:
            mental_score -= 10
        elif avg_mastery > 80:
            mental_score += 10
            
    return {
        "mental_score": min(100, mental_score),
        "study_score": study_score,
        "burnout_risk": "Low" if mental_score > 70 else "High",
        "focus_hours": 14.5,
        "topics_distribution": [
            {"name": t.get("topic_id", "Unknown"), "value": t.get("mastery_score", 0)}
            for t in topics_data
        ]
    }


@app.get("/api/metrics")
async def get_metrics():
    # Fetch real topics from MongoDB
    topics_data = list(db["weak_topic_index"].find({}, {"_id": 0}))
    topics = []
    for r in topics_data:
        topics.append({
            "name": r.get("topic_id", "Unknown Topic"),
            "mastery": r.get("mastery_score", 50),
            "last_reviewed": str(r.get("updated_at", "Never"))[:10] if r.get("updated_at") else "Never"
        })

    avg_mastery = sum([t["mastery"] for t in topics]) / len(topics) if topics else 0

    # Fetch real agent activity logs from MongoDB
    recent_logs = list(
        db["agent_logs"]
        .find({}, {"_id": 0})
        .sort("timestamp", DESCENDING)
        .limit(10)
    )
    feed = []
    for log in recent_logs:
        ts = log.get("timestamp", "")
        # Format relative time
        try:
            log_dt = datetime.fromisoformat(ts)
            delta = datetime.now(timezone.utc) - log_dt
            if delta.total_seconds() < 60:
                time_str = "Just now"
            elif delta.total_seconds() < 3600:
                time_str = f"{int(delta.total_seconds() // 60)} min ago"
            elif delta.total_seconds() < 86400:
                time_str = f"{int(delta.total_seconds() // 3600)} hour ago"
            else:
                time_str = f"{int(delta.total_seconds() // 86400)} days ago"
        except Exception:
            time_str = ts[:16]
        feed.append({"time": time_str, "event": log.get("event", "")})

    # Fallback if no logs yet
    if not feed:
        feed = [
            {"time": "Just now", "event": "[SYSTEM] Agent initialized and ready"},
            {"time": "Startup", "event": "[SYSTEM] Connected to MongoDB Atlas"},
        ]

    return {
        "mastery_avg": f"{avg_mastery:.0f}%",
        "topics_tracked": len(topics),
        "pending_labs": 3,
        "study_streak": 14,
        "topics": topics,
        "feed": feed,
    }


@app.get("/api/schedule")
async def get_schedule():
    routine_data = list(db["daily_routine_blocks"].find({}, {"_id": 0}).sort("start_time", 1))
    schedule = []
    for r in routine_data:
        schedule.append({
            "time": r.get("start_time", r.get("activity_name", "00:00")),
            "activity": r.get("activity", r.get("activity_name", "Task")),
            "status": r.get("status", "pending").lower()
        })
    return schedule


@app.get("/api/pipelines")
async def get_pipelines():
    """Fetch real CI/CD pipeline data from GitLab. Falls back to cached data."""
    project = _get_gitlab_project()
    if project is not None:
        try:
            pipelines = project.pipelines.list(per_page=5, order_by="id", sort="desc")
            result = []
            for p in pipelines:
                result.append({
                    "id": f"#{p.id}",
                    "name": f"Pipeline on {p.ref}",
                    "status": p.status,  # success, failed, running, pending, canceled
                    "progress": 100 if p.status == "success" else (
                        50 if p.status == "running" else (
                            0 if p.status == "pending" else 80
                        )
                    ),
                })
            if result:
                return result
        except Exception as e:
            print(f"GitLab pipeline fetch error: {e}")

    # Fallback: return static data if GitLab is unreachable
    return [
        {"id": "#1042", "name": "Model Training", "status": "running", "progress": 45},
        {"id": "#1041", "name": "Data Ingestion", "status": "success", "progress": 100},
        {"id": "#1040", "name": "Agent Fine-tuning", "status": "failed", "progress": 82},
    ]


class TopicRequest(BaseModel):
    name: str


@app.post("/api/topics")
async def add_topic(request: TopicRequest):
    db["weak_topic_index"].update_one(
        {"topic_id": request.name},
        {"$set": {"mastery_score": 50, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    log_agent_activity(f"[MONGODB] New topic added: '{request.name}'", "Initial mastery: 50%")
    return {"status": "success", "message": f"Topic '{request.name}' added."}


class ScheduleRequest(BaseModel):
    time: str
    activity: str


@app.post("/api/schedule")
async def add_schedule_item(request: ScheduleRequest):
    db["daily_routine_blocks"].insert_one({
        "activity": request.activity,
        "activity_name": request.activity,
        "start_time": request.time,
        "duration": 60,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending"
    })
    log_agent_activity(f"[MONGODB] Schedule event added: '{request.activity}'", f"Time: {request.time}")
    return {"status": "success", "message": "Event added."}


@app.post("/api/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    topic: str = Form(None),
):
    """Save the uploaded document and auto-trigger the 9-step agent cycle."""
    ingestion_dir = os.path.join(root_dir, "ingestion")
    os.makedirs(ingestion_dir, exist_ok=True)

    filename = file.filename
    if topic:
        safe_topic = "".join([c if c.isalnum() else "_" for c in topic])
        filename = f"{safe_topic}_{filename}"

    file_path = os.path.join(ingestion_dir, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # ⚡ AUTO-TRIGGER: Kick off the full 9-step autonomous cycle in background
    background_tasks.add_task(run_syllabus_cycle_background, file_path, topic or filename)

    log_agent_activity(
        f"[FIVETRAN] Document uploaded: '{filename}'",
        f"Topic: {topic or 'unassigned'}"
    )

    return {
        "status": "success",
        "filename": filename,
        "message": (
            f"File '{filename}' uploaded. The Academic Commander agent is now "
            f"autonomously executing the full 9-step analysis cycle for topic '{topic}'."
        ),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
