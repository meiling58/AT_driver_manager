import time
import asyncio
# from driver_manager.pool_concurrency import run_with_pool

# Use 50 URLs for stable, meaningful benchmarking
from src.driver_manager.pool_concurrency import run_with_pool

URLS = ["https://example.com"] * 50

# Pool sizes to test
POOL_SIZES = [3, 5, 8, 10]


async def benchmark(pool_size: int) -> float:
    """Run the pool concurrency test for a given pool size and return elapsed time."""
    start = time.time()
    await run_with_pool(URLS, pool_size=pool_size)
    end = time.time()
    return round(end - start, 2)


def autotune():
    print("=== Auto‑tuning Browser Pool Size ===")
    print(f"Total URLs: {len(URLS)}")
    print(f"Testing pool sizes: {POOL_SIZES}\n")

    results = {}

    # Run benchmark for each pool size
    for size in POOL_SIZES:
        print(f"Testing pool_size = {size} ...")
        elapsed = asyncio.run(benchmark(size))
        results[size] = elapsed
        print(f"  → Time: {elapsed} seconds\n")

    # Print summary table
    print("\n=== Summary ===")
    print(f"{'Pool Size':<12} {'Time (s)':<10}")
    print("-" * 24)
    for size, t in results.items():
        print(f"{size:<12} {t:<10}")

    # Determine the best pool size
    best_size = min(results, key=results.get)
    best_time = results[best_size]

    print("\n🏆 Best Configuration")
    print(f"pool_size = {best_size}  (time: {best_time}s)")
    print("\nAuto‑tuning complete.")


if __name__ == "__main__":
    autotune()
