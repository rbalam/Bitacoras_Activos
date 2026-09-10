import unittest
from unittest.mock import patch, MagicMock
import asyncio
import sys

# Mock pymssql before importing sql_service
sys.modules['pymssql'] = MagicMock()

from backend.services.sql_service import sql_service

class TestSQLService(unittest.IsolatedAsyncioTestCase):

    @patch('backend.services.sql_service.pymssql.connect')
    async def test_search_by_invoice_number_parameterized(self, mock_connect):
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [{"id": 1, "NumeroFactura": "INV-12345"}]

        # We need to temporarily set the environment variables to mock the hosts
        with patch.dict('os.environ', {
            'SQL_SERVER_1_HOST': 'host1', 'SQL_SERVER_1_DB': 'db1', 'SQL_SERVER_1_USER': 'u1',
            'SQL_SERVER_2_HOST': 'host2', 'SQL_SERVER_2_DB': 'db2', 'SQL_SERVER_2_USER': 'u2',
            'SQL_SERVER_3_HOST': 'host3', 'SQL_SERVER_3_DB': 'db3', 'SQL_SERVER_3_USER': 'u3'
        }):
            # Re-init servers to pickup the environ
            sql_service.__init__()

            await sql_service.search_by_invoice_number("12345")

            # search_by_invoice_number loops through all 3 servers.
            self.assertEqual(mock_cursor.execute.call_count, 3)

            # Verify the call for one of the iterations
            for call_args in mock_cursor.execute.call_args_list:
                args, kwargs = call_args
                query = args[0]
                params = args[1] if len(args) > 1 else None

                self.assertIn("NumeroFactura LIKE %s", query)
                self.assertEqual(params, ('%12345%',))

    @patch('backend.services.sql_service.pymssql.connect')
    async def test_get_invoices_parameterized(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [{"id": 1}]

        with patch.dict('os.environ', {
            'SQL_SERVER_1_HOST': 'host1', 'SQL_SERVER_1_DB': 'db1', 'SQL_SERVER_1_USER': 'u1'
        }):
            sql_service.__init__()

            await sql_service.get_invoices(0, start_date="2023-01-01", end_date="2023-12-31")

            self.assertEqual(mock_cursor.execute.call_count, 1)

            args, kwargs = mock_cursor.execute.call_args
            query = args[0]
            params = args[1]

            self.assertIn("Fecha >= %s", query)
            self.assertIn("Fecha <= %s", query)
            self.assertEqual(params, ("2023-01-01", "2023-12-31"))

if __name__ == '__main__':
    unittest.main()
