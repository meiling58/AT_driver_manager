import time
from functools import wraps

from src.driver_manager.auto_tuner import run_auto_tuner
from src.driver_manager.manager import driver_context, get_driver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from src.driver_manager.auto_select_driver_manager import auto_driver_context, get_recommended_config

def track_runtime(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"\n⏱️ '{func.__name__}' completed in {duration:.2f}s")
        return result

    return wrapper


class Section508Scraper:

    def __init__(self, headless=False):
        self.base_url = "https://www.section508.gov/test/"
        self.config = get_recommended_config()
        self.ctx_manager = auto_driver_context(headless=headless)
        self.driver_bundle = self.ctx_manager.__enter__()
        self.engine = self.config['engine']
        if self.engine == "playwright":
            self.p, self.browser, self.context, self.page = self.driver_bundle
        else:
            self.driver = self.driver_bundle


        self.sections_path = '//*[@id="content-section"]/div/section/ul/li'

    def open_section508(self):
        self.page.goto(self.base_url)
        print(self.page.title())


    def close_section508(self):
        self.page.close()

if __name__ == "__main__":

    print(f"Testing start....")
    scraper = Section508Scraper()
    scraper.open_section508()
    scraper.close_section508()

