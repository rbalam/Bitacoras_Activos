import pytest
from unittest.mock import patch, MagicMock
from backend.services.sql_service import SQLServerService
import asyncio

@pytest.fixture
def sql_service():
    service = SQLServerService()
    # Mock environment variables to ensure all servers are configured
    service.servers = [
        {
            "name": "Cienfuegos",
            "host": "test_host",
            "port": "1433",
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
        }
    ]
    return service

@pytest.mark.asyncio
async def test_execute_query_exception(sql_service):
    with patch("backend.services.sql_service.pymssql.connect") as mock_connect:
        mock_connect.side_effect = Exception("Test connection error")

        with patch("backend.services.sql_service.logger") as mock_logger:
            result = await sql_service.execute_query(0, "SELECT 1")

            assert result is None
            mock_logger.error.assert_called_once()
            assert "Error al ejecutar query en Cienfuegos: Test connection error" in mock_logger.error.call_args[0][0]
