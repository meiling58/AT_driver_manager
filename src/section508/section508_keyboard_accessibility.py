from src.driver_manager.manager import driver_context


def test_keyboard_navigation(url):
    """Checks where focus lands after initial tabs."""
    with driver_context(engine="playwright", browser="chromium", headless=False) as (p, b, c, page):
        print(f"\n--- Testing Keyboard Nav on: {url} ---")
        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Start with a click on the body to ensure focus is at the top
        page.click("body")

        for i in range(1, 6):  # Tab 5 times to see the flow
            page.keyboard.press("Tab")
            focused_tag = page.evaluate("document.activeElement.tagName")
            focused_text = page.evaluate("document.activeElement.innerText").strip() or "[No Text]"
            print(f"Tab {i}: Focus on <{focused_tag}> | Text: '{focused_text}'")


def check_for_keyboard_trap(url, max_tabs=30):
    """Navigates a page to see if focus gets 'stuck' in a loop or single element."""
    with driver_context(engine="playwright", browser="chromium", headless=False) as (p, b, c, page):
        print(f"\n--- Checking for Keyboard Traps on: {url} ---")
        page.goto(url)
        page.wait_for_load_state("networkidle")

        history = []

        for i in range(max_tabs):
            page.keyboard.press("Tab")
            # Use outerHTML to uniquely identify the element
            current_el_html = page.evaluate("document.activeElement.outerHTML")

            # 508 Check: If we see the same element twice in a row, it's a trap
            if history and current_el_html == history[-1]:
                print(f"!!! KEYBOARD TRAP DETECTED at Tab {i} !!!")
                print(f"Stuck on: {current_el_html[:100]}...")
                return True

            history.append(current_el_html)

        print("No immediate keyboard traps detected in first 30 tabs.")
        return False


# --- TEST RUNNER BLOCK ---
if __name__ == "__main__":
    # Test a government site (usually good nav)
    target_url = "https://www.section508.gov"

    # Run the focus test
    test_keyboard_navigation(target_url)

    # Run the trap test
    check_for_keyboard_trap(target_url)