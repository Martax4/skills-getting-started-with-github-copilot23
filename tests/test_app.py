from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original))


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities


def test_signup_for_activity_adds_participant():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_404():
    response = client.post(
        "/activities/Unknown Activity/signup?email=student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_for_existing_participant_returns_400():
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json() == {
        "message": f"Removed {email} from {activity_name}"
    }


def test_unregister_for_unknown_activity_returns_404():
    response = client.delete(
        "/activities/Unknown Activity/unregister?email=student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_for_missing_participant_returns_400():
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
