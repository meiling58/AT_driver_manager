# src/ollama_library/engines/ollama_selenium_hybrid.py
# ⏱️ [selenium] find_all_data completed in 0 m 26.792062s
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

from src.driver_manager.manager import driver_context
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from src.ollama_library.engines.dataset_builder import save_json, save_csv
from src.utils.runntime_tracker import track_runtime


class OllamaScraper:

    def __init__(self, browser='firefox', headless=True, max_workers=30):
        self.base_url = "https://ollama.com/library"
        self.ctx_manager = driver_context(engine="selenium", browser=browser, headless=headless)
        self.driver_bundle = self.ctx_manager.__enter__()
        self.driver = self.driver_bundle
        self.wait = WebDriverWait(self.driver, 10)
        self.KNOWN_CAPABILITIES = set()
        self.models_xpath = '//*[@id="repo"]/ul/li'
        self.max_workers = max_workers


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

        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            rows = soup.select("div.grid.grid-cols-12.items-center")
            versions = []
            for row in rows:
                if "bg-neutral-50" in row.get("class",[]): continue  # skipping header
                v_name_tag = row.select_one("span.col-span-6 a")
                if not v_name_tag: continue
                p_cols = row.select("p.col-span-2")
                d_cols = row.select("div.col-span-2")
                sibling = row.find_next_sibling("div")
                raw = sibling.get_text(strip=True).replace("\xa0", " ") if sibling else ""
                versions.append({
                    "name": v_name_tag.text.strip(),
                    "size": p_cols[0].text.strip() if len(p_cols) > 0 else "",
                    "context": p_cols[1].text.strip() if len(p_cols) > 1 else "",
                    "input": d_cols[-1].text.strip() if d_cols else "",
                    "usage_command": f"ollama pull {v_name_tag.text.strip()}",
                    "updated_at": raw.split("·")[-1].strip() if "·" in raw else raw
                })

            return versions
        except Exception:
            return []

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
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_model = {executor.submit(self.get_model_tag_details, m["model_name"]): m for m in basic_info_list}
            for i, future in enumerate(as_completed(future_to_model), 1):
                model_info = future_to_model[future]
                model_info["versions"] = future.result()
                results.append(model_info)
                if i % 50 == 0: print(f"Completed {i}/{len(basic_info_list)}")

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
