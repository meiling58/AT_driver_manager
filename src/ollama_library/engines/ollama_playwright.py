# src/ollama_library/engines/ollama_playwright.py
# 5m 11.739165s

from src.driver_manager.manager import driver_context
from src.ollama_library.engines.dataset_builder import save_json, save_csv
from src.utils.runntime_tracker import track_runtime


class OllamaScraper:
    def __init__(self, browser='firefox', headless=True):
        self.base_url = "https://ollama.com/library"
        self.ctx_manager = driver_context(engine="playwright", browser=browser, headless=headless)
        self.driver_bundle = self.ctx_manager.__enter__()
        self.p, self.browser, self.context, self.page = self.driver_bundle
        self.KNOWN_CAPABILITIES = set()
        self.models_xpath = '//*[@id="repo"]/ul/li'


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

        # Wait until first data row appears
        self.page.goto(url, wait_until="networkidle")
        try:
            self.page.wait_for_selector("div.grid.grid-cols-12.items-center span.col-span-6 a")

        except Exception as e:
            print(f"Timed out waiting for tag rows for {model_name}: {e}")

        rows = self.page.locator("div.grid.grid-cols-12.items-center").all()

        data = []
        for row in rows:
            # skip header/table
            if row.get_attribute("class").find("bg-neutral-50") != -1:
                continue
            d = row.inner_text().splitlines()
            d = list(filter(lambda item: item not in ["","latest"], d))
            name = d[0] if len(d) > 0 else None
            size = d[1] if len(d) > 0 else None
            context = d[2] if len(d) > 0 else None
            input_type = d[3] if len(d) > 0 else None

            try:
                # Get the next sibling div
                sibling = row.evaluate('''element => {
                            let nextSibling = element.nextElementSibling;
                            return nextSibling ? nextSibling.outerHTML : null;
                        }''')
                if sibling:
                    # Parse the sibling content
                    sibling_text = self.page.evaluate('''html => {
                                    const div = document.createElement('div');
                                    div.innerHTML = html;
                                    return div.textContent || div.innerText || '';
                                }''', sibling)

                    raw = sibling_text.replace('\xa0', ' ').strip()
                    if '·' in raw:
                        updated_at = raw.split('·')[-1].strip()
                    else:
                        updated_at = raw
                else:
                    updated_at = None

            except:
                updated_at = None

            data.append({
                "name": name,
                "size": size,
                "context": context,
                "input_type": input_type,
                "usage_command": f"ollama pull {name}",
                "updated_at": updated_at,
            })

        return data


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
        for i, info in enumerate(cards_data):
            name = info["model_name"]
            print(f"  [{i + 1}/{len(cards_data)}] Fetching tags for {name}...")
            try:
                versions = self.get_model_tag_details(name)
            except Exception as e:
                print(f"  ⚠ Failed to get tags for {name}: {e}")

                versions =[]
            results.append({
                **info,
                "versions": versions,
            })

        save_json(cards_data)
        save_csv(cards_data)
        print(f"Successfully archived {len(cards_data)} models.")


    def close_ollama(self):
        self.page.close()


if __name__ == "__main__":
    print(f"Testing start....")
    scraper = OllamaScraper()
    scraper.find_all_data()
    scraper.close_ollama()