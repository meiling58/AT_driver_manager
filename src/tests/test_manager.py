from src.driver_manager.manager import driver_context

# 1. Test with Playwright (Default)
with driver_context(browser="webkit", device_name="iPhone 14") as driver:
    p, browser, context, page = driver
    page.goto("https://www.section508.gov")
    print(f"Playwright WebKit Title: {page.title()}")

# 2. Test with Selenium (Explicit)
with driver_context(engine="selenium", browser="chrome", device_name="iPhone X") as driver:
    driver.get("https://www.section508.gov")
    print(f"Selenium Chrome Title: {driver.title}")

# 3 Test with Playwright/chrome
with driver_context(engine="playwright", browser="chrome") as driver:
    p, b, c, page = driver
    page.goto("https://www.section508.gov")
    print(f"Playwright chrome Title: {page.title()}")
