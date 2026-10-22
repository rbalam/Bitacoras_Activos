import asyncio
import time

async def main():
    class MockDBCollection:
        def __init__(self, delay=0.1):
            self.delay = delay
        def find(self, query, proj):
            return self
        def sort(self, field, d):
            return self
        async def to_list(self, limit):
            await asyncio.sleep(self.delay)
            return []

    class MockDBInstance:
        def __init__(self):
            self.maintenances = MockDBCollection(0.2)
            self.quotes = MockDBCollection(0.1)

    class MockAnalytics:
        async def calculate_asset_total_cost(self, asset_id):
            await asyncio.sleep(0.3)
            return {"total": 100}
        async def should_replace_asset(self, asset_id):
            await asyncio.sleep(0.15)
            return {"replace": False}

    db = MockDBInstance()
    analytics = MockAnalytics()
    asset_id = "test_asset"

    # Simulate sequential (current)
    start_seq = time.time()
    maintenances = await db.maintenances.find({"asset_id": asset_id}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    costs = await analytics.calculate_asset_total_cost(asset_id)
    replacement = await analytics.should_replace_asset(asset_id)
    quotes = await db.quotes.find({"asset_id": asset_id}, {"_id": 0}).to_list(100)
    end_seq = time.time()
    print(f"Sequential time: {end_seq - start_seq:.4f} seconds")

    # Simulate parallel (proposed)
    start_par = time.time()
    maintenances_task = db.maintenances.find({"asset_id": asset_id}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    costs_task = analytics.calculate_asset_total_cost(asset_id)
    replacement_task = analytics.should_replace_asset(asset_id)
    quotes_task = db.quotes.find({"asset_id": asset_id}, {"_id": 0}).to_list(100)

    maintenances, costs, replacement, quotes = await asyncio.gather(
        maintenances_task, costs_task, replacement_task, quotes_task
    )
    end_par = time.time()
    print(f"Parallel time: {end_par - start_par:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
