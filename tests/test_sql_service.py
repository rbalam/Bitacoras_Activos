import pytest
import os
from unittest.mock import patch, MagicMock
from backend.services.sql_service import SQLServerService

@pytest.fixture
def sql_service():
    # Setup dummy environment variables for tests
    with patch.dict(os.environ, {
        "SQL_SERVER_1_HOST": "host1",
        "SQL_SERVER_1_PORT": "1433",
        "SQL_SERVER_1_DB": "db1",
        "SQL_SERVER_1_USER": "user1",
        "SQL_SERVER_1_PASSWORD": "pass1",
        "SQL_SERVER_2_HOST": "host2",
        "SQL_SERVER_2_PORT": "1433",
        "SQL_SERVER_2_DB": "db2",
        "SQL_SERVER_2_USER": "user2",
        "SQL_SERVER_2_PASSWORD": "pass2",
        "SQL_SERVER_3_HOST": "host3",
        "SQL_SERVER_3_PORT": "1433",
        "SQL_SERVER_3_DB": "db3",
        "SQL_SERVER_3_USER": "user3",
        "SQL_SERVER_3_PASSWORD": "pass3",
    }):
        service = SQLServerService()
        yield service

@pytest.mark.asyncio
async def test_execute_query_error(sql_service):
    """Test that execute_query correctly handles exceptions raised during database operations."""

    # We will mock pymssql.connect inside the backend.services.sql_service module scope
    with patch('backend.services.sql_service.pymssql.connect') as mock_connect:
        mock_connect.side_effect = Exception("Database connection failed")

        # Call with server_index=0
        result = await sql_service.execute_query(0, "SELECT * FROM Table")

        # Verify that it caught the exception and returned None
        assert result is None
        mock_connect.assert_called_once()

@pytest.mark.asyncio
async def test_execute_query_success(sql_service):
    """Test that execute_query returns results on successful execution."""

    with patch('backend.services.sql_service.pymssql.connect') as mock_connect:
        # Create a mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Set up the mock hierarchy
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Set up mock results
        mock_results = [{"id": 1, "name": "Test"}]
        mock_cursor.fetchall.return_value = mock_results

        # Call with server_index=0
        result = await sql_service.execute_query(0, "SELECT * FROM Table")

        # Verify the results and that methods were called correctly
        assert result == mock_results
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once_with(as_dict=True)
        mock_cursor.execute.assert_called_once_with("SELECT * FROM Table")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()
