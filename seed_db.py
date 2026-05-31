"""
Academic Commander — MongoDB Database Seeder.
Pushes default student profile, mastery topics, and today's schedule blocks
to the live MongoDB Atlas cluster configured in your .env file.
"""

import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = "academic_commander"

if not MONGO_URI:
    print("❌ Error: MONGO_URI is not set in your .env file.")
    exit(1)

print("Connecting to MongoDB Atlas cluster...")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# 1. Seed Student Profile
print("Seeding student profile...")
db["students"].delete_many({}) # clear old profiles
student_doc = {
    "user_id": "student_001",
    "name": "Aasrith K.",
    "student_id": "AC-2026-0429",
    "semester": "Spring 2026",
    "program": "B.Tech CS"
}
db["students"].insert_one(student_doc)
print("   - Inserted profile for student_001")

# 2. Seed Mastery Topics
print("Seeding mastery topics...")
db["weak_topic_index"].delete_many({}) # clear old topics
topics_list = [
    {"topic_id": "Linear Algebra", "mastery_score": 82, "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()},
    {"topic_id": "Probability & Statistics", "mastery_score": 65, "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()},
    {"topic_id": "Data Structures", "mastery_score": 91, "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()},
    {"topic_id": "Machine Learning Fundamentals", "mastery_score": 47, "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()},
    {"topic_id": "Database Systems", "mastery_score": 73, "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()},
    {"topic_id": "Computer Networks", "mastery_score": 34, "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()},
    {"topic_id": "Operating Systems", "mastery_score": 58, "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()},
    {"topic_id": "Discrete Mathematics", "mastery_score": 88, "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()},
    {"topic_id": "Software Engineering", "mastery_score": 71, "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()},
    {"topic_id": "Artificial Intelligence", "mastery_score": 52, "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()},
]
db["weak_topic_index"].insert_many(topics_list)
print(f"   - Seeded {len(topics_list)} topics inside weak_topic_index")

# 3. Seed Today's Daily Schedule Blocks
print("Seeding today's daily schedule blocks...")
db["daily_routine_blocks"].delete_many({}) # clear old schedule

# Use today's date for start_times
today_date_str = datetime.now().strftime("%Y-%m-%d")

schedule_blocks = [
    {
        "activity_name": "Linear Algebra Review",
        "start_time": f"{today_date_str}T08:00:00",
        "duration_minutes": 90,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "activity_name": "ML Fundamentals Lecture",
        "start_time": f"{today_date_str}T09:45:00",
        "duration_minutes": 90,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "activity_name": "Data Structures Practice",
        "start_time": f"{today_date_str}T11:30:00",
        "duration_minutes": 60,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "activity_name": "Database Systems Lab",
        "start_time": f"{today_date_str}T14:00:00",
        "duration_minutes": 90,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "activity_name": "Probability Problem Sets",
        "start_time": f"{today_date_str}T15:45:00",
        "duration_minutes": 60,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "activity_name": "Computer Networks Review",
        "start_time": f"{today_date_str}T17:00:00",
        "duration_minutes": 60,
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "activity_name": "AI Mid-Semester Prep Exam",
        "start_time": f"{today_date_str}T19:00:00",
        "duration_minutes": 90,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

db["daily_routine_blocks"].insert_many(schedule_blocks)
print(f"   - Seeded {len(schedule_blocks)} calendar events inside daily_routine_blocks")
print("\nDatabase successfully seeded with live data! The dashboard will now reflect this live information.")
