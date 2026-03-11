# archive/driver_manager.py
# all in one driver_manager will split to modules
# please check /driver_manager/ for details

import os
import shutil
import subprocess
import random
import time
from contextlib import contextmanager

# Selenium (secondary engine)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

# Playwright (primary engine)
from playwright.sync_api import sync_playwright


# ============================================================
# 1. Retry decorator (for robustness)
# ============================================================

def retry(times=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"[Retry {attempt+1}/{times}] {func.__name__} failed:", e)
                    time.sleep(delay)
            raise RuntimeError(f"{func.__name__} failed after {times} retries")
        return wrapper
    return decorator


# ============================================================
# 2. Proxy manager (simple rotation)
# ============================================================

class ProxyManager:
    def __init__(self, proxies=None):
        self.proxies = proxies or []

    def add(self, proxy: str):
        self.proxies.append(proxy)

    def get_random(self):
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def get_next(self):
        if not self.proxies:
            return None
        proxy = self.proxies.pop(0)
        self.proxies.append(proxy)
        return proxy


# Example: you can populate this from env, file, etc.
GLOBAL_PROXY_MANAGER = ProxyManager(
    proxies=[
        # "http://user:pass@host:port",
        # "http://host:port",
    ]
)


# ============================================================
# 3. Stealth helpers for Playwright
# ============================================================

def apply_stealth(page):
    # Remove webdriver
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    """)

    # Fake plugins
    page.add_init_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4]
        });
    """)

    # Fake languages
    page.add_init_script("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """)

    # Fake WebGL vendor
    page.add_init_script("""
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {
            if (param === 37445) return 'Intel Inc.';
            if (param === 37446) return 'Intel Iris OpenGL Engine';
            return getParameter(param);
        };
    """)

    # Fake timezone
    page.add_init_script("""
        Intl.DateTimeFormat = function() {
            return { resolvedOptions: () => ({ timeZone: 'America/New_York' }) };
        };
    """)


# ============================================================
# 4. Auto-install Playwright browsers if missing
# ============================================================

def ensure_playwright_browsers():
    """
    Ensures Playwright browsers are installed.
    Safe to call every time; it only installs if missing.
    """
    try:
        if shutil.which("playwright") is None:
            print("Playwright CLI not found in PATH.")
            return

        # Very simple existence check; you can refine this per OS
        base_dir = os.path.expanduser("~")
        possible_dir = os.path.join(base_dir, "AppData", "Local", "ms-playwright")
        if not os.path.exists(possible_dir):
            print("Playwright browsers missing. Installing...")
            subprocess.run(["playwright", "install"], check=True)

    except Exception as e:
        print("Failed to auto-install Playwright browsers:", e)


# ============================================================
# 5. Playwright primary engine
# ============================================================

@retry(times=2, delay=1)
def get_playwright_driver(
    headless: bool = True,
    use_stealth: bool = True,
    use_proxy: bool = False,
):
    ensure_playwright_browsers()

    proxy = None
    if use_proxy:
        proxy = GLOBAL_PROXY_MANAGER.get_random()
        print("Using proxy for Playwright:", proxy)

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

    # Return all so caller can choose what to use
    return p, browser, context, page


# ============================================================
# 6. Selenium secondary engine (only when requested)
# ============================================================

@retry(times=2, delay=1)
def get_selenium_driver(
    browser: str = "chrome",
    headless: bool = True,
    use_proxy: bool = False,
):
    browser = browser.lower()
    proxy = GLOBAL_PROXY_MANAGER.get_random() if use_proxy else None

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
            print("Using proxy for Selenium Chrome:", proxy)
        return webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        if proxy:
            options.set_preference("network.proxy.type", 1)
            host, port = proxy.split(":") if ":" in proxy else (proxy, "8080")
            options.set_preference("network.proxy.http", host)
            options.set_preference("network.proxy.http_port", int(port))
            options.set_preference("network.proxy.ssl", host)
            options.set_preference("network.proxy.ssl_port", int(port))
            print("Using proxy for Selenium Firefox:", proxy)
        return webdriver.Firefox(options=options)

    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
            print("Using proxy for Selenium Edge:", proxy)
        return webdriver.Edge(options=options)

    raise ValueError("Unsupported Selenium browser. Use: chrome, firefox, edge.")


# ============================================================
# 7. Unified driver getter with smart-ish fallback
# ============================================================

def get_driver(
    browser: str = "chrome",
    headless: bool = True,
    engine: str = "playwright",   # "playwright" or "selenium"
    use_stealth: bool = True,
    use_proxy: bool = False,
    allow_fallback: bool = True,
):
    """
    Main entry point.

    - Playwright is primary engine.
    - Selenium only used when explicitly requested or as fallback (if allow_fallback=True).
    """
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
                return get_selenium_driver(
                    browser=browser,
                    headless=headless,
                    use_proxy=use_proxy,
                )
            raise

    if engine == "selenium":
        return get_selenium_driver(
            browser=browser,
            headless=headless,
            use_proxy=use_proxy,
        )

    raise ValueError("Engine must be 'playwright' or 'selenium'.")


# ============================================================
# 8. Context manager for auto-cleanup
# ============================================================

@contextmanager
def driver_context(
    browser: str = "chrome",
    headless: bool = True,
    engine: str = "playwright",
    use_stealth: bool = True,
    use_proxy: bool = False,
    allow_fallback: bool = True,
):
    """
    Yields either:
      - (p, browser, context, page) for Playwright
      - selenium_driver for Selenium
    and cleans up properly afterward.
    """
    driver = get_driver(
        browser=browser,
        headless=headless,
        engine=engine,
        use_stealth=use_stealth,
        use_proxy=use_proxy,
        allow_fallback=allow_fallback,
    )

    try:
        yield driver
    finally:
        # Playwright: tuple
        if isinstance(driver, tuple) and len(driver) == 4:
            p, browser_obj, context, page = driver
            try:
                page.close()
            except Exception:
                pass
            try:
                context.close()
            except Exception:
                pass
            try:
                browser_obj.close()
            except Exception:
                pass
            try:
                p.stop()
            except Exception:
                pass
        else:
            # Selenium
            try:
                driver.quit()
            except Exception:
                pass


# ============================================================
# 9. Test routine
# ============================================================

def test_all():
    print("\n=== Testing Playwright (primary, stealth + no proxy) ===")
    try:
        with driver_context(engine="playwright", use_stealth=True, use_proxy=False) as d:
            print("Playwright initialized successfully.")
    except Exception as e:
        print("Playwright FAILED:", e)

    print("\n=== Testing Playwright (with proxy, if any configured) ===")
    try:
        with driver_context(engine="playwright", use_stealth=True, use_proxy=True) as d:
            print("Playwright with proxy initialized successfully.")
    except Exception as e:
        print("Playwright with proxy FAILED:", e)

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
