import time
import asyncio

# from driver_manager.concurrency import run_concurrent
# from driver_manager.pool_concurrency import run_with_pool
from src.driver_manager.concurrency import run_concurrent
from src.driver_manager.pool_concurrency import run_with_pool

URLS = ["https://example.com"] * 50


def test_no_pool():
    print("=== No pool (fresh browser per URL) ===")
    start = time.time()
    results = asyncio.run(run_concurrent(URLS))
    end = time.time()
    print(f"Total time: {round(end - start, 2)}s")
    return results


def test_with_pool():
    print("\n=== With browser pool (reused browsers) ===")
    start = time.time()
    results = asyncio.run(run_with_pool(URLS, pool_size=3))
    end = time.time()
    print(f"Total time: {round(end - start, 2)}s")
    return results


if __name__ == "__main__":
    no_pool_results = test_no_pool()
    pool_results = test_with_pool()
