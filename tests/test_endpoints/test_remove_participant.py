from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_remove_existing_participant_returns_200():
    # Arrange
    email = "daniel@mergington.edu"  # Exists in Chess Club

    # Act
    response = client.delete("/activities/Chess%20Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"


def test_remove_existing_participant_deletes_from_list():
    # Arrange
    email = "emma@mergington.edu"  # Exists in Programming Class

    # Act
    client.delete("/activities/Programming%20Class/participants", params={"email": email})

    # Assert
    activities = client.get("/activities").json()
    assert email not in activities["Programming Class"]["participants"]


def test_remove_returns_correct_message():
    # Arrange
    email = "sophia@mergington.edu"  # Exists in Programming Class

    # Act
    response = client.delete("/activities/Programming%20Class/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Programming Class"


def test_remove_nonexistent_activity_returns_404():
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete("/activities/Nonexistent/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    email = "nonexistent@mergington.edu"

    # Act
    response = client.delete("/activities/Chess%20Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_empty_email_returns_error():
    # Arrange
    email = ""

    # Act
    response = client.delete("/activities/Chess%20Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 422  # FastAPI validation error


def test_remove_activity_name_url_encoding():
    # Arrange
    email = "olivia@mergington.edu"  # Exists in Gym Class

    # Act
    response = client.delete("/activities/Gym%20Class/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert email not in activities["Gym Class"]["participants"]


def test_remove_participant_list_order_preserved():
    # Arrange
    activity_name = "Track and Field"
    initial_participants = client.get("/activities").json()[activity_name]["participants"].copy()

    # Act
    client.delete(f"/activities/{activity_name}/participants", params={"email": initial_participants[0]})

    # Assert
    activities = client.get("/activities").json()
    remaining = activities[activity_name]["participants"]
    assert len(remaining) == len(initial_participants) - 1
    # Order should be preserved (remove only the specified email)
    expected_remaining = [p for p in initial_participants if p != initial_participants[0]]
    assert remaining == expected_remaining


def test_remove_multiple_calls_on_same_activity():
    # Arrange
    activity_name = "Music Ensemble"
    initial_count = len(client.get("/activities").json()[activity_name]["participants"])

    # Act
    client.delete(f"/activities/{activity_name}/participants", params={"email": "noah@mergington.edu"})
    client.delete(f"/activities/{activity_name}/participants", params={"email": "ava@mergington.edu"})

    # Assert
    activities = client.get("/activities").json()
    assert len(activities[activity_name]["participants"]) == initial_count - 2


def test_remove_all_participants_leaves_empty_list():
    # Arrange
    activity_name = "Debate Team"
    participants = client.get("/activities").json()[activity_name]["participants"].copy()

    # Act
    for email in participants:
        client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    activities = client.get("/activities").json()
    assert activities[activity_name]["participants"] == []