# from driver_manager.fallback import run_with_fallback
from src.driver_manager.fallback import run_with_fallback

URL1 = "https://example.com"
URL2 = "https://bot.sannysoft.com"
URL3 = "https://this-domain-does-not-exist-12345.com"


def test_fallback(url):
    print("=== Testing Smart Fallback Logic ===")
    title = run_with_fallback(url)
    print(f"\nFinal Result: {title}")


if __name__ == "__main__":
    test_fallback(URL3)

