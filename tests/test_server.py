import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_existing_user(async_client: AsyncClient, mock_db):
    # Setup: Insert an existing user into the mock database
    existing_user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "tecnico",
        "hashed_password": "fake_hash",
        "active": True
    }
    await mock_db.users.insert_one(existing_user_data)

    # Action: Try to register a user with the same email
    new_user_data = {
        "email": "test@example.com",
        "full_name": "New User",
        "role": "tecnico",
        "password": "newpassword123"
    }

    response = await async_client.post("/api/auth/register", json=new_user_data)

    # Assert: Should return 400 Bad Request with specific error message
    assert response.status_code == 400
    assert response.json() == {"detail": "El email ya está registrado"}
