import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities state before each test."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_data():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert expected_activity in activities
    assert "description" in activities[expected_activity]
    assert "participants" in activities[expected_activity]


def test_signup_for_activity_appends_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    before_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert len(app_module.activities[activity_name]["participants"]) == before_count + 1
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={duplicate_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "daniel@mergington.edu"
    assert email_to_remove in app_module.activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email_to_remove}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email_to_remove} from {activity_name}"
    assert email_to_remove not in app_module.activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing@student.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={missing_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
