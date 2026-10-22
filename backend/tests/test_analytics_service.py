import pytest
from unittest.mock import AsyncMock, MagicMock
from services.analytics_service import AnalyticsService

@pytest.mark.asyncio
async def test_calculate_asset_total_cost():
    db_mock = MagicMock()
    cursor_mock = MagicMock()
    cursor_mock.to_list = AsyncMock(return_value=[
        {"tipo": "preventivo", "costo": 100.0},
        {"tipo": "correctivo", "costo": 200.0},
        {"tipo": "emergencia", "costo": 50.0},
        {"tipo": "otro", "costo": 10.0}
    ])
    db_mock.maintenances.find.return_value = cursor_mock

    service = AnalyticsService(db_mock)
    result = await service.calculate_asset_total_cost("asset-123")

    assert result["total_mantenimiento_preventivo"] == 100.0
    assert result["total_reparaciones"] == 250.0
    assert result["total_general"] == 350.0

    db_mock.maintenances.find.assert_called_once_with(
        {"asset_id": "asset-123", "estado": "completado"},
        {"_id": 0, "tipo": 1, "costo": 1}
    )
    cursor_mock.to_list.assert_called_once_with(1000)

@pytest.mark.asyncio
async def test_calculate_asset_total_cost_empty():
    db_mock = MagicMock()
    cursor_mock = MagicMock()
    cursor_mock.to_list = AsyncMock(return_value=[])
    db_mock.maintenances.find.return_value = cursor_mock

    service = AnalyticsService(db_mock)
    result = await service.calculate_asset_total_cost("asset-123")

    assert result["total_mantenimiento_preventivo"] == 0
    assert result["total_reparaciones"] == 0
    assert result["total_general"] == 0
