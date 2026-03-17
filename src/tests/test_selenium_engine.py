# tests/test_selenium_engine.py

from src.driver_manager.selenium_engine import get_selenium_driver
import time


def test_all_selenium_browsers():
    print("\n--- Testing Desktop Browsers (Selenium) ---")
    browsers = ["chrome", "msedge", "firefox"]

    for b in browsers:
        print(f"Testing: {b}")
        driver = None
        try:
            driver = get_selenium_driver(browser_type=b, headless=True)
            driver.get("https://www.section508.gov/")
            print(f"✅ {b} Success: {driver.title[:30]}...")
        except Exception as e:
            print(f"❌ {b} Failed: {e}")
        finally:
            if driver:
                driver.quit()


def test_selenium_mobile(device):
    print(f"\n--- Testing Mobile Emulation: {device} ---")
    driver = None
    try:
        # Note: device_name only works for 'chrome' and 'msedge'
        driver = get_selenium_driver(browser_type="chrome", device_name=device, headless=True)
        driver.get("https://www.section508.gov/")

        # Simple check to see if the viewport changed (Mobile headers usually trigger different UI)
        print(f"✅ Mobile {device} Success: {driver.title[:30]}...")

    except ValueError as ve:
        print(f"⚠️ ALERT: Skipping '{device}'. Reason: {ve}")
    except Exception as e:
        print(f"❌ ERROR: Could not emulate {device}: {e}")
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    # 1. Test standard desktop browsers
    test_all_selenium_browsers()

    # 2. Test valid mobile devices
    # Common Selenium device names: "iPhone X", "Pixel 5", "Nexus 5"
    test_selenium_mobile("iPhone X")
    test_selenium_mobile("Pixel 5")

    # 3. Test invalid device (To verify your error handling)
    test_selenium_mobile("iPhone 10")