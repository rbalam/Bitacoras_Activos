import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock
from mongomock_motor import AsyncMongoMockClient

# We need to set env vars before importing init_configs because it uses os.environ inside the function
# but they need to exist. Wait, load_dotenv might override them, but it's loaded at module level.
# Actually load_dotenv only sets if they are not already set, or sets them.
os.environ['MONGO_URL'] = "mongodb://localhost:27017"
os.environ['DB_NAME'] = "testdb"

from backend.init_config import init_configs

@pytest.fixture
def mock_client():
    # Return a mocked AsyncIOMotorClient that connects to an in-memory db
    return AsyncMongoMockClient()

@pytest.mark.asyncio
async def test_init_configs_empty_db(mocker, mock_client, capsys):
    # Mock AsyncIOMotorClient to return our mongomock client
    mocker.patch('backend.init_config.AsyncIOMotorClient', return_value=mock_client)

    # Ensure db is empty
    db = mock_client[os.environ['DB_NAME']]
    await db.configs.delete_many({})

    await init_configs()

    # Verify configs were inserted
    configs = await db.configs.find().to_list(None)
    assert len(configs) == 5

    categories = [c['category'] for c in configs]
    assert categories.count('twilio') == 3
    assert categories.count('email') == 2

    # Check stdout
    captured = capsys.readouterr()
    assert "5 configuraciones inicializadas correctamente" in captured.out

@pytest.mark.asyncio
async def test_init_configs_existing_decline_replace(mocker, mock_client, capsys):
    mocker.patch('backend.init_config.AsyncIOMotorClient', return_value=mock_client)

    # Pre-populate db
    db = mock_client[os.environ['DB_NAME']]
    await db.configs.delete_many({})
    await db.configs.insert_one({"key": "TEST", "value": "123"})

    # Mock input to return 'n' (decline)
    mocker.patch('builtins.input', return_value='n')

    await init_configs()

    # Verify configs were NOT replaced (still 1)
    configs = await db.configs.find().to_list(None)
    assert len(configs) == 1
    assert configs[0]["key"] == "TEST"

    captured = capsys.readouterr()
    assert "Ya existen 1 configuraciones" in captured.out
    assert "Operación cancelada" in captured.out

@pytest.mark.asyncio
async def test_init_configs_existing_accept_replace(mocker, mock_client, capsys):
    mocker.patch('backend.init_config.AsyncIOMotorClient', return_value=mock_client)

    # Pre-populate db
    db = mock_client[os.environ['DB_NAME']]
    await db.configs.delete_many({})
    await db.configs.insert_one({"key": "TEST", "value": "123"})

    # Mock input to return 's' (accept)
    mocker.patch('builtins.input', return_value='s')

    await init_configs()

    # Verify configs were replaced (now 5, and TEST is gone)
    configs = await db.configs.find().to_list(None)
    assert len(configs) == 5
    keys = [c['key'] for c in configs]
    assert "TEST" not in keys

    captured = capsys.readouterr()
    assert "Ya existen 1 configuraciones" in captured.out
    assert "Eliminadas 1 configuraciones anteriores" in captured.out
    assert "5 configuraciones inicializadas correctamente" in captured.out
