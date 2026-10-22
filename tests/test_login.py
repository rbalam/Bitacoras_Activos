import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock
from backend.server import app

app.router.on_startup.clear()

@pytest.fixture(autouse=True)
def mock_db_and_auth(mocker):
    app.dependency_overrides = {}
    mocker.patch("backend.server.db")
    mocker.patch("backend.server.db.users.find_one", new_callable=AsyncMock)

@pytest.fixture
def mock_db_users(mocker):
    return mocker.patch("backend.server.db.users.find_one", new_callable=AsyncMock)

@pytest.fixture
def mock_verify_password(mocker):
    return mocker.patch("backend.server.verify_password")

@pytest.fixture
def mock_create_access_token(mocker):
    return mocker.patch("backend.server.create_access_token", return_value="fake_token")

@pytest.mark.asyncio
async def test_login_success(mock_db_users, mock_verify_password, mock_create_access_token):
    mock_db_users.return_value = {
        "email": "test@example.com",
        "hashed_password": "hashed",
        "full_name": "Test User",
        "role": "admin",
        "active": True,
        "id": "123",
        "created_at": "2023-01-01T00:00:00"
    }
    mock_verify_password.return_value = True

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={"email": "test@example.com", "password": "password"})

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake_token"
    assert response.json()["user"]["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login_success_created_at_datetime(mock_db_users, mock_verify_password, mock_create_access_token):
    from datetime import datetime, timezone
    mock_db_users.return_value = {
        "email": "test@example.com",
        "hashed_password": "hashed",
        "full_name": "Test User",
        "role": "admin",
        "active": True,
        "id": "123",
        "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc)
    }
    mock_verify_password.return_value = True

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={"email": "test@example.com", "password": "password"})

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake_token"
    assert response.json()["user"]["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login_invalid_credentials_not_found(mock_db_users, mock_verify_password):
    mock_db_users.return_value = None

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"
    mock_verify_password.assert_not_called()

@pytest.mark.asyncio
async def test_login_invalid_credentials_wrong_password(mock_db_users, mock_verify_password):
    mock_db_users.return_value = {
        "email": "test@example.com",
        "hashed_password": "hashed",
        "full_name": "Test User",
        "role": "admin",
        "active": True,
        "id": "123",
        "created_at": "2023-01-01T00:00:00"
    }
    mock_verify_password.return_value = False

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"

@pytest.mark.asyncio
async def test_login_inactive_user(mock_db_users, mock_verify_password):
    mock_db_users.return_value = {
        "email": "test@example.com",
        "hashed_password": "hashed",
        "full_name": "Test User",
        "role": "admin",
        "active": False,
        "id": "123",
        "created_at": "2023-01-01T00:00:00"
    }
    mock_verify_password.return_value = True

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={"email": "test@example.com", "password": "password"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Usuario inactivo"
