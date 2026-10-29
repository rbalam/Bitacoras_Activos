import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from server import app
import server
import jwt
from auth import JWT_SECRET, JWT_ALGORITHM

# Avoid global db connection error during testing startup
app.router.on_startup.clear()

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_db():
    with patch('server.db', new_callable=AsyncMock) as mock_db:
        # Avoid AsyncIOMotorDatabase object spec issue
        server.db = MagicMock()
        server.db.users.find_one = AsyncMock()
        yield server.db

def test_login_success(mock_db):
    mock_db.users.find_one.return_value = {
        "id": "123",
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "admin",
        "hashed_password": "fake_hash",
        "created_at": "2024-01-01T00:00:00Z",
        "active": True
    }

    with patch('server.verify_password', return_value=True):
        response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password"})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"

    # verify jwt payload
    payload = jwt.decode(data["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "123"
    assert payload["email"] == "test@example.com"
    assert payload["role"] == "admin"

def test_login_invalid_email(mock_db):
    mock_db.users.find_one.return_value = None

    response = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"

def test_login_invalid_password(mock_db):
    mock_db.users.find_one.return_value = {
        "id": "123",
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "admin",
        "hashed_password": "fake_hash",
        "created_at": "2024-01-01T00:00:00Z",
        "active": True
    }

    with patch('server.verify_password', return_value=False):
        response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"

def test_login_inactive_user(mock_db):
    mock_db.users.find_one.return_value = {
        "id": "123",
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "admin",
        "hashed_password": "fake_hash",
        "created_at": "2024-01-01T00:00:00Z",
        "active": False
    }

    with patch('server.verify_password', return_value=True):
        response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Usuario inactivo"
