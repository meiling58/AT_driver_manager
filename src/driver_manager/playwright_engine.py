# driver_manager/playwright_engine.py

from playwright.sync_api import sync_playwright
from src.driver_manager.auto_install import ensure_playwright_browsers
from src.driver_manager.stealth import apply_stealth
from src.driver_manager.proxy_manager import GLOBAL_PROXY_MANAGER
from src.driver_manager.retry import retry

@retry(times=2)
def get_playwright_driver(headless=True, use_stealth=True, use_proxy=False):
    ensure_playwright_browsers()

    proxy = GLOBAL_PROXY_MANAGER.get_random() if use_proxy else None

    p = sync_playwright().start()

    browser = p.chromium.launch(
        headless=headless,
        proxy={"server": proxy} if proxy else None,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
    )

    context = browser.new_context()
    page = context.new_page()

    if use_stealth:
        apply_stealth(page)

    return p, browser, context, page
