# src/section508/engines/section508_selenium_hybrid.py
# 3.187083s

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from src.driver_manager.manager import driver_context
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from src.section508.engines.dataset_builder import save_json, save_csv
from src.utils.runntime_tracker import track_runtime


class Section508Scraper:

    def __init__(self, browser='firefox', headless=True):
        self.base_url = "https://www.section508.gov/test/"
        self.ctx_manager = driver_context(engine="selenium", browser=browser, headless=headless)
        self.driver_bundle = self.ctx_manager.__enter__()
        self.driver = self.driver_bundle
        self.wait = WebDriverWait(self.driver, 10)

    def open_section508(self):
        self.driver.get(self.base_url)
        print(self.driver.title)

    @track_runtime(engine_name="selenium")
    def find_all_data(self):

        self.driver.get(self.base_url)

        # wait until cards load
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.usa-card"))
        )

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        cards = soup.select("li.usa-card")

        cards_data = []

        # -------------------------------
        # STEP 1: parse card info
        # -------------------------------
        for card in cards:

            link = card.select_one("h2 a")
            desc = card.select_one(".usa-card__body p")
            href = urljoin(self.base_url, link["href"])
            title = link.contents[0].strip()


            cards_data.append({
                "href": href,
                "title": title,
                "description": desc.get_text(strip=True) if desc else ""
            })

        # -------------------------------
        # STEP 2: visit each page
        # -------------------------------
        for item in cards_data:

            self.driver.get(item["href"])

            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#content-section"))
            )

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            headings = soup.select("#content-section h2, #content-section h3")

            subtitles = []

            for h in headings:

                text = h.get_text(strip=True)

                if text and text != item["title"]:
                    subtitles.append(text)

            item["sub_titles"] = subtitles

        save_json(cards_data)
        save_csv(cards_data)
        print(f"Found {len(cards_data)} Section508 cards")



    def close_section508(self):
        self.ctx_manager.__exit__(None, None, None)


if __name__ == "__main__":
    print(f"Testing start....")
    scraper = Section508Scraper()
    scraper.find_all_data()
    scraper.close_section508()
