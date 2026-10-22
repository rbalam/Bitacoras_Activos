import pytest
from unittest.mock import MagicMock
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.services.analytics_service import AnalyticsService

def test_analytics_service_init():
    mock_db = MagicMock(spec=AsyncIOMotorDatabase)
    service = AnalyticsService(db=mock_db)
    assert service.db == mock_db
