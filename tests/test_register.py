import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

import os
# Mocking environment variables before importing app
os.environ["MONGO_URL"] = "mongodb://localhost:27017"
os.environ["DB_NAME"] = "test_db"
os.environ["JWT_SECRET"] = "test-secret"

import backend
from backend.server import app

# Create mock database objects
mock_db = MagicMock()
mock_users_collection = MagicMock()
mock_db.users = mock_users_collection

# Override global db object in server module
backend.server.db = mock_db

client = TestClient(app)
app.router.on_startup.clear()
app.router.on_shutdown.clear()

def test_register_success():
    # Arrange
    # Configure mock collection methods
    mock_users_collection.find_one = AsyncMock(return_value=None)
    mock_users_collection.insert_one = AsyncMock(return_value=None)

    user_data = {
        "email": "testuser@example.com",
        "full_name": "Test User",
        "role": "tecnico",
        "password": "strongpassword123"
    }

    # Act
    response = client.post("/api/auth/register", json=user_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "tecnico"
    assert "password" not in data
    assert "id" in data

    # Verify mocked DB calls
    mock_users_collection.find_one.assert_called_once_with({"email": "testuser@example.com"}, {"_id": 0})
    mock_users_collection.insert_one.assert_called_once()

    # Assert password is not saved directly, but hashed
    inserted_doc = mock_users_collection.insert_one.call_args[0][0]
    assert "password" not in inserted_doc
    assert "hashed_password" in inserted_doc


def test_register_duplicate_email():
    # Arrange
    # Configure mock collection methods
    mock_users_collection.find_one = AsyncMock(return_value={"email": "testuser@example.com", "id": "123"})

    user_data = {
        "email": "testuser@example.com",
        "full_name": "Test User",
        "role": "tecnico",
        "password": "strongpassword123"
    }

    # Act
    response = client.post("/api/auth/register", json=user_data)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "El email ya está registrado"

    mock_users_collection.find_one.assert_called_once_with({"email": "testuser@example.com"}, {"_id": 0})
