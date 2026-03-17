# src/driver_manager.py

import os
import shutil
import subprocess
from contextlib import contextmanager

# Selenium imports (secondary engine)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

# Playwright imports (primary engine)
from playwright.sync_api import sync_playwright


# ============================================================
# 1. Auto-install Playwright browsers if missing
# ============================================================

def ensure_playwright_browsers():
    """
    Ensures Playwright browsers are installed.
    Safe to call every time; it only installs if missing.
    """
    try:
        # Check if Playwright CLI exists
        if shutil.which("playwright") is None:
            print("Playwright not found in PATH.")
            return

        # Check if Chromium browser exists
        browser_dir = os.path.expanduser(
            "~/AppData/Local/ms-playwright/chromium"
        )
        if not os.path.exists(browser_dir):
            print("Playwright browsers missing. Installing...")
            subprocess.run(["playwright", "install"], check=True)

    except Exception as e:
        print("Failed to auto-install Playwright browsers:", e)


# ============================================================
# 2. Playwright primary engine
# ============================================================

def get_playwright_driver(headless=True):
    ensure_playwright_browsers()

    p = sync_playwright().start()
    browser = p.chromium.launch(headless=headless)

    # Return both so we can close them later
    return p, browser


# ============================================================
# 3. Selenium fallback (only when explicitly requested)
# ============================================================

def get_selenium_driver(browser="chrome", headless=True):
    browser = browser.lower()

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        return webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        return webdriver.Firefox(options=options)

    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")
        return webdriver.Edge(options=options)

    raise ValueError("Unsupported Selenium browser.")


# ============================================================
# 4. Unified driver getter
# ============================================================

def get_driver(
    browser="chrome",
    headless=True,
    engine="playwright",   # "playwright" or "selenium"
):
    """
    Main entry point.
    Playwright is primary engine.
    Selenium only used when explicitly requested.
    """
    engine = engine.lower()

    if engine == "playwright":
        return get_playwright_driver(headless=headless)

    if engine == "selenium":
        return get_selenium_driver(browser=browser, headless=headless)

    raise ValueError("Engine must be 'playwright' or 'selenium'.")


# ============================================================
# 5. Context manager for auto-cleanup
# ============================================================

@contextmanager
def driver_context(
    browser="chrome",
    headless=True,
    engine="playwright",
):
    driver = get_driver(browser, headless, engine)

    try:
        yield driver
    finally:
        # Playwright cleanup
        if isinstance(driver, tuple):
            p, browser_obj = driver
            browser_obj.close()
            p.stop()
        else:
            # Selenium cleanup
            driver.quit()


# ============================================================
# 6. Test routine
# ============================================================

def test_all():
    print("\n=== Testing Playwright (primary) ===")
    try:
        with driver_context(engine="playwright") as d:
            print("Playwright initialized successfully.")
    except Exception as e:
        print("Playwright FAILED:", e)

    print("\n=== Testing Selenium Chrome ===")
    try:
        with driver_context(engine="selenium", browser="chrome") as d:
            print("Selenium Chrome initialized successfully.")
    except Exception as e:
        print("Selenium Chrome FAILED:", e)

    print("\n=== Testing Selenium Firefox ===")
    try:
        with driver_context(engine="selenium", browser="firefox") as d:
            print("Selenium Firefox initialized successfully.")
    except Exception as e:
        print("Selenium Firefox FAILED:", e)

    print("\n=== Testing Selenium Edge ===")
    try:
        with driver_context(engine="selenium", browser="edge") as d:
            print("Selenium Edge initialized successfully.")
    except Exception as e:
        print("Selenium Edge FAILED:", e)


if __name__ == "__main__":
    test_all()
