# driver_manager/selenium_engine.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from src.driver_manager.proxy_manager import GLOBAL_PROXY_MANAGER
from src.driver_manager.retry import retry


# This is the "Gold Standard" list for Chrome/Edge emulation
SELENIUM_VALID_DEVICES = [
    "iPhone X", "iPhone XR", "iPhone SE", "iPhone 12 Pro",
    "Pixel 5", "Pixel 7", "Samsung Galaxy S8+", "Samsung Galaxy S20 Ultra",
    "iPad Air", "iPad Mini"
]

@retry(times=2)
def get_selenium_driver(browser_type="chrome", headless=True, use_proxy=False, device_name=None):
    browser_type = browser_type.lower()
    proxy = GLOBAL_PROXY_MANAGER.get_random() if use_proxy else None

    # 1. Validation for Mobile Emulation
    if device_name and device_name not in SELENIUM_VALID_DEVICES:
        # We raise a ValueError to stop the @retry from looping
        raise ValueError(f"❌ '{device_name}' is not a valid Selenium device name. Try: {SELENIUM_VALID_DEVICES[:3]}")

    # 1. Chrome & Edge (Support Mobile Emulation)
    if browser_type in ["chrome", "msedge"]:
        options = ChromeOptions() if browser_type == "chrome" else EdgeOptions()

        if headless:
            options.add_argument("--headless=new")

        if proxy:
            options.add_argument(f"--proxy-server={proxy}")

        # Add Mobile Emulation
        if device_name:
            # Selenium uses a specific dictionary for mobile emulation
            mobile_emulation = {"deviceName": device_name}
            options.add_experimental_option("mobileEmulation", mobile_emulation)

        if browser_type == "msedge":
            return webdriver.Edge(options=options)
        return webdriver.Chrome(options=options)

    # 2. Firefox (Does not natively support 'deviceName' emulation like Chrome)
    if browser_type == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        if device_name:
            print(f"⚠️ Warning: Selenium Firefox does not support 'deviceName' emulation. Testing desktop instead.")
        return webdriver.Firefox(options=options)

    raise ValueError(f"Unsupported Selenium browser: {browser_type}")




# # driver_manager/selenium_engine.py
#
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options as ChromeOptions
# from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver.edge.options import Options as EdgeOptions
#
# from src.driver_manager.proxy_manager import GLOBAL_PROXY_MANAGER
# from src.driver_manager.retry import retry
#
# @retry(times=2)
# def get_selenium_driver(browser="chrome", headless=True, use_proxy=False):
#     browser = browser.lower()
#     proxy = GLOBAL_PROXY_MANAGER.get_random() if use_proxy else None
#
#     if browser == "chrome":
#         options = ChromeOptions()
#         if headless:
#             options.add_argument("--headless=new")
#         if proxy:
#             options.add_argument(f"--proxy-server={proxy}")
#         return webdriver.Chrome(options=options)
#
#     if browser == "firefox":
#         options = FirefoxOptions()
#         if headless:
#             options.add_argument("--headless")
#         return webdriver.Firefox(options=options)
#
#     if browser == "edge":
#         options = EdgeOptions()
#         if headless:
#             options.add_argument("--headless")
#         return webdriver.Edge(options=options)
#
#     raise ValueError("Unsupported Selenium browser.")
