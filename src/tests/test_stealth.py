import time

from archive.driver_manager import driver_context



def test_stealth():

    print(driver_context())

    with driver_context(engine="playwright", use_stealth=True) as d:
        p, browser, context, page = d

        page.goto("https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html")

        print("Page loaded. Check the results manually in the HTML output.")
        print(page.title())


if __name__ == "__main__":
    print(f"==== Test Goal ==== \nconfirm that stealth removes navigator.webdriver and masks fingerprints. ====")
    print(f"===== Expected behavior ====")
    print(f"navigator.webdriver = false")
    print(f"Headless detection byPassed")
    print(f"WebGL vendor spoofed")
    print(f"Plugins spoofed")
    print(f"\nTest starting.....\n")

    start_time = time.time()
    test_stealth()
    end_time = time.time()
    total_seconds = round(end_time - start_time, 2)
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60

    print("\n⏱ Test completed!")
    print(f"Total runtime: {minutes} minutes {seconds:.2f} seconds")


