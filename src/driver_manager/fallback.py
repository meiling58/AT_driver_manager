import random
from contextlib import contextmanager
# from driver_manager.manager import driver_context
# from driver_manager.proxy_manager import GLOBAL_PROXY_MANAGER
# from driver_manager.stealth import apply_stealth
# from driver_manager.retry import retry
from web_drivers_modular_architecture.src.driver_manager.manager import driver_context
from web_drivers_modular_architecture.src.driver_manager.retry import retry


class FallbackError(Exception):
    pass


def try_playwright(url, use_stealth=False, use_proxy=False):
    with driver_context(
        engine="playwright",
        use_stealth=use_stealth,
        use_proxy=use_proxy
    ) as d:
        p, browser, context, page = d
        page.goto(url)
        return page.title()


def try_selenium(url, use_proxy=False):
    with driver_context(
        engine="selenium",
        use_proxy=use_proxy
    ) as d:
        driver = d
        driver.get(url)
        return driver.title


@retry(times=3, delay=1)
def run_with_fallback(url):
    """
    Try multiple strategies until one succeeds.
    """
    strategies = [
        ("Playwright", lambda: try_playwright(url)),
        ("Playwright + stealth", lambda: try_playwright(url, use_stealth=True)),
        ("Playwright + proxy", lambda: try_playwright(url, use_proxy=True)),
        ("Playwright + new proxy", lambda: try_playwright(url, use_proxy=True)),
        ("Selenium", lambda: try_selenium(url)),
        ("Selenium + proxy", lambda: try_selenium(url, use_proxy=True)),
    ]

    for name, func in strategies:
        try:
            print(f"Trying: {name}")
            return func()
        except Exception as e:
            print(f"  Failed: {name} → {e}")

    raise FallbackError(f"All fallback strategies failed for URL: {url}")
