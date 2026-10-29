import pytest
from unittest.mock import patch, MagicMock
from backend.services.sql_service import sql_service

@pytest.mark.asyncio
@patch.dict('os.environ', {'SQL_SERVER_1_HOST': 'localhost', 'SQL_SERVER_1_DB': 'db', 'SQL_SERVER_1_USER': 'user', 'SQL_SERVER_1_PORT': '1433', 'SQL_SERVER_1_PASSWORD': 'pass'})
async def test_execute_query_parameterized():
    # Reinitalize service to pick up mocked env vars
    from backend.services.sql_service import SQLServerService
    local_sql_service = SQLServerService()

    with patch("backend.services.sql_service.pymssql.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [{"id": 1}]

        # Test without parameters
        results = await local_sql_service.execute_query(0, "SELECT * FROM Table")
        assert results == [{"id": 1}]
        mock_cursor.execute.assert_called_with("SELECT * FROM Table")

        # Test with parameters
        results = await local_sql_service.execute_query(0, "SELECT * FROM Table WHERE id = %s", (1,))
        assert results == [{"id": 1}]
        mock_cursor.execute.assert_called_with("SELECT * FROM Table WHERE id = %s", (1,))

@pytest.mark.asyncio
async def test_get_invoices_parameterized():
    with patch.object(sql_service, "execute_query", return_value=[{"id": 1}]) as mock_exec:
        results = await sql_service.get_invoices(0, "2023-01-01", "2023-12-31")
        assert results == [{"id": 1}]
        args, kwargs = mock_exec.call_args
        assert args[0] == 0
        assert "AND Fecha >= %s" in args[1]
        assert "AND Fecha <= %s" in args[1]
        assert args[2] == ("2023-01-01", "2023-12-31")

@pytest.mark.asyncio
async def test_search_by_invoice_number_parameterized():
    with patch.object(sql_service, "execute_query", return_value=[{"NumeroFactura": "INV-123"}]) as mock_exec:
        results = await sql_service.search_by_invoice_number("123")
        assert len(results) == 3 # 3 servers

        args, kwargs = mock_exec.call_args_list[0]
        assert "LIKE %s" in args[1]
        assert args[2] == ("%123%",)
