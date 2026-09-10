import pytest
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Add backend to path so we can import init_config
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from init_config import get_default_configs, check_and_clear_existing, print_configs

def test_get_default_configs():
    configs = get_default_configs()
    assert isinstance(configs, list)
    assert len(configs) == 5

    # Check that expected keys are present in the first item
    assert "id" in configs[0]
    assert "key" in configs[0]
    assert "value" in configs[0]
    assert "category" in configs[0]

@pytest.mark.asyncio
async def test_check_and_clear_existing_empty(mocker):
    # Setup mock db
    mock_db = MagicMock()
    mock_db.configs.count_documents = AsyncMock(return_value=0)

    result = await check_and_clear_existing(mock_db)

    assert result is True
    mock_db.configs.count_documents.assert_called_once_with({})
    # Input should not have been called
    mock_db.configs.delete_many.assert_not_called()

@pytest.mark.asyncio
async def test_check_and_clear_existing_cancel(mocker):
    # Setup mock db
    mock_db = MagicMock()
    mock_db.configs.count_documents = AsyncMock(return_value=5)

    # Mock built-in input to return 'n' (cancel)
    mocker.patch('builtins.input', return_value='n')

    result = await check_and_clear_existing(mock_db)

    assert result is False
    mock_db.configs.count_documents.assert_called_once_with({})
    mock_db.configs.delete_many.assert_not_called()

@pytest.mark.asyncio
async def test_check_and_clear_existing_confirm(mocker):
    # Setup mock db
    mock_db = MagicMock()
    mock_db.configs.count_documents = AsyncMock(return_value=5)

    mock_delete_result = MagicMock()
    mock_delete_result.deleted_count = 5
    mock_db.configs.delete_many = AsyncMock(return_value=mock_delete_result)

    # Mock built-in input to return 's' (confirm)
    mocker.patch('builtins.input', return_value='s')

    result = await check_and_clear_existing(mock_db)

    assert result is True
    mock_db.configs.count_documents.assert_called_once_with({})
    mock_db.configs.delete_many.assert_called_once_with({})

def test_print_configs(capsys):
    # A tiny fake config list
    configs = [
        {
            "key": "TEST_KEY",
            "value": "supersecretpassword",
            "active": True,
            "is_sensitive": True
        },
        {
            "key": "PUBLIC_KEY",
            "value": "public_data",
            "active": False,
            "is_sensitive": False
        }
    ]

    print_configs(configs)

    captured = capsys.readouterr()
    # verify expected output
    assert "Configuraciones creadas:" in captured.out
    assert "TEST_KEY" in captured.out
    assert "supersecre..." in captured.out
    assert "✓ Activo" in captured.out

    assert "PUBLIC_KEY" in captured.out
    assert "public_data" in captured.out
    assert "✗ Inactivo" in captured.out
