# src/tests/test_auto_selection.py

import sys
from pathlib import Path

# Ensure the project root is in the path so we can import src
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from src.driver_manager.auto_select_driver_manager import auto_driver_context, get_recommended_config


def test_auto_selection_flow():
    print("\n--- 🤖 Testing Auto-Selection Logic ---")

    # 1. Check what the 'Intelligence' layer chose
    best = get_recommended_config()
    print(f"📊 Recommended by Tuner: {best['engine']} | {best['browser']}")

    # 2. Use the context manager to launch the "Best" driver
    # It should automatically use Playwright-Firefox based on your last run
    print(f"🚀 Launching the best engine...")
    with auto_driver_context(headless=True) as driver:
        if best['engine'] == "playwright":
            p, b, c, page = driver
            page.goto("https://www.google.com")
            print(f"✅ Playwright Success: Viewed '{page.title()}'")
        else:
            driver.get("https://www.google.com")
            print(f"✅ Selenium Success: Viewed '{driver.title}'")


def test_manual_override_still_works():
    print("\n--- 🔄 Testing Manual Override ---")
    # Even though Playwright is 'Best', we force Selenium-Chrome here
    print("Forcing Selenium-Chrome despite recommendations...")
    with auto_driver_context(engine="selenium", browser="chrome", headless=True) as driver:
        driver.get("https://www.bing.com")
        print(f"✅ Override Success: Viewed '{driver.title}'")


if __name__ == "__main__":
    try:
        test_auto_selection_flow()
        test_manual_override_still_works()
        print("\n✨ All Auto-Selection tests passed!")
    except Exception as e:
        print(f"❌ Test Failed: {e}")