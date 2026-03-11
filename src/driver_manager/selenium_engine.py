# driver_manager/selenium_engine.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from src.driver_manager.proxy_manager import GLOBAL_PROXY_MANAGER
from src.driver_manager.retry import retry

@retry(times=2)
def get_selenium_driver(browser="chrome", headless=True, use_proxy=False):
    browser = browser.lower()
    proxy = GLOBAL_PROXY_MANAGER.get_random() if use_proxy else None

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        return webdriver.Chrome(options=options)

    if browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        return webdriver.Firefox(options=options)

    if browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")
        return webdriver.Edge(options=options)

    raise ValueError("Unsupported Selenium browser.")
