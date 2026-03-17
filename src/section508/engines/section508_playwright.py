from src.driver_manager.manager import driver_context
from src.section508.engines.dataset_builder import save_json, save_csv
from src.utils.runntime_tracker import track_runtime


class Section508Scraper:
    def __init__(self, browser='firefox', headless=True):
        self.base_url = "https://www.section508.gov/test/"
        self.ctx_manager = driver_context(engine="playwright", browser=browser, headless=headless)
        self.driver_bundle = self.ctx_manager.__enter__()
        self.p, self.browser, self.context, self.page = self.driver_bundle

        self.sections_path = '//*[@id="content-section"]/div/section/ul/li'

    def open_section508(self):
        self.page.goto(self.base_url, wait_until="networkidle")
        print(self.page.title())

    @track_runtime(engine_name="playwright")
    def find_all_data(self):
        self.page.goto(self.base_url, wait_until="networkidle")
        self.page.wait_for_selector("li.usa-card")

        cards = (self.page.locator("li.usa-card")).all()

        cards_data = []

        # -------------------------------
        # STEP 1: Collect card data only
        # -------------------------------
        for card in cards:
            link = card.locator("h2 a")
            href = link.get_attribute("href")
            title = link.inner_text().strip()

            description = card.locator(".usa-card__body p").inner_text().strip()

            if not href or not title:
                continue

            # Make sure we have absolute URL
            if href.startswith("/"):
                href = "https://www.section508.gov" + href

            cards_data.append({
                "href": href,
                "title": title,
                "description": description
            })

        # --------------------------------
        # STEP 2: Visit each page for subtitles
        # --------------------------------
        for item in cards_data:

            self.page.goto(item["href"])

            self.page.wait_for_selector("#content-section")

            headings = self.page.locator("#content-section h2, #content-section h3").all()

            subtitles = []

            for h in headings:
                text = h.inner_text().strip()

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
    # scraper.open_section508()
    scraper.find_all_data()
    scraper.close_section508()