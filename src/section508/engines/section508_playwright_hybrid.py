from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.driver_manager.manager import driver_context
from src.section508.engines.dataset_builder import save_json, save_csv
from src.utils.runntime_tracker import track_runtime


class Section508Scraper:
    def __init__(self, browser='firefox', headless=True):
        self.base_url = "https://www.section508.gov/test/"
        self.ctx_manager = driver_context(engine="playwright", browser=browser, headless=headless)
        self.driver_bundle = self.ctx_manager.__enter__()
        self.p, self.browser, self.context, self.page = self.driver_bundle

    def open_section508(self):
        self.page.goto(self.base_url)
        print(self.page.title())

    @track_runtime(engine_name="playwright")
    def find_all_data(self):

        self.page.goto(self.base_url)
        self.page.wait_for_selector("li.usa-card")
        soup = BeautifulSoup(self.page.content(), "html.parser")
        cards = soup.select("li.usa-card")
        cards_data = []

        # -------------------------
        # STEP 1: extract card info
        # -------------------------
        for card in cards:
            link = card.select_one("h2 a")
            desc = card.select_one(".usa-card__body p")
            href = urljoin(self.base_url, link["href"])
            title = link.contents[0].strip() if link.contents else link.get_text(strip=True)

            cards_data.append({
                "href": href,
                "title": title,
                "description": desc.get_text(strip=True) if desc else ""
            })

        # -------------------------
        # STEP 2: visit each page
        # -------------------------
        for item in cards_data:
            self.page.goto(item["href"])

            self.page.wait_for_selector("#content-section")
            soup = BeautifulSoup(self.page.content(), "html.parser")
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
        self.page.close()


if __name__ == "__main__":
    print(f"Testing start....")
    scraper = Section508Scraper()
    scraper.find_all_data()
    scraper.close_section508()