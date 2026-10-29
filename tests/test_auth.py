import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

import backend.server
from backend.server import app

client = TestClient(app)

# Fixture to clear app startup/shutdown events
@pytest.fixture(autouse=True)
def mock_events():
    app.router.on_startup.clear()
    app.router.on_shutdown.clear()

@pytest.fixture
def mock_db():
    # Mock the global db in server
    with patch("backend.server.db", new_callable=AsyncMock) as mock_db_instance:
        yield mock_db_instance

def test_register_success(mock_db):
    # Setup mock
    mock_db.users.find_one = AsyncMock(return_value=None)
    mock_db.users.insert_one = AsyncMock()

    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "tecnico",
        "phone": "1234567890",
        "password": "securepassword123"
    }

    # Make request
    response = client.post("/api/auth/register", json=user_data)

    # Assertions
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert response.json()["full_name"] == "Test User"
    assert "id" in response.json()
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()

    # Verify db interactions
    mock_db.users.find_one.assert_called_once_with({"email": "test@example.com"}, {"_id": 0})
    mock_db.users.insert_one.assert_called_once()

    # Check inserted document
    inserted_doc = mock_db.users.insert_one.call_args[0][0]
    assert inserted_doc["email"] == "test@example.com"
    assert "hashed_password" in inserted_doc
    # Check that password was hashed, not stored in plaintext
    assert inserted_doc["hashed_password"] != "securepassword123"

def test_register_existing_email(mock_db):
    # Setup mock to return an existing user
    mock_db.users.find_one = AsyncMock(return_value={"email": "existing@example.com"})

    user_data = {
        "email": "existing@example.com",
        "full_name": "Existing User",
        "role": "admin",
        "password": "anotherpassword123"
    }

    # Make request
    response = client.post("/api/auth/register", json=user_data)

    # Assertions
    assert response.status_code == 400
    assert response.json() == {"detail": "El email ya está registrado"}

    # Verify db interactions
    mock_db.users.find_one.assert_called_once_with({"email": "existing@example.com"}, {"_id": 0})
    mock_db.users.insert_one.assert_not_called()
