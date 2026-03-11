# driver_manager/driver_manager.py

from contextlib import contextmanager
from src.driver_manager.playwright_engine import get_playwright_driver
from src.driver_manager.selenium_engine import get_selenium_driver

def get_driver(
    browser="chrome",
    headless=True,
    engine="playwright",
    use_stealth=True,
    use_proxy=False,
    allow_fallback=True,
):
    engine = engine.lower()

    if engine == "playwright":
        try:
            return get_playwright_driver(
                headless=headless,
                use_stealth=use_stealth,
                use_proxy=use_proxy,
            )
        except Exception as e:
            print("Playwright failed:", e)
            if allow_fallback:
                print("Falling back to Selenium...")
                return get_selenium_driver(browser, headless, use_proxy)
            raise

    if engine == "selenium":
        return get_selenium_driver(browser, headless, use_proxy)

    raise ValueError("Engine must be 'playwright' or 'selenium'.")

@contextmanager
def driver_context(**kwargs):
    driver = get_driver(**kwargs)
    try:
        yield driver
    finally:
        if isinstance(driver, tuple):
            p, browser, context, page = driver
            page.close()
            context.close()
            browser.close()
            p.stop()
        else:
            driver.quit()
