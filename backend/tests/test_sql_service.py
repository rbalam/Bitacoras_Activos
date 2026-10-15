import pytest
from unittest.mock import patch
import pymssql
from backend.services.sql_service import sql_service

@pytest.mark.asyncio
async def test_execute_query_error_handling(monkeypatch):
    # Ensure server is completely configured to bypass the early return
    monkeypatch.setitem(sql_service.servers[0], "host", "fake_host")
    monkeypatch.setitem(sql_service.servers[0], "database", "fake_db")
    monkeypatch.setitem(sql_service.servers[0], "user", "fake_user")

    with patch("backend.services.sql_service.pymssql.connect") as mock_connect, \
         patch("backend.services.sql_service.logger") as mock_logger:

        # Configure mock to raise an exception
        mock_connect.side_effect = Exception("DB Connection Error")

        # Execute query
        result = await sql_service.execute_query(0, "SELECT 1")

        # Assertions
        assert result is None
        mock_logger.error.assert_called_once()
        assert "Error al ejecutar query" in mock_logger.error.call_args[0][0]
        assert "DB Connection Error" in mock_logger.error.call_args[0][0]
