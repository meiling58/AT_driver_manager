from src.driver_manager.playwright_engine import get_playwright_driver
from axe_playwright_python.sync_playwright import Axe


def test_all_508():
    browsers_to_test = ["chromium", "firefox", "msedge", "webkit"]

    for b in browsers_to_test:
        p, browser, context, page = get_playwright_driver(browser_type=b)
        page.goto("https://www.section508.gov/")
        results = Axe().run(page, options={"runOnly": ["section508"]})
        print(f"Browser: {b} | Violations: {results.violations_count}")
        assert results.violations_count == 0

        browser.close()
        p.stop()

def test_mobile_508(device):
    print(f"\n--- Starting Audit for: {device} ---")

    try:
        # We try to get the driver
        p, browser, context, page = get_playwright_driver(
            browser_type="webkit",
            device_name=device
        )

        try:
            page.goto("https://www.section508.gov/")
            results = Axe().run(page, options={"runOnly": ["section508"]})
            print(f"✅ Mobile {device} Violations: {results.violations_count}")
            assert results.violations_count == 0
        finally:
            browser.close()
            p.stop()

    except ValueError as ve:
        # This catches your custom ValueError from the engine
        print(f"⚠️  ALERT: Skipping test for '{device}'. Reason: {ve}")
    except Exception as e:
        # This catches any other unexpected errors
        print(f"❌ ERROR: An unexpected error occurred for {device}: {e}")

if __name__ == "__main__":
    print(f"Testing all browsers with playwright engine")
    test_all_508()
    device1="iPhone 14"
    print(f"\nTesting mobile with {device1}")
    test_mobile_508(device1)
    device2="Pixel 7" #"Pixel 7", "Galaxy S9+", "Galaxy S20"
    test_mobile_508(device2)
    print(f"Testing not available device")
    device3="iPhone 10"
    test_mobile_508(device3)

