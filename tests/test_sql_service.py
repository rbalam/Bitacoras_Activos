import pytest
from unittest.mock import patch, MagicMock
from backend.services.sql_service import SQLServerService

@pytest.fixture
def sql_service():
    service = SQLServerService()
    # Replace default servers with predictable test configurations
    service.servers = [
        {
            "name": "Valid Server",
            "host": "localhost",
            "port": "1433",
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
        },
        {
            "name": "Incomplete Server",
            "host": "localhost",
            "port": "1433",
            "database": None,  # Missing database
            "user": "test_user",
            "password": "test_password",
        },
        {
            "name": "Missing Port Server",
            "host": "localhost",
            "port": None,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
        }
    ]
    return service

@pytest.mark.asyncio
async def test_execute_query_success(sql_service):
    query = "SELECT * FROM TestTable"
    expected_results = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

    with patch("backend.services.sql_service.pymssql.connect") as mock_connect:
        # Setup mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = expected_results

        # Execute
        results = await sql_service.execute_query(0, query)

        # Verify results
        assert results == expected_results

        # Verify interactions
        mock_connect.assert_called_once_with(
            server="localhost",
            port="1433",
            user="test_user",
            password="test_password",
            database="test_db",
            timeout=10
        )
        mock_conn.cursor.assert_called_once_with(as_dict=True)
        mock_cursor.execute.assert_called_once_with(query)
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

@pytest.mark.asyncio
async def test_execute_query_success_default_port(sql_service):
    query = "SELECT * FROM TestTable"

    with patch("backend.services.sql_service.pymssql.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Execute query on server with missing port (index 2)
        await sql_service.execute_query(2, query)

        # Verify it falls back to port "1433"
        mock_connect.assert_called_once_with(
            server="localhost",
            port="1433",
            user="test_user",
            password="test_password",
            database="test_db",
            timeout=10
        )

@pytest.mark.asyncio
async def test_execute_query_invalid_index(sql_service):
    # Requesting an index >= len(servers)
    results = await sql_service.execute_query(len(sql_service.servers), "SELECT 1")
    assert results is None

@pytest.mark.asyncio
async def test_execute_query_incomplete_config(sql_service):
    # Requesting server with missing database (index 1)
    results = await sql_service.execute_query(1, "SELECT 1")
    assert results is None

@pytest.mark.asyncio
async def test_execute_query_exception(sql_service):
    query = "SELECT 1"

    with patch("backend.services.sql_service.pymssql.connect") as mock_connect:
        mock_connect.side_effect = Exception("Database connection failed")

        # Execution should catch exception and return None
        results = await sql_service.execute_query(0, query)
        assert results is None
