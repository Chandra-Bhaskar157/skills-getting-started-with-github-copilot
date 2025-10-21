from fastapi.testclient import TestClient
import json

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Should be a dict containing at least one activity
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_student@mergington.edu"

    # Ensure the test email is not present initially
    activities[activity]["participants"] = [p for p in activities[activity]["participants"] if p != email]

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Check that the participant appears in the activity
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email in data[activity]["participants"]

    # Unregister via DELETE endpoint
    resp = client.request(
        "DELETE",
        f"/activities/{activity}/participants",
        json={"email": email},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "Unregistered" in body.get("message", "")

    # Ensure participant no longer present
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]
