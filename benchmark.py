import asyncio
import time
from backend.services.sql_service import sql_service

async def main():
    # Mocking execute_query to simulate slow DB calls
    async def mock_execute_query(server_index, query):
        await asyncio.sleep(0.5)
        return [{"id": 1, "NumeroFactura": "12345"}]

    sql_service.execute_query = mock_execute_query

    start_time = time.time()
    results = await sql_service.search_by_invoice_number("12345")
    end_time = time.time()

    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(main())
