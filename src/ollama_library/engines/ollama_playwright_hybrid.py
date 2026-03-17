# src/ollama_library/engines/ollama_playwright_hybrid.py
# ⏱️ [playwright] find_all_data completed in 0 m 30.106338s

from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup

from src.driver_manager.manager import driver_context
from src.ollama_library.engines.dataset_builder import save_json, save_csv
from src.utils.runntime_tracker import track_runtime


class OllamaScraper:
    def __init__(self, browser='firefox', headless=True, max_workers=30):
        self.base_url = "https://ollama.com/library"
        self.ctx_manager = driver_context(engine="playwright", browser=browser, headless=headless)
        self.driver_bundle = self.ctx_manager.__enter__()
        self.p, self.browser, self.context, self.page = self.driver_bundle
        self.KNOWN_CAPABILITIES = set()
        self.models_xpath = '//*[@id="repo"]/ul/li'
        self.max_workers = max_workers

    def open_ollama(self):
        self.page.goto(self.base_url, wait_until="networkidle")
        print(self.page.title())

    def scroll_to_bottom(self):
        print("🖱️ Scrolling to load all models...")
        last_count = 0
        while True:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_selector("#repo ul li")
            # time.sleep(1.5)
            current_count = len(self.page.query_selector_all("#repo ul li"))
            if current_count == last_count: break
            last_count = current_count
        print(f"✅ Library fully expanded: {last_count} models.")

    def set_capabilities(self):
        self.open_ollama()
        self.scroll_to_bottom()
        css = 'div[class="flex flex-wrap space-x-2"]'
        cards = self.page.locator(css).all()
        all_tags = []
        for card in cards:
            texts = card.inner_text().strip().split("\n")
            for text in texts:
                if not any(map(str.isdigit, text)):
                    all_tags.append(text)
        all_tags = list(dict.fromkeys(all_tags))  # remove duplicate
        all_tags = [item for item in all_tags if item != ""]  # remove ""
        self.KNOWN_CAPABILITIES = set(all_tags)

    def get_model_tag_details(self, model_name):
        url = f"{self.base_url}/{model_name}/tags"
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.select("div.grid.grid-cols-12.items-center")
            versions = []
            for row in rows:
                if "bg-neutral-50" in row.get("class", []): continue
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


    @track_runtime(engine_name="playwright")
    def find_all_data(self):
        self.set_capabilities()
        cards = self.page.query_selector_all("#repo ul li")
        cards_data = []

        # -------------------------------
        # STEP 1: Collect card data only
        # -------------------------------
        for card in cards:
            try:
                name = card.query_selector("h2 span").inner_text().strip()
                summary = card.query_selector("p").inner_text().strip() if card.query_selector("p") else ""
                # metadata info
                raw_metadata = card.query_selector_all("span.flex")
                metadata = []
                for m in raw_metadata:
                    metadata.append(m.inner_text().strip().replace('\xa0', '').replace("\n", " "))

                # 2. Capabilities vs Versions
                # Feature tags are usually in a specific container
                tag_els = card.query_selector_all("div.flex.flex-wrap span")
                all_tags = [t.inner_text().strip() for t in tag_els]

                capabilities = [t for t in all_tags if t.lower() in self.KNOWN_CAPABILITIES]
                primary_v = next((t for t in all_tags if t.lower() not in self.KNOWN_CAPABILITIES), "latest")

                cards_data.append({
                    "model_name": name,
                    "primary_version": primary_v,
                    "capabilities": capabilities,
                    "metadata": metadata,
                    "summary": summary,
                    "url": f"{self.base_url}/{name}",
                    "usage_command": f"ollama run {name}:{primary_v}",
                    "updated_at": metadata[-1] if metadata else "Unknown"
                })
            except Exception:
                continue
        print(f"collect basic data")

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_model = {executor.submit(self.get_model_tag_details, m["model_name"]): m for m in cards_data}
            for i, future in enumerate(as_completed(future_to_model), 1):
                model_info = future_to_model[future]
                model_info["versions"] = future.result()
                results.append(model_info)
                if i % 50 == 0: print(f"Completed {i}/{len(cards_data)}")

        save_json(results)
        save_csv(results)
        print(f"Successfully archived {len(cards_data)} models.")


    def close_ollama(self):
        self.page.close()


if __name__ == "__main__":
    print(f"Testing start....")
    scraper = OllamaScraper()
    scraper.find_all_data()
    scraper.close_ollama()