from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_query_param_missing_email_raises_error():
    # Arrange - No email parameter

    # Act
    response = client.post("/activities/Chess%20Club/signup")

    # Assert
    assert response.status_code == 422  # Missing required query param


def test_empty_activity_name_string():
    # Arrange
    email = "test@mergington.edu"

    # Act
    response = client.post("/activities//signup", params={"email": email})  # Empty activity name

    # Assert
    assert response.status_code == 404  # Empty string not found


def test_activity_name_with_special_characters():
    # Arrange
    email = "special@mergington.edu"

    # Act
    response = client.post("/activities/Test%20%26%20Activity/signup", params={"email": email})  # & in name

    # Assert
    assert response.status_code == 404  # Activity doesn't exist


def test_null_values_rejected():
    # Arrange - Try to pass None (though FastAPI handles this)

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": None})

    # Assert
    assert response.status_code == 422  # Invalid type


def test_unicode_email_handling():
    # Arrange
    email = "tëst@mergington.edu"  # Unicode characters

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    # Current app accepts unicode, so this succeeds
    assert response.status_code == 200


def test_signup_response_has_required_fields():
    # Arrange
    email = "response@mergington.edu"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)


def test_remove_response_has_required_fields():
    # Arrange
    email = "response2@mergington.edu"

    # Act
    client.post("/activities/Chess%20Club/signup", params={"email": email})
    response = client.delete("/activities/Chess%20Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)


def test_error_response_has_detail_field():
    # Arrange
    email = "duplicate@mergington.edu"

    # Act - First signup
    client.post("/activities/Chess%20Club/signup", params={"email": email})
    # Second signup (duplicate)
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)


def test_http_status_codes_are_correct():
    # Arrange
    valid_email = "status@mergington.edu"
    invalid_email = "duplicate@mergington.edu"

    # Act - Valid signup
    response = client.post("/activities/Chess%20Club/signup", params={"email": valid_email})
    assert response.status_code == 200

    # Invalid activity
    response = client.post("/activities/Invalid/signup", params={"email": valid_email})
    assert response.status_code == 404

    # Duplicate signup
    response = client.post("/activities/Chess%20Club/signup", params={"email": invalid_email})
    client.post("/activities/Chess%20Club/signup", params={"email": invalid_email})  # First time
    response = client.post("/activities/Chess%20Club/signup", params={"email": invalid_email})  # Duplicate
    assert response.status_code == 400

    # Valid removal
    response = client.delete("/activities/Chess%20Club/participants", params={"email": valid_email})
    assert response.status_code == 200

    # Remove non-existent
    response = client.delete("/activities/Chess%20Club/participants", params={"email": "nonexistent@mergington.edu"})
    assert response.status_code == 404