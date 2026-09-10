import unittest
from unittest.mock import patch, MagicMock
import asyncio
from backend.services.sql_service import SQLServerService

class TestSQLServerService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.service = SQLServerService()
        # Ensure we have at least one validly configured server for the tests
        self.service.servers[0] = {
            "name": "TestServer",
            "host": "localhost",
            "port": "1433",
            "database": "testdb",
            "user": "testuser",
            "password": "testpassword",
        }

    @patch('pymssql.connect')
    async def test_get_invoices_parameterized(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        await self.service.get_invoices(0, "2023-01-01", "2023-12-31")

        mock_cursor.execute.assert_called_once()
        args, _ = mock_cursor.execute.call_args
        query, params = args

        self.assertIn("AND Fecha >= %s", query)
        self.assertIn("AND Fecha <= %s", query)
        self.assertEqual(params, ("2023-01-01", "2023-12-31"))
        self.assertNotIn("2023-01-01", query) # Ensure value is not in query string

    @patch('pymssql.connect')
    async def test_search_by_invoice_number_parameterized(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        await self.service.search_by_invoice_number("INV-12345")

        # Check the first call (to the first server)
        mock_cursor.execute.assert_called()
        args, _ = mock_cursor.execute.call_args_list[0]
        query, params = args

        self.assertIn("LIKE %s", query)
        self.assertEqual(params, ("%INV-12345%",))
        self.assertNotIn("INV-12345", query) # Ensure value is not in query string

if __name__ == '__main__':
    unittest.main()
