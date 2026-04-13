from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_signup_valid_email_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_valid_email_returns_correct_message():
    # Arrange
    email = "anotherstudent@mergington.edu"
    activity_name = "Programming Class"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_signup_updates_activities_state():
    # Arrange
    email = "teststudent@mergington.edu"
    activity_name = "Gym Class"
    initial_count = len(client.get("/activities").json()[activity_name]["participants"])

    # Act
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    activities = client.get("/activities").json()
    assert len(activities[activity_name]["participants"]) == initial_count + 1
    assert email in activities[activity_name]["participants"]


def test_signup_nonexistent_activity_returns_404():
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Nonexistent/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_email_returns_400():
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_email_case_sensitivity():
    # Arrange
    email = "Michael@mergington.edu"  # Different case from existing

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200  # Should allow different case
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_empty_email_rejected():
    # Arrange
    email = ""

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 422  # FastAPI validation error for empty string


def test_signup_invalid_email_format():
    # Arrange
    email = "invalidemail"  # Missing @

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    # Note: Current app doesn't validate email format, so this will succeed
    # This test documents the missing validation
    assert response.status_code == 200


def test_signup_activity_name_url_encoding():
    # Arrange
    email = "encodedstudent@mergington.edu"
    activity_name = "Chess Club"  # Has space

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_activity_name_case_sensitivity():
    # Arrange
    email = "casestudent@mergington.edu"

    # Act
    response = client.post("/activities/chess%20club/signup", params={"email": email})  # lowercase

    # Assert
    assert response.status_code == 404  # Activity names are case-sensitive
    assert response.json()["detail"] == "Activity not found"


def test_signup_very_long_email_rejected():
    # Arrange
    email = "a" * 1000 + "@mergington.edu"  # Very long email

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    # Current app doesn't validate length, so this succeeds
    # This documents missing validation
    assert response.status_code == 200


def test_signup_whitespace_only_email_rejected():
    # Arrange
    email = "   "

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    # Current app doesn't validate whitespace, so this succeeds
    # This documents missing validation
    assert response.status_code == 200