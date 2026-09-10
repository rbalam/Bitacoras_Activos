import asyncio
import time

class MockCollection:
    async def find_one(self, *args, **kwargs):
        await asyncio.sleep(0.1) # Simulate DB latency
        return {"id": "mocked_id", "name": "Mocked Asset"}

class MockDB:
    def __init__(self):
        self.assets = MockCollection()

async def sequential_fetch(db, old_asset_id, new_asset_id):
    start_time = time.time()
    old_asset = await db.assets.find_one({"id": old_asset_id}, {"_id": 0})
    new_asset = await db.assets.find_one({"id": new_asset_id}, {"_id": 0})
    end_time = time.time()
    return end_time - start_time

async def concurrent_fetch(db, old_asset_id, new_asset_id):
    start_time = time.time()
    old_asset, new_asset = await asyncio.gather(
        db.assets.find_one({"id": old_asset_id}, {"_id": 0}),
        db.assets.find_one({"id": new_asset_id}, {"_id": 0})
    )
    end_time = time.time()
    return end_time - start_time

async def main():
    db = MockDB()
    seq_time = await sequential_fetch(db, "1", "2")
    print(f"Sequential fetch time: {seq_time:.4f} seconds")

    conc_time = await concurrent_fetch(db, "1", "2")
    print(f"Concurrent fetch time: {conc_time:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
