import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set env vars to avoid startup errors
os.environ["MONGO_URL"] = "mongodb://localhost:27017"
os.environ["DB_NAME"] = "test_db"
os.environ["JWT_SECRET"] = "test_secret"

import server
from server import app
from auth import create_access_token

# We need to mock the startup event since it accesses db.configs which raises
# Event loop is closed. We can clear the startup events for tests.
app.router.on_startup.clear()

class MockCollection:
    def __init__(self, return_value=None):
        self._return_value = return_value
        self.calls = []

    async def find_one(self, query, projection=None):
        self.calls.append((query, projection))
        return self._return_value

@pytest.fixture
def mock_db_users(mocker):
    mock_coll = MockCollection()
    # We patch the 'users' attribute on server.db to be our MockCollection
    mocker.patch.object(server.db, 'users', mock_coll)
    return mock_coll

@pytest.fixture
def valid_user_data():
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "admin",
        "phone": "123456789",
        "active": True,
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

def test_endpoint_valid_token(mock_db_users, valid_user_data):
    mock_db_users._return_value = valid_user_data
    token = create_access_token(data={"sub": valid_user_data["id"]})

    with TestClient(app) as client:
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == valid_user_data["email"]
    assert data["id"] == valid_user_data["id"]
    assert len(mock_db_users.calls) == 1
    assert mock_db_users.calls[0][0] == {"id": valid_user_data["id"]}

def test_endpoint_valid_token_user_not_found(mock_db_users, valid_user_data):
    mock_db_users._return_value = None
    token = create_access_token(data={"sub": valid_user_data["id"]})

    with TestClient(app) as client:
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Usuario no encontrado"
    assert len(mock_db_users.calls) == 1
    assert mock_db_users.calls[0][0] == {"id": valid_user_data["id"]}

def test_endpoint_invalid_token():
    with TestClient(app) as client:
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido o expirado"

def test_endpoint_missing_credentials():
    with TestClient(app) as client:
        response = client.get("/api/auth/me")

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"
