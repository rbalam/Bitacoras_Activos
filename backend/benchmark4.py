import asyncio
import time
import os
import shutil
import tempfile
import aiofiles

def setup_dummy_file(size_mb):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(os.urandom(size_mb * 1024 * 1024))
        return f.name

async def blocking_io_handler(file_path, source_path):
    with open(source_path, "rb") as src:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(src, buffer)
    # Give some time to the event loop (like FastAPI would)
    await asyncio.sleep(0.001)

async def aiofiles_io_handler(file_path, source_path):
    async with aiofiles.open(source_path, "rb") as src:
        async with aiofiles.open(file_path, "wb") as buffer:
            while True:
                chunk = await src.read(1024 * 1024)
                if not chunk:
                    break
                await buffer.write(chunk)

async def to_thread_io_handler(file_path, source_path):
    def save_file(path, src_path):
        with open(src_path, "rb") as src:
            with open(path, "wb") as buffer:
                shutil.copyfileobj(src, buffer)
    await asyncio.to_thread(save_file, file_path, source_path)

async def dummy_request():
    """Simulates a fast healthcheck/ping endpoint to measure event loop blocking."""
    start = time.perf_counter()
    await asyncio.sleep(0) # Yield back immediately, representing a pure CPU check or instantly available resource
    return time.perf_counter() - start

async def run_concurrent_test(mode, source_path, num_uploads=30, num_pings=1000):
    dest_files = []

    async def upload_task(i):
        dest_path = f"test_dest_{mode}_{i}.dat"
        dest_files.append(dest_path)
        if mode == "blocking":
            await blocking_io_handler(dest_path, source_path)
        elif mode == "aiofiles":
            await aiofiles_io_handler(dest_path, source_path)
        elif mode == "to_thread":
            await to_thread_io_handler(dest_path, source_path)

    async def ping_loop():
        latencies = []
        for _ in range(num_pings):
            latency = await dummy_request()
            latencies.append(latency)
            await asyncio.sleep(0.001) # constant rate of requests
        return latencies

    start_time = time.perf_counter()

    # Run uploads and pings concurrently
    upload_tasks = [asyncio.create_task(upload_task(i)) for i in range(num_uploads)]
    ping_task = asyncio.create_task(ping_loop())

    await asyncio.gather(*upload_tasks)
    latencies = await ping_task

    total_time = time.perf_counter() - start_time

    for dest_path in dest_files:
        if os.path.exists(dest_path):
            os.remove(dest_path)

    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)

    return total_time, avg_latency, max_latency

async def run_benchmark():
    dummy_path = setup_dummy_file(50) # 50MB file

    try:
        print("Running benchmark simulating 30 concurrent 50MB uploads + 1000 concurrent light requests...")
        print("-" * 60)

        # Run blocking
        total_b, avg_b, max_b = await run_concurrent_test("blocking", dummy_path)
        print(f"Blocking (Current):")
        print(f"  Total Time: {total_b:.4f}s")
        print(f"  Avg Ping Latency: {avg_b:.6f}s")
        print(f"  Max Ping Latency: {max_b:.6f}s")
        print("-" * 60)

        # Run aiofiles
        total_a, avg_a, max_a = await run_concurrent_test("aiofiles", dummy_path)
        print(f"Aiofiles:")
        print(f"  Total Time: {total_a:.4f}s")
        print(f"  Avg Ping Latency: {avg_a:.6f}s")
        print(f"  Max Ping Latency: {max_a:.6f}s")
        print("-" * 60)

        # Run to_thread
        total_t, avg_t, max_t = await run_concurrent_test("to_thread", dummy_path)
        print(f"To_thread:")
        print(f"  Total Time: {total_t:.4f}s")
        print(f"  Avg Ping Latency: {avg_t:.6f}s")
        print(f"  Max Ping Latency: {max_t:.6f}s")

    finally:
        os.remove(dummy_path)

asyncio.run(run_benchmark())
