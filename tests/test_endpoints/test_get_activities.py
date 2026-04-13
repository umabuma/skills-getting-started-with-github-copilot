from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_returns_200():
    # Arrange - No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200


def test_get_activities_returns_dict():
    # Arrange - No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    activities = response.json()
    assert isinstance(activities, dict)


def test_get_activities_has_all_expected_activities():
    # Arrange - No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    activities = response.json()
    expected_activities = [
        "Chess Club", "Programming Class", "Gym Class", "Basketball",
        "Track and Field", "Art Club", "Music Ensemble", "Debate Team",
        "Science Club"
    ]
    assert len(activities) == len(expected_activities)
    for activity in expected_activities:
        assert activity in activities


def test_activity_structure_has_required_fields():
    # Arrange - No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    activities = response.json()
    for activity_name, activity_data in activities.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data


def test_participants_are_list_type():
    # Arrange - No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    activities = response.json()
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["participants"], list)


def test_max_participants_is_integer():
    # Arrange - No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    activities = response.json()
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["max_participants"], int)


def test_initial_participant_counts_match_expected():
    # Arrange - No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    activities = response.json()
    expected_counts = {
        "Chess Club": 2,
        "Programming Class": 2,
        "Gym Class": 2,
        "Basketball": 1,
        "Track and Field": 2,
        "Art Club": 1,
        "Music Ensemble": 2,
        "Debate Team": 1,
        "Science Club": 2
    }
    for activity_name, expected_count in expected_counts.items():
        assert len(activities[activity_name]["participants"]) == expected_count