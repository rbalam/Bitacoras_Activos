import pytest
from mongomock_motor import AsyncMongoMockClient
from httpx import AsyncClient, ASGITransport
import os
import sys

# Add backend to PYTHONPATH for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from server import app
import server

@pytest.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client["test_db"]

    # Patch the global db object in server.py
    original_db = server.db
    original_client = server.client

    server.client = client
    server.db = db

    yield db

    # Restore original db
    server.client = original_client
    server.db = original_db

@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
