# driver_manager/playwright_engine.py

import sys
from playwright.sync_api import sync_playwright


def get_playwright_driver(headless=True, browser_type="chromium", device_name=None):
    p = sync_playwright().start()

    # 1. VALIDATION: Check if device exists
    if device_name and device_name not in p.devices:
        available_devices = list(p.devices.keys())[:5]  # Show a few examples
        p.stop()  # Clean up before crashing
        raise ValueError(
            f"❌ Invalid device: '{device_name}'. \n"
            f"Suggested devices: {available_devices}..."
        )

    # ... rest of your browser launch logic ...
    if browser_type == "firefox":
        browser = p.firefox.launch(headless=headless)
    elif browser_type == "webkit":
        browser = p.webkit.launch(headless=headless)
    else:
        browser = p.chromium.launch(headless=headless)

    # 2. APPLY EMULATION
    if device_name:
        context = browser.new_context(**p.devices[device_name])
    else:
        context = browser.new_context()

    page = context.new_page()
    return p, browser, context, page

# # driver_manager/playwright_engine.py
#
# from playwright.sync_api import sync_playwright
# from src.driver_manager.auto_install import ensure_playwright_browsers
# from src.driver_manager.stealth import apply_stealth
# from src.driver_manager.proxy_manager import GLOBAL_PROXY_MANAGER
# from src.driver_manager.retry import retry
#
# @retry(times=2)
# def get_playwright_driver(headless=True, use_stealth=True, use_proxy=False):
#     ensure_playwright_browsers()
#
#     proxy = GLOBAL_PROXY_MANAGER.get_random() if use_proxy else None
#
#     p = sync_playwright().start()
#
#     browser = p.chromium.launch(
#         headless=headless,
#         proxy={"server": proxy} if proxy else None,
#         args=[
#             "--disable-blink-features=AutomationControlled",
#             "--no-sandbox",
#             "--disable-dev-shm-usage",
#         ],
#     )
#
#     context = browser.new_context()
#     page = context.new_page()
#
#     if use_stealth:
#         apply_stealth(page)
#
#     return p, browser, context, page
