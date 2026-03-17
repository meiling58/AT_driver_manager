from src.driver_manager.manager import driver_context
from axe_playwright_python.sync_playwright import Axe


def run_508_scan(url):
    with driver_context(engine="playwright", browser="chromium", headless=False) as (playwright, browser, context,
                                                                                     page):
        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Axe().run() returns an AxeResults object
        results = Axe().run(page)

        # ACCESS THE DATA VIA THE .response ATTRIBUTE
        raw_data = results.response
        violations = raw_data.get("violations", [])

        print(f"Found {len(violations)} Section 508 violations on {url}")

        for v in violations:
            # Since raw_data is a dictionary, use dictionary access here
            print(f"ID: {v['id']} - Description: {v['description']}")
            print(f"Impact: {v['impact']} | Help: {v['helpUrl']}\n")

def run_standalone_audit(url):
    # set headless=False will see the page show when run the code
    with driver_context(engine="playwright", browser="chrome", headless=False) as (playwright, browser, context, page):
        print("Navigating to target...")
        page.goto(url)
        page.wait_for_load_state("networkidle")

        # This library handles the dictionary context correctly
        results = Axe().run(page, context=None, options={"runOnly": ["section508"]})
        print(results)

        print(f"--- Audit Complete ---")

        print(f"Violations found: {results.violations_count}")

def test_keyboard_navigation(url):
    with driver_context(engine="playwright", browser="chromium") as (playwright, browser, context, page):
        page.goto(url)

        # 1. Press Tab multiple times
        for _ in range(3):
            page.keyboard.press("Tab")

        # 2. Check which element is currently focused
        # This is a 'Pro' check for Section 508
        focused_element_tag = page.evaluate("document.activeElement.tagName")
        focused_text = page.evaluate("document.activeElement.innerText")

        print(f"Current Focus is on: <{focused_element_tag}> with text: '{focused_text}'")


def find_all_empty_links(url):
    with driver_context(engine="playwright", browser="chromium") as (p, b, c, page):
        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Get all anchor tags
        links = page.locator("a").all()
        empty_links_found = 0

        print(f"--- Scanning {len(links)} links on {url} ---")

        for link in links:
            # 1. Get visible text
            text = link.inner_text().strip()

            # 2. Get accessible attributes
            aria_label = link.get_attribute("aria-label")
            aria_labelledby = link.get_attribute("aria-labelledby")
            title = link.get_attribute("title")

            # 3. Check for internal images with alt text
            has_alt_img = False
            img_locator = link.locator("img")
            if img_locator.count() > 0:
                # Check if ANY image inside the link has alt text
                for img in img_locator.all():
                    if img.get_attribute("alt"):
                        has_alt_img = True

            # If ALL of these are missing, it's an empty link
            if not text and not aria_label and not aria_labelledby and not title and not has_alt_img:
                empty_links_found += 1
                href = link.get_attribute("href") or "No Href"
                html = link.evaluate("el => el.outerHTML")

                print(f"FAILURE {empty_links_found}: Empty Link Detected!")
                print(f"  - Href: {href}")
                print(f"  - Raw HTML: {html[:100]}...")  # Print first 100 chars
                print("-" * 30)

        if empty_links_found == 0:
            print("Great news: All links have an accessible name!")


# Use your manager to audit a site
test_url1 = "https://www.section508.gov"
test_url2 = "https://google.com"
test_url3 = "https://www.dequeuniversity.com/demo/mars/"
# run_508_scan(test_url1)
# run_508_scan("https://example-gov-site.gov")
# run_standalone_audit(test_url1)
# run_standalone_audit(test_url2)
# run_508_scan(test_url1)
# run_508_scan(test_url3)
# run_508_scan(test_url2)
# test_keyboard_navigation(test_url1)
# test_keyboard_navigation(test_url2)
# test_keyboard_navigation(test_url3)
find_all_empty_links(test_url1)