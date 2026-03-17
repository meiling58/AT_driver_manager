import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.driver_manager.manager import driver_context
from src.ollama_library.engines.dataset_builder import save_json, save_csv


class OllamaScraperHybrid:
    def __init__(self, browser="firefox", headless=True):
        # self.driver = driver_context(engine="playwright", browser=browser, headless=headless)
        ctx = driver_context(engine="selenium", browser=browser, headless=headless)
        # self._ctx = driver_context(engine="selenium", browser=browser, headless=headless)
        self.driver = ctx.__enter__()

        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "https://ollama.com/library"
        self.models_xpath = '//*[@id="repo"]/ul/li'
        self.KNOWN_CAPABILITIES = set()

    # Load Main Page
    def open_library(self):
        self.driver.get(self.base_url)
        self.wait.until(EC.presence_of_element_located((By.ID, "repo")))

    # scroll until all models are loaded
    def scroll_to_bottom(self):
        last_count = 0
        while True:
            cards = self.driver.find_elements(By.XPATH, self.models_xpath)
            count = len(cards)
            if count == last_count:
                break
            last_count = count

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                WebDriverWait(self.driver, 3).until(
                    lambda d: len(d.find_elements(By.XPATH, self.models_xpath)) > count
                )
            except:
                break

    # Detect capabilities
    def detect_capabilities(self):
        self.scroll_to_bottom()
        cards = self.driver.find_elements(By.XPATH, self.models_xpath)

        tags = set()
        for card in cards:
            spans = card.find_elements(By.CSS_SELECTOR, "div.flex div span")
            for span in spans:
                t = span.text.strip()
                if t and not any(c.isdigit() for c in t) and t.lower() != "latest":
                    tags.add(t)

        if self.KNOWN_CAPABILITIES:
            new_caps = tags - self.KNOWN_CAPABILITIES
            if new_caps:
                print(f"⚠ New capabilities detected: {new_caps}")

        self.KNOWN_CAPABILITIES = tags
        print(f"✅ Detected {len(tags)} capabilities")

    def save_data(self, data):
        data_dir = os.path.join(os.path.dirname(os.getcwd()), "../src/ollama_library/data")
        os.makedirs(data_dir, exist_ok=True)
        save_json(data, os.path.join(data_dir, "ollama_library.json"))
        save_csv(data, os.path.join(data_dir, "ollama_library.csv"))
        print(f"Archived {len(data)} models.")

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    scraper = OllamaScraperHybrid(headless=False)
    # print(scraper.KNOWN_CAPABILITIES)
    try:
        scraper.open_library()
        print(scraper.KNOWN_CAPABILITIES)

    #     # all_models = scraper.get_all_models()
    #     # print(f"Total models found: {all_models[0]}")
    #     # print(f"Model names: {all_models[1][:10]}")  # Print first 10 model names for verification
    #     data = scraper.get_all_models_info()
    #     scraper.save_data(data)
    finally:
        scraper.close()