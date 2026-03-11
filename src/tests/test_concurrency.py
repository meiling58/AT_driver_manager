import time
import asyncio
# from driver_manager.concurrency import run_concurrent
from src.driver_manager.concurrency import run_concurrent

TEST_URLS_1 = [
    "https://example.com",
    "https://www.python.org",
    "https://www.wikipedia.org",
    "https://github.com",
    "https://news.ycombinator.com",
]

TEST_URLS_2 = ["https://example.com"] * 20

def test_concurrency(urls):
    print("=== Testing Concurrency ===")
    print(f"Total URLs: {len(urls)}")

    start = time.time()
    results = asyncio.run(run_concurrent(urls))
    end = time.time()

    for url, title in results:
        print(f"{url} → {title}")

    print("\n⏱ Total time:", round(end - start, 2), "seconds")


if __name__ == "__main__":
    test_concurrency(TEST_URLS_1)

    test_concurrency(TEST_URLS_2)
