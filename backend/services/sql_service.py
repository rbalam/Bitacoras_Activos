import pymssql
import os
import logging
from typing import List, Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)

class SQLServerService:
    def __init__(self):
        self.servers = [
            {
                "name": "Cienfuegos",
                "host": os.environ.get("SQL_SERVER_1_HOST"),
                "port": os.environ.get("SQL_SERVER_1_PORT"),
                "database": os.environ.get("SQL_SERVER_1_DB"),
                "user": os.environ.get("SQL_SERVER_1_USER"),
                "password": os.environ.get("SQL_SERVER_1_PASSWORD"),
            },
            {
                "name": "Estelar",
                "host": os.environ.get("SQL_SERVER_2_HOST"),
                "port": os.environ.get("SQL_SERVER_2_PORT"),
                "database": os.environ.get("SQL_SERVER_2_DB"),
                "user": os.environ.get("SQL_SERVER_2_USER"),
                "password": os.environ.get("SQL_SERVER_2_PASSWORD"),
            },
            {
                "name": "Central",
                "host": os.environ.get("SQL_SERVER_3_HOST"),
                "port": os.environ.get("SQL_SERVER_3_PORT"),
                "database": os.environ.get("SQL_SERVER_3_DB"),
                "user": os.environ.get("SQL_SERVER_3_USER"),
                "password": os.environ.get("SQL_SERVER_3_PASSWORD"),
            },
        ]
    
    async def execute_query(self, server_index: int, query: str) -> Optional[List[Dict[str, Any]]]:
        """Ejecutar query en un servidor SQL específico"""
        if server_index >= len(self.servers):
            logger.error(f"Índice de servidor inválido: {server_index}")
            return None
        
        server = self.servers[server_index]
        if not all([server["host"], server["database"], server["user"]]):
            logger.warning(f"Servidor {server['name']} no configurado completamente")
            return None
        
        try:
            def _execute():
                conn = pymssql.connect(
                    server=server["host"],
                    port=server["port"] or "1433",
                    user=server["user"],
                    password=server["password"],
                    database=server["database"],
                    timeout=10
                )
                cursor = conn.cursor(as_dict=True)
                cursor.execute(query)
                results = cursor.fetchall()
                conn.close()
                return results
            
            results = await asyncio.to_thread(_execute)
            logger.info(f"Query ejecutado en {server['name']}: {len(results)} registros")
            return results
        except Exception as e:
            logger.error(f"Error al ejecutar query en {server['name']}: {str(e)}")
            return None
    
    async def get_invoices(self, server_index: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtener facturas de un servidor SQL"""
        # Esta es una query de ejemplo - debe ajustarse según la estructura real de las tablas
        query = """
        SELECT TOP 100
            *
        FROM Facturas
        WHERE 1=1
        """
        
        if start_date:
            query += f" AND Fecha >= '{start_date}'"
        if end_date:
            query += f" AND Fecha <= '{end_date}'"
        
        query += " ORDER BY Fecha DESC"
        
        results = await self.execute_query(server_index, query)
        return results or []
    
    async def search_by_invoice_number(self, invoice_number: str) -> List[Dict[str, Any]]:
        """Buscar una factura específica en todos los servidores"""
        all_results = []
        
        for i in range(len(self.servers)):
            query = f"""
            SELECT TOP 10 *
            FROM Facturas
            WHERE NumeroFactura LIKE '%{invoice_number}%'
            """
            
            results = await self.execute_query(i, query)
            if results:
                for result in results:
                    result["source_server"] = self.servers[i]["name"]
                all_results.extend(results)
        
        return all_results

sql_service = SQLServerService()
