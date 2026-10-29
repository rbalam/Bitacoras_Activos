import asyncio
import time
from unittest.mock import AsyncMock
from backend.services.sql_service import SQLServerService

async def main():
    service = SQLServerService()
    # Mock execute_query to simulate a 0.5s network delay
    async def mock_execute(index, query):
        await asyncio.sleep(0.5)
        return [{"id": index, "invoice": "INV-123"}]
    service.execute_query = AsyncMock(side_effect=mock_execute)

    start_time = time.time()
    results = await service.search_by_invoice_number("123")
    end_time = time.time()

    duration = end_time - start_time
    print(f"Time taken: {duration:.4f} seconds")
    print(f"Results count: {len(results)}")

if __name__ == "__main__":
    asyncio.run(main())
