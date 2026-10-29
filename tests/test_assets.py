import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

import os
os.environ["MONGO_URL"] = "mongodb://localhost:27017"
os.environ["DB_NAME"] = "testdb"
os.environ["JWT_SECRET"] = "testsecret"

# Mock db
mock_db = MagicMock()
mock_db.assets = AsyncMock()

import backend.server
backend.server.db = mock_db
backend.server.app.router.on_startup.clear()

from backend.server import app, get_current_user
from backend.models import User
import uuid
from jose import jwt

client = TestClient(app)

# Helper function to generate valid JWT
def create_test_token(user_id: str):
    token = jwt.encode({"sub": user_id}, "testsecret", algorithm="HS256")
    return token

async def override_get_current_user():
    return User(
        id="test_user_id",
        email="test@test.com",
        full_name="Test User",
        role="admin"
    )

app.dependency_overrides[get_current_user] = override_get_current_user

def test_create_asset_success():
    # Setup mock behavior
    mock_db.assets.find_one.return_value = None

    asset_data = {
        "serial_number": "SN12345",
        "etiqueta_id": "LBL001",
        "modelo": "Model X",
        "marca": "Brand Y",
        "capacidad": "10L",
        "area_restaurante": "Cocina",
        "sucursal": "Centro",
        "costo_equipo": 1500.0,
        "estado": "operativo"
    }

    response = client.post("/api/assets", json=asset_data)

    assert response.status_code == 201
    assert response.json()["serial_number"] == "SN12345"
    assert response.json()["created_by"] == "test_user_id"
    mock_db.assets.insert_one.assert_called_once()

def test_create_asset_duplicate():
    mock_db.assets.find_one.return_value = {"serial_number": "SN12345"}

    asset_data = {
        "serial_number": "SN12345",
        "etiqueta_id": "LBL001",
        "modelo": "Model X",
        "marca": "Brand Y",
        "capacidad": "10L",
        "area_restaurante": "Cocina",
        "sucursal": "Centro",
        "costo_equipo": 1500.0,
        "estado": "operativo"
    }

    response = client.post("/api/assets", json=asset_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Ya existe un activo con este número de serie"

def test_create_asset_missing_fields():
    asset_data = {
        "serial_number": "SN12345"
    }

    response = client.post("/api/assets", json=asset_data)

    assert response.status_code == 422
