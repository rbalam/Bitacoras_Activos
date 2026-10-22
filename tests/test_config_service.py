import pytest
import logging
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.config_service import ConfigService

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@pytest.fixture
def config_service(mock_db):
    return ConfigService(db=mock_db)

@pytest.mark.asyncio
async def test_load_cache_empty(config_service, mock_db, caplog):
    caplog.set_level(logging.INFO)
    # Setup mock to return empty list
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = []
    mock_db.configs.find.return_value = mock_cursor

    # Execute
    await config_service.load_cache()

    # Assert
    assert config_service._cache == {}
    assert config_service._cache_loaded is True
    assert "Loaded 0 configs into cache" in caplog.text
    mock_db.configs.find.assert_called_once_with({"active": True}, {"_id": 0})
    mock_cursor.to_list.assert_called_once_with(1000)

@pytest.mark.asyncio
async def test_load_cache_with_configs(config_service, mock_db, caplog):
    caplog.set_level(logging.INFO)
    # Setup mock to return some configs
    configs = [
        {"key": "TEST_KEY_1", "value": "test_value_1"},
        {"key": "TEST_KEY_2", "value": "test_value_2"}
    ]
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = configs
    mock_db.configs.find.return_value = mock_cursor

    # Execute
    await config_service.load_cache()

    # Assert
    assert config_service._cache == {"TEST_KEY_1": "test_value_1", "TEST_KEY_2": "test_value_2"}
    assert config_service._cache_loaded is True
    assert "Loaded 2 configs into cache" in caplog.text
    mock_db.configs.find.assert_called_once_with({"active": True}, {"_id": 0})
    mock_cursor.to_list.assert_called_once_with(1000)
