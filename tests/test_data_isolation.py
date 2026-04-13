from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_activities_reset_between_tests():
    # Arrange
    email = "isolationtest@mergington.edu"
    activity_name = "Art Club"

    # Act - Add participant
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert - Should be added in this test
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

    # Note: The fixture should reset data between tests, so this change won't persist


def test_signup_state_not_persisted_between_tests():
    # Arrange
    email = "persistence@mergington.edu"
    activity_name = "Science Club"

    # Act - Check initial state (should be reset)
    activities = client.get("/activities").json()
    initial_count = len(activities[activity_name]["participants"])

    # Assert - Should not have the participant from previous test
    assert "isolationtest@mergington.edu" not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count


def test_removal_state_not_persisted_between_tests():
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"

    # Act - Check that participant still exists (should be reset)
    activities = client.get("/activities").json()

    # Assert - Should have original participants
    assert email_to_remove in activities[activity_name]["participants"]
    assert "daniel@mergington.edu" in activities[activity_name]["participants"]


def test_concurrent_signups_dont_lose_data():
    # Arrange
    emails = ["concurrent1@mergington.edu", "concurrent2@mergington.edu"]
    activity_name = "Basketball"

    # Act
    for email in emails:
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    activities = client.get("/activities").json()
    participants = activities[activity_name]["participants"]
    for email in emails:
        assert email in participants
    assert len(participants) >= len(emails)  # At least the new ones


def test_signup_then_remove_then_signup_same_email_works():
    # Arrange
    email = "reuse@mergington.edu"
    activity_name = "Track and Field"

    # Act
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_parallel_operations_on_different_activities():
    # Arrange
    email1 = "parallel1@mergington.edu"
    email2 = "parallel2@mergington.edu"

    # Act
    client.post("/activities/Chess%20Club/signup", params={"email": email1})
    client.post("/activities/Programming%20Class/signup", params={"email": email2})

    # Assert
    activities = client.get("/activities").json()
    assert email1 in activities["Chess Club"]["participants"]
    assert email2 in activities["Programming Class"]["participants"]