"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import os
from pathlib import Path
import threading

# Replace direct imports with a safe import that gives a clear runtime error if fastapi is not installed.
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import RedirectResponse
except Exception as e:
    raise RuntimeError(
        "Missing required package 'fastapi'. Install dependencies with:\n"
        "  pip3 install -r /workspaces/skills-getting-started-with-github-copilot/requirements.txt"
    ) from e

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    # Sports-related activities
    "Soccer Team": {
        "description": "Team soccer practice, drills, and inter-school matches",
        "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": ["alex@mergington.edu", "nina@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Lap swimming, stroke improvement and safety training",
        "schedule": "Tuesdays and Thursdays, 5:00 PM - 6:30 PM",
        "max_participants": 18,
        "participants": ["liam@mergington.edu"]
    },
    # Artistic activities
    "Art Club": {
        "description": "Explore drawing, painting, and mixed media projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["zoe@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting workshops, rehearsals, and school productions",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 25,
        "participants": ["maria@mergington.edu"]
    },
    # Intellectual activities
    "Debate Team": {
        "description": "Practice argumentation, public speaking and tournaments",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["noah@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Problem solving, competition prep, and math enrichment",
        "schedule": "Saturdays, 10:00 AM - 12:00 PM",
        "max_participants": 20,
        "participants": ["chloe@mergington.edu"]
    }
}

# Simple lock to protect the in-memory activities store from concurrent writes
_store_lock = threading.Lock()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Protect modification and prevent duplicate signups / over-capacity
    with _store_lock:
        # Duplicate check
        if email in activity.get("participants", []):
            raise HTTPException(status_code=409, detail="Student already signed up for this activity")

        # Capacity check (if configured)
        maxp = activity.get("max_participants")
        if maxp is not None and len(activity.get("participants", [])) >= maxp:
            raise HTTPException(status_code=400, detail="Activity is full")

        activity.setdefault("participants", []).append(email)

    return {"message": f"Signed up {email} for {activity_name}"}
