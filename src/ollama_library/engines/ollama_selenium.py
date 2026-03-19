# src/ollama_library/engines/ollama_selenium.py
# [selenium] find_all_data completed in 3 m 4.851142s
from src.driver_manager.manager import driver_context
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from src.ollama_library.engines.dataset_builder import save_json, save_csv
from src.utils.runntime_tracker import track_runtime


class OllamaScraper:

    def __init__(self, browser='firefox', headless=True):
        self.base_url = "https://ollama.com/library"
        self.ctx_manager = driver_context(engine="selenium", browser=browser, headless=headless)
        self.driver_bundle = self.ctx_manager.__enter__()
        self.driver = self.driver_bundle
        self.wait = WebDriverWait(self.driver, 10)
        self.KNOWN_CAPABILITIES = set()
        self.models_xpath = '//*[@id="repo"]/ul/li'

    def open_ollama(self):
        self.driver.get(self.base_url)
        self.wait.until(EC.presence_of_element_located((By.ID, "repo")))
        # print(self.driver.title)

    def scroll_to_bottom(self):
        last = 0
        while True:
            cards = self.driver.find_elements(By.XPATH, self.models_xpath)
            count = len(cards)
            if count == last:
                break
            last = count
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                WebDriverWait(self.driver, 3).until(
                    lambda d: len(d.find_elements(By.XPATH, self.models_xpath)) > count
                )
            except:
                break

    def set_capabilities(self):
        self.open_ollama()
        self.scroll_to_bottom()
        model_cards = self.driver.find_elements(By.XPATH, self.models_xpath)
        all_tags = []
        for card in model_cards:
            spans = card.find_elements(By.XPATH, './/div[contains(@class, "flex")]/div/span')
            for span in spans:
                text = span.text.strip()
                if text:
                    all_tags.append(text)
        tags_only = {tag for tag in all_tags if not any(c.isdigit() for c in tag) and tag.lower() != "latest"}
        self.KNOWN_CAPABILITIES = tags_only

    def get_model_tag_details(self, model_name):
        url = f"{self.base_url}/{model_name}/tags"
        self.driver.get(url)
        result = []
        # Wait until first data row appears
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.grid.grid-cols-12.items-center span.col-span-6 a")
                )
            )
        except:
            print(f"⚠ Timed out waiting for tag rows for {model_name}")
            return result

        # Find all data rows
        rows = self.driver.find_elements(
            By.CSS_SELECTOR, "div.grid.grid-cols-12.items-center"
        )
        for row in rows:
            # Skip header row
            if "bg-neutral-50" in row.get_attribute("class"):
                continue

            # Version name
            try:
                version = row.find_element(
                    By.CSS_SELECTOR, "span.col-span-6 a"
                ).text.strip()
            except:
                continue

            # Size and Context → <p class="col-span-2">
            p_cols = row.find_elements(By.CSS_SELECTOR, "p.col-span-2")
            size = p_cols[0].text.strip() if len(p_cols) > 0 else ""
            context = p_cols[1].text.strip() if len(p_cols) > 1 else ""

            # Input → <div class="col-span-2">
            d_cols = row.find_elements(By.CSS_SELECTOR, "div.col-span-2")
            input_type = d_cols[-1].text.strip() if d_cols else ""

            # Updated at → next sibling div after the grid row
            # Text looks like "6995872bfe4c · 9 months ago"
            try:
                sibling = row.find_element(
                    By.XPATH, "following-sibling::div[1]"
                )
                raw = sibling.text.replace('\xa0', ' ').strip()
                # Extract just "X months/years ago" — split on " · "
                if '·' in raw:
                    updated_at = raw.split('·')[-1].strip()
                else:
                    updated_at = raw
            except:
                updated_at = None

            if version:
                result.append({
                    "name": version,
                    "size": size,
                    "context": context,
                    "input": input_type,
                    "usage_command": f"ollama pull {version}",
                    "updated_at": updated_at
                })
        return result

    @track_runtime(engine_name="selenium")
    def find_all_data(self):
        # 1. set up the capabilities
        self.set_capabilities()
        cards = self.driver.find_elements(By.XPATH, self.models_xpath)
        basic_info_list = []
        for card in cards:
            try:
                name = card.find_element(By.XPATH, './/h2/div/span').text
                summary = card.find_element(By.XPATH, './/p').text

                metadata1 = card.find_elements(By.XPATH, './/div[contains(@class, "flex")]/div/span')
                data = [span.text for span in metadata1 if span.text.strip()]
                capabilities = [cap for cap in data if cap in self.KNOWN_CAPABILITIES]
                versions = [v for v in data if v not in self.KNOWN_CAPABILITIES]

                for item in data:
                    if item not in self.KNOWN_CAPABILITIES and not any(
                            char.isdigit() for char in item) and item != 'latest':
                        print(f"DEBUG: Found potential new capability tag: {item}")

                primary_version = versions[0] if versions else "latest"

                meta_spans_3 = card.find_elements(By.XPATH, './/div[contains(@class, "flex")]/p/span')
                metadata = [(span.text).replace('\n', '') for span in meta_spans_3 if span.text.strip()]

                basic_info_list.append({
                    "model_name": name,
                    "primary_version": primary_version,
                    "capabilities": capabilities,
                    "metadata": metadata,
                    "summary": summary,
                    "usage_command": f"ollama run {name}:{primary_version}",
                    "url": f"https://ollama.com/library/{name}",
                    "updated_at": metadata[2] if len(metadata) > 2 else "Unknown",
                })
            except Exception as e:
                print(f"Error collecting basic info: {e}")
                continue

        results = []
        for i, info in enumerate(basic_info_list):
            name = info["model_name"]
            print(f"  [{i + 1}/{len(basic_info_list)}] Fetching tags for {name}...")
            try:
                versions = self.get_model_tag_details(name)
            except Exception as e:
                print(f"  ⚠ Failed to get tags for {name}: {e}")
                versions = []

            results.append({
                **info,
                "versions": versions,
            })
        save_json(results)
        save_csv(results)
        print(f"Successfully archived {len(results)} models.")

    def close_ollama(self):
        self.ctx_manager.__exit__(None, None, None)


if __name__ == "__main__":
    print(f"Testing start....")
    scraper = OllamaScraper()
    scraper.find_all_data()
    scraper.close_ollama()
