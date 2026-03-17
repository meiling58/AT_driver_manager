# src/section508/engines/section508_selenium.py

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
        # Wait until cards appear
        cards = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.usa-card"))
        )

        cards_data = []

        # -------------------------------
        # STEP 1: Collect card data only
        # -------------------------------
        for card in cards:
            link = card.find_element(By.CSS_SELECTOR, "h2 a")

            href = link.get_attribute("href")
            title = link.text.strip()

            description = card.find_element(
                By.CSS_SELECTOR, ".usa-card__body p"
            ).text.strip()

            cards_data.append({
                "href": href,
                "title": title,
                "description": description
            })

        # --------------------------------
        # STEP 2: Visit each page for subtitles
        # --------------------------------
        for item in cards_data:

            self.driver.get(item["href"])

            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#content-section"))
            )

            headings = self.driver.find_elements(
                By.CSS_SELECTOR,
                "#content-section h2, #content-section h3"
            )

            subtitles = []

            for h in headings:
                text = h.text.strip()

                if text and text != item["title"]:
                    subtitles.append(text)

            item["sub_titles"] = subtitles

        save_json(cards_data)
        save_csv(cards_data)
        print(f"Found {len(cards_data)} Section508 cards")
        return cards_data

    def close_section508(self):
        self.ctx_manager.__exit__(None, None, None)


if __name__ == "__main__":
    print(f"Testing start....")
    scraper = Section508Scraper()
    scraper.find_all_data()
    scraper.close_section508()
