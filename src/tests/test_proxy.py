# from driver_manager.manager import driver_context
# from driver_manager.proxy_manager import GLOBAL_PROXY_MANAGER

# Add some fake proxies for testing
import time

from archive.driver_manager import driver_context
from src.driver_manager.proxy_manager import GLOBAL_PROXY_MANAGER

GLOBAL_PROXY_MANAGER.proxies = [
    "http://1.1.1.1:8080",
    "http://2.2.2.2:8080",
    "http://3.3.3.3:8080",
]

def test_proxy_rotation():
    print("Random proxy:", GLOBAL_PROXY_MANAGER.get_random())
    print("Next proxy:", GLOBAL_PROXY_MANAGER.get_next())
    print("Next proxy:", GLOBAL_PROXY_MANAGER.get_next())
    print("Next proxy:", GLOBAL_PROXY_MANAGER.get_next())

    # Test Playwright with proxy
    try:
        with driver_context(engine="playwright", use_proxy=True) as d:
            print("Playwright launched with proxy.")
    except Exception as e:
        print("Playwright proxy test FAILED:", e)

if __name__ == "__main__":
    print(f"==== Test Goal ==== \nconfirm that proxies rotate and are applied to Playwright/Selenium. ====")
    print(f"===== Expected behavior ====")
    print(f"see proxies rotating in order")
    print(f"Playwright prints: Using proxy for Playwright: http://X.X.X.X:8080")
    print(f"Browser launches (even if proxy is fake, it should still start)")
    print(f"\nTest starting.....\n")

    start_time = time.time()
    test_proxy_rotation()
    end_time = time.time()
    total_seconds = round(end_time - start_time, 2)
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60

    print("\n⏱ Test completed!")
    print(f"Total runtime: {minutes} minutes {seconds:.2f} seconds")
