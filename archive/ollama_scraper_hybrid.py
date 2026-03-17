# src/ollama_library/ollama_scraper_hybrid.py

import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from src.driver_manager.auto_select_driver_manager import auto_driver_context, get_recommended_config
from src.ollama_library.engines.dataset_builder import save_json, save_csv
from src.utils.runntime_tracker import track_runtime


# def track_runtime(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         start = time.time()
#         result = func(*args, **kwargs)
#         duration = time.time() - start
#         print(f"\n⏱️ '{func.__name__}' completed in {duration:.2f}s")
#         return result
#
#     return wrapper


class OllamaScraperHybrid:
    def __init__(self, headless=True, max_workers=30):
        self.config = get_recommended_config()
        self.ctx_manager = auto_driver_context(headless=headless)
        self.driver_bundle = self.ctx_manager.__enter__()

        self.engine = self.config['engine']
        if self.engine == "playwright":
            self.p, self.browser, self.context, self.page = self.driver_bundle
        else:
            self.driver = self.driver_bundle

        self.base_url = "https://ollama.com/library"
        self.max_workers = max_workers
        self.KNOWN_CAPABILITIES = set()

    def scroll_to_bottom(self):
        print("🖱️ Scrolling to load all models...")
        last_count = 0
        while True:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.5)
            current_count = len(self.page.query_selector_all("#repo ul li"))
            if current_count == last_count: break
            last_count = current_count
        print(f"✅ Library fully expanded: {last_count} models.")

    def detect_capabilities(self):
        """Specifically targets blue badges (capabilities) and excludes names/stats."""
        print("🔍 Detecting capabilities dynamically...")
        # Targeting badges that are usually blue/purple (tools, vision, etc.)
        # These typically have 'bg-blue-50' or similar classes in Ollama's UI
        elements = self.page.query_selector_all("span[class*='bg-blue'], span[class*='bg-purple']")

        found = set()
        for el in elements:
            txt = el.inner_text().strip().lower()
            if txt and not any(c.isdigit() for c in txt) and txt != "latest":
                found.add(txt)

        # Fallback if specific classes aren't found: use the original "tools/vision" set as base
        self.KNOWN_CAPABILITIES = found if found else {"tools", "vision", "embedding", "thinking", "cloud"}
        print(f"✅ Capabilities Detected: {self.KNOWN_CAPABILITIES}")

    def get_basic_info(self):
        """Parses model cards with sanitized metadata cleaning."""
        cards = self.page.query_selector_all("#repo ul li")
        basic_info = []

        for card in cards:
            try:
                name = card.query_selector("h2 span").inner_text().strip()
                summary = card.query_selector("p").inner_text().strip() if card.query_selector("p") else ""

                # 1. Clean Metadata (Pulls, Tags, Updated)
                # We target the row with icons and split/clean the \n characters
                meta_els = card.query_selector_all("div.flex.items-center.gap-x-4 span")
                raw_meta = [m.inner_text().strip().replace('\n', ' ') for m in meta_els]
                # Filter out the repeating words (e.g., keep "7.3M Pulls", remove "Pulls")
                metadata = []
                for m in raw_meta:
                    if m and m not in ["Pulls", "Tags", "Updated"]:
                        metadata.append(m)

                # 2. Capabilities vs Versions
                # Feature tags are usually in a specific container
                tag_els = card.query_selector_all("div.flex.flex-wrap span")
                all_tags = [t.inner_text().strip() for t in tag_els]

                capabilities = [t for t in all_tags if t.lower() in self.KNOWN_CAPABILITIES]
                primary_v = next((t for t in all_tags if t.lower() not in self.KNOWN_CAPABILITIES), "latest")

                basic_info.append({
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
        return basic_info

    def fetch_versions_http(self, model_name):
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

    @track_runtime
    def run_full_scrape(self):
        self.page.goto(self.base_url)
        self.scroll_to_bottom()

        self.detect_capabilities()
        basic_info = self.get_basic_info()

        print(f"🚀 Threading {len(basic_info)} models...")
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_model = {executor.submit(self.fetch_versions_http, m["model_name"]): m for m in basic_info}
            for i, future in enumerate(as_completed(future_to_model), 1):
                model_info = future_to_model[future]
                model_info["versions"] = future.result()
                results.append(model_info)
                if i % 50 == 0: print(f"Completed {i}/{len(basic_info)}")

        return results

    def save_data(self, data):
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)
        save_json(data, data_dir / "ollama_library.json")
        save_csv(data, data_dir / "ollama_library.csv")

    def close(self):
        self.ctx_manager.__exit__(None, None, None)


if __name__ == "__main__":
    scraper = OllamaScraperHybrid(headless=True, max_workers=30)
    try:
        results = scraper.run_full_scrape()
        scraper.save_data(results)
    finally:
        scraper.close()