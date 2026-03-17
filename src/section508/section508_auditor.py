import json
from axe_playwright_python.sync_playwright import Axe
from src.driver_manager.manager import driver_context


class Section508Auditor:
    def __init__(self, url):
        self.url = url
        self.results = {
            "url": url,
            "axe_violations": [],
            "empty_links": [],
            "keyboard_trap": False,
            "focus_path": []
        }

    def run_all_tests(self, headless=True):
        """Orchestrates all 508 checks in a single session."""
        with driver_context(engine="playwright", browser="chromium", headless=headless) as (p, b, c, page):
            print(f"🚀 Starting Full 508 Audit for: {self.url}")
            page.goto(self.url)
            page.wait_for_load_state("networkidle")

            # 1. Run Automated Axe Scan
            print("  - Running Axe-core scan...")
            axe_results = Axe().run(page)
            self.results["axe_violations"] = axe_results.response.get("violations", [])

            # 2. Check for Empty Links
            print("  - Checking for empty links...")
            self._check_links(page)

            # 3. Check for Keyboard Traps & Path
            print("  - Testing keyboard navigation...")
            self._check_keyboard(page)

            print("✅ Audit Complete.")
            return self.results

    def _check_links(self, page):
        links = page.locator("a").all()
        for link in links:
            text = link.inner_text().strip()
            aria = link.get_attribute("aria-label")
            if not text and not aria:
                self.results["empty_links"].append(link.get_attribute("href") or "N/A")

    def _check_keyboard(self, page, max_tabs=20):
        page.click("body")  # Reset focus
        history = []
        for i in range(max_tabs):
            page.keyboard.press("Tab")

            # SAFE EVALUATE: Check if el exists before accessing properties
            el_info = page.evaluate("""() => {
                const el = document.activeElement;
                if (!el) return { tag: "NONE", text: "", html: "" };
                return { 
                    tag: el.tagName || "UNKNOWN", 
                    text: (el.innerText || "").trim(), 
                    html: el.outerHTML || "" 
                };
            }""")

            # Record focus path
            self.results["focus_path"].append({"step": i + 1, "tag": el_info["tag"], "text": el_info["text"]})

            # Trap detection - only check if we actually have HTML to compare
            if el_info["html"] and history and el_info["html"] == history[-1]:
                self.results["keyboard_trap"] = True
                print(f"!!! KEYBOARD TRAP DETECTED at step {i + 1} !!!")
                break

            history.append(el_info["html"])

    def export_report(self, filename="audit_report.json"):
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=4)
        print(f"📄 Report saved to {filename}")


# --- Execution ---
if __name__ == "__main__":
    auditor = Section508Auditor("https://www.section508.gov")
    # auditor = Section508Auditor("https://www.dequeuniversity.com/demo/mars/")
    report = auditor.run_all_tests(headless=False)
    auditor.export_report()
