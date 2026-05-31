"""
MongoDB Atlas MCP Server for Academic Commander.

Provides tools to manage student profiles, mastery tracking, weak-area
indexing, and daily routine scheduling via a MongoDB Atlas backend.
All collections live in the ``academic_commander`` database.

Environment variables
---------------------
MONGO_URI : str
    MongoDB Atlas connection string (e.g. ``mongodb+srv://...``).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pymongo import MongoClient, ASCENDING

load_dotenv()

MONGO_URI: str = os.getenv("MONGO_URI", "")
DB_NAME: str = "academic_commander"

mcp = FastMCP("MongoDB MCP – Academic Commander")

# ---------------------------------------------------------------------------
# Helper: lazy MongoDB client
# ---------------------------------------------------------------------------
_client: MongoClient | None = None


def _get_db():
    """Return the ``academic_commander`` database handle, creating the client
    on first call so the module can be imported without a live connection."""
    global _client
    if _client is None:
        if not MONGO_URI:
            raise RuntimeError("MONGO_URI environment variable is not set.")
        _client = MongoClient(MONGO_URI)
    return _client[DB_NAME]


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def fetch_student_profile(user_id: str) -> dict[str, Any]:
    """Load a student's mastery state from the ``students`` collection.

    Parameters
    ----------
    user_id : str
        Unique identifier for the student (e.g. university roll number).

    Returns
    -------
    dict
        The student document, or an error message if not found.
    """
    try:
        db = _get_db()
        doc = db["students"].find_one({"user_id": user_id}, {"_id": 0})
        if doc is None:
            return {"error": f"No student found with user_id '{user_id}'."}
        return {"student": doc}
    except Exception as exc:
        return {"error": f"Failed to fetch student profile: {exc}"}


@mcp.tool()
def update_weak_areas(topic_id: str, mastery_delta: int) -> dict[str, Any]:
    """Atomic upsert of mastery scores in the ``weak_topic_index`` collection.

    The mastery score is incremented by *mastery_delta* and then clamped to
    the **0–100** range so it never overflows or underflows.

    Parameters
    ----------
    topic_id : str
        Identifier of the topic whose score should be updated.
    mastery_delta : int
        Signed integer to add to the current mastery score.

    Returns
    -------
    dict
        Confirmation with the new (clamped) mastery score.
    """
    try:
        db = _get_db()
        collection = db["weak_topic_index"]

        # Fetch current score (default 50 for new topics)
        existing = collection.find_one({"topic_id": topic_id})
        current_score: int = existing.get("mastery_score", 50) if existing else 50

        new_score: int = max(0, min(100, current_score + mastery_delta))

        collection.update_one(
            {"topic_id": topic_id},
            {
                "$set": {
                    "mastery_score": new_score,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            },
            upsert=True,
        )

        return {
            "topic_id": topic_id,
            "previous_score": current_score,
            "delta": mastery_delta,
            "new_score": new_score,
        }
    except Exception as exc:
        return {"error": f"Failed to update weak areas: {exc}"}


@mcp.tool()
def inject_routine_block(
    activity_name: str,
    start_time: str,
    duration_minutes: int,
) -> dict[str, Any]:
    """Insert a calendar event into the ``daily_routine_blocks`` collection.

    Parameters
    ----------
    activity_name : str
        Human-readable name for the activity (e.g. "Revise Linear Algebra").
    start_time : str
        ISO-8601 datetime string for the block start (e.g. "2026-05-29T09:00:00").
    duration_minutes : int
        Length of the block in minutes.

    Returns
    -------
    dict
        The inserted block document.
    """
    try:
        db = _get_db()
        block = {
            "activity_name": activity_name,
            "start_time": start_time,
            "duration_minutes": duration_minutes,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        result = db["daily_routine_blocks"].insert_one(block)
        block["_id"] = str(result.inserted_id)
        return {"block": block}
    except Exception as exc:
        return {"error": f"Failed to inject routine block: {exc}"}


@mcp.tool()
def get_daily_schedule() -> dict[str, Any]:
    """Return today's schedule blocks sorted by ``start_time``.

    Only blocks whose ``start_time`` falls within the current UTC day are
    returned.

    Returns
    -------
    dict
        A list of today's routine blocks, sorted chronologically.
    """
    try:
        db = _get_db()
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        cursor = (
            db["daily_routine_blocks"]
            .find(
                {
                    "start_time": {
                        "$gte": today_str + "T00:00:00",
                        "$lte": today_str + "T23:59:59",
                    }
                },
                {"_id": 0},
            )
            .sort("start_time", ASCENDING)
        )

        blocks = list(cursor)
        return {"date": today_str, "blocks": blocks, "count": len(blocks)}
    except Exception as exc:
        return {"error": f"Failed to get daily schedule: {exc}"}


@mcp.tool()
def get_all_topics() -> dict[str, Any]:
    """List all tracked topics with their mastery scores.

    Reads every document in the ``weak_topic_index`` collection.

    Returns
    -------
    dict
        A list of topic objects with ``topic_id``, ``mastery_score``, and
        ``updated_at`` fields.
    """
    try:
        db = _get_db()
        topics = list(db["weak_topic_index"].find({}, {"_id": 0}).sort("topic_id", ASCENDING))
        return {"topics": topics, "count": len(topics)}
    except Exception as exc:
        return {"error": f"Failed to list topics: {exc}"}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
