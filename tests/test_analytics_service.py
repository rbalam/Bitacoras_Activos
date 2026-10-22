import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from backend.services.analytics_service import AnalyticsService
from motor.motor_asyncio import AsyncIOMotorDatabase

@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.assets.count_documents = AsyncMock()
    db.maintenances.count_documents = AsyncMock()
    db.authorizations.count_documents = AsyncMock()
    db.alerts.count_documents = AsyncMock()
    return db

@pytest.mark.asyncio
async def test_get_dashboard_stats(mock_db):
    # Configurar los retornos esperados de los mocks de la base de datos
    mock_db.assets.count_documents.side_effect = [
        100,  # total_assets
        70,   # assets_operativos
        20,   # assets_mantenimiento
        10    # assets_criticos
    ]

    mock_db.maintenances.count_documents.return_value = 5  # mantenimientos_pendientes
    mock_db.authorizations.count_documents.return_value = 3  # autorizaciones_pendientes
    mock_db.alerts.count_documents.return_value = 2  # alertas_activas

    service = AnalyticsService(db=mock_db)

    # Mockear el método get_monthly_costs
    with patch.object(service, 'get_monthly_costs', new_callable=AsyncMock) as mock_get_monthly_costs:
        mock_get_monthly_costs.return_value = 15000.50

        # Ejecutar la función a probar
        stats = await service.get_dashboard_stats()

        # Verificar que se llamaron a los mocks con los argumentos correctos
        assert mock_db.assets.count_documents.call_count == 4
        mock_db.assets.count_documents.assert_any_call({})
        mock_db.assets.count_documents.assert_any_call({"estado": "operativo"})
        mock_db.assets.count_documents.assert_any_call({"estado": "mantenimiento"})
        mock_db.assets.count_documents.assert_any_call({"estado": "critico"})

        mock_db.maintenances.count_documents.assert_called_once_with(
            {"estado": {"$in": ["programado", "en_proceso"]}}
        )
        mock_db.authorizations.count_documents.assert_called_once_with({"estado": "pendiente"})
        mock_db.alerts.count_documents.assert_called_once_with({"leida": False})

        now = datetime.now(timezone.utc)
        mock_get_monthly_costs.assert_called_once_with(now.year, now.month)

        # Verificar los resultados devueltos
        assert stats == {
            "total_assets": 100,
            "assets_operativos": 70,
            "assets_mantenimiento": 20,
            "assets_criticos": 10,
            "mantenimientos_pendientes": 5,
            "autorizaciones_pendientes": 3,
            "alertas_activas": 2,
            "gasto_mes_actual": 15000.50
        }
