import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from backend.services.config_service import ConfigService

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.configs = MagicMock()
    # find_one is async
    db.configs.find_one = AsyncMock()
    # update_one is async
    db.configs.update_one = AsyncMock()
    # find is sync, returns a cursor which has async to_list
    return db

@pytest.fixture
def config_service(mock_db):
    return ConfigService(db=mock_db)

@pytest.mark.asyncio
async def test_load_cache(config_service, mock_db):
    # Setup mock data
    mock_configs = [
        {"key": "KEY1", "value": "value1"},
        {"key": "KEY2", "value": "value2"}
    ]

    # Mock the database cursor and to_list
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=mock_configs)
    mock_db.configs.find.return_value = mock_cursor

    # Execute
    await config_service.load_cache()

    # Verify
    mock_db.configs.find.assert_called_once_with({"active": True}, {"_id": 0})
    mock_cursor.to_list.assert_called_once_with(1000)
    assert config_service._cache == {"KEY1": "value1", "KEY2": "value2"}
    assert config_service._cache_loaded is True

@pytest.mark.asyncio
async def test_get_not_loaded(config_service, mock_db):
    # Setup mock data
    mock_configs = [{"key": "KEY1", "value": "value1"}]
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=mock_configs)
    mock_db.configs.find.return_value = mock_cursor

    # Execute
    result = await config_service.get("KEY1")

    # Verify
    assert result == "value1"
    assert config_service._cache_loaded is True

@pytest.mark.asyncio
async def test_get_already_loaded(config_service, mock_db):
    # Setup state
    config_service._cache = {"KEY1": "value1"}
    config_service._cache_loaded = True

    # Execute
    result = await config_service.get("KEY1")

    # Verify
    assert result == "value1"
    mock_db.configs.find.assert_not_called()

@pytest.mark.asyncio
async def test_get_default(config_service, mock_db):
    # Setup state
    config_service._cache = {}
    config_service._cache_loaded = True

    # Execute
    result = await config_service.get("MISSING_KEY", "default_value")

    # Verify
    assert result == "default_value"

@pytest.mark.asyncio
async def test_set_existing(config_service, mock_db):
    # Setup mock data
    mock_db.configs.find_one.return_value = {"key": "KEY1", "value": "old_value"}

    # Setup state
    config_service._cache = {"KEY1": "old_value"}
    config_service._cache_loaded = True

    # Execute
    result = await config_service.set("KEY1", "new_value", "user123")

    # Verify
    assert result is True
    mock_db.configs.find_one.assert_called_once_with({"key": "KEY1"}, {"_id": 0})
    mock_db.configs.update_one.assert_called_once_with(
        {"key": "KEY1"},
        {
            "$set": {
                "value": "new_value",
                "updated_at": ANY,
                "updated_by": "user123"
            }
        }
    )
    assert config_service._cache["KEY1"] == "new_value"

@pytest.mark.asyncio
async def test_set_not_existing(config_service, mock_db):
    # Setup mock data
    mock_db.configs.find_one.return_value = None

    # Setup state
    config_service._cache = {}
    config_service._cache_loaded = True

    # Execute
    result = await config_service.set("MISSING_KEY", "new_value", "user123")

    # Verify
    assert result is False
    mock_db.configs.find_one.assert_called_once_with({"key": "MISSING_KEY"}, {"_id": 0})
    mock_db.configs.update_one.assert_not_called()
    assert "MISSING_KEY" not in config_service._cache

@pytest.mark.asyncio
async def test_reload_cache(config_service, mock_db):
    # Setup state
    config_service._cache = {"OLD": "val"}
    config_service._cache_loaded = True

    # Setup mock data for load_cache
    mock_configs = [{"key": "NEW", "value": "val2"}]
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=mock_configs)
    mock_db.configs.find.return_value = mock_cursor

    # Execute
    await config_service.reload_cache()

    # Verify
    assert config_service._cache == {"NEW": "val2"}

@pytest.mark.asyncio
async def test_get_twilio_config(config_service):
    # Mock the get method directly
    config_service.get = AsyncMock()
    config_service.get.side_effect = ["sid_val", "token_val", "from_val"]

    # Execute
    result = await config_service.get_twilio_config()

    # Verify
    assert result == {
        "account_sid": "sid_val",
        "auth_token": "token_val",
        "whatsapp_from": "from_val"
    }
    assert config_service.get.call_count == 3
    config_service.get.assert_any_call("TWILIO_ACCOUNT_SID")
    config_service.get.assert_any_call("TWILIO_AUTH_TOKEN")
    config_service.get.assert_any_call("TWILIO_WHATSAPP_FROM")

@pytest.mark.asyncio
async def test_get_resend_config(config_service):
    # Mock the get method directly
    config_service.get = AsyncMock()
    config_service.get.side_effect = ["key_val", "email_val"]

    # Execute
    result = await config_service.get_resend_config()

    # Verify
    assert result == {
        "api_key": "key_val",
        "sender_email": "email_val"
    }
    assert config_service.get.call_count == 2
    config_service.get.assert_any_call("RESEND_API_KEY")
    config_service.get.assert_any_call("SENDER_EMAIL")
