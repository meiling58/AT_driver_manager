# auto_tuner.py

import os
import json
import time
from dataclasses import dataclass
from statistics import mean

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from driver_manager import create_driver
# from manager import create_driver

BENCHMARK_FILE = "browser_benchmark.json"
TEST_URL = "https://ollama.com/library"


@dataclass
class AutoTuningReport:
    fastest_scrape_browser: str
    fastest_interaction_browser: str
    overall_best: str
    selenium_startup: dict
    navigation_speed: dict
    infinite_scroll: dict
    requests_speed: float
    timestamp: str


# ───────────────────────────────────────────────────────────────
# Utility: Save & Load Benchmark Cache
# ───────────────────────────────────────────────────────────────
def save_benchmark(data):
    with open(BENCHMARK_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_benchmark():
    if os.path.exists(BENCHMARK_FILE):
        with open(BENCHMARK_FILE, "r") as f:
            return json.load(f)
    return None


# ───────────────────────────────────────────────────────────────
# Benchmark: Selenium Startup Time
# ───────────────────────────────────────────────────────────────
def benchmark_selenium_startup(browser):
    times = []
    for _ in range(3):
        start = time.time()
        driver = create_driver(browser=browser, headless=True)
        driver.quit()
        times.append(time.time() - start)
    return round(mean(times), 3)


# ───────────────────────────────────────────────────────────────
# Benchmark: Navigation Speed
# ───────────────────────────────────────────────────────────────
def benchmark_navigation(browser):
    times = []
    for _ in range(3):
        driver = create_driver(browser=browser, headless=True)
        start = time.time()
        driver.get(TEST_URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "repo"))
        )
        times.append(time.time() - start)
        driver.quit()
    return round(mean(times), 3)


# ───────────────────────────────────────────────────────────────
# Benchmark: Infinite Scroll Speed
# ───────────────────────────────────────────────────────────────
def benchmark_infinite_scroll(browser):
    driver = create_driver(browser=browser, headless=True)
    wait = WebDriverWait(driver, 10)

    driver.get(TEST_URL)
    wait.until(EC.presence_of_element_located((By.ID, "repo")))

    scrolls = 0
    start = time.time()

    while time.time() - start < 5:  # 5-second test
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scrolls += 1

    driver.quit()
    return scrolls


# ───────────────────────────────────────────────────────────────
# Benchmark: Requests Speed
# ───────────────────────────────────────────────────────────────
def benchmark_requests():
    times = []
    for _ in range(3):
        start = time.time()
        requests.get(TEST_URL, timeout=10)
        times.append(time.time() - start)
    return round(mean(times), 3)


# ───────────────────────────────────────────────────────────────
# Main Benchmark Runner
# ───────────────────────────────────────────────────────────────
def benchmark_browsers():
    browsers = ["firefox", "chrome", "edge"]
    results = {
        "selenium_startup": {},
        "navigation_speed": {},
        "infinite_scroll": {},
    }

    print("\n🔧 Running browser benchmarks...\n")

    for browser in browsers:
        try:
            print(f"⏳ Benchmarking {browser} startup...")
            results["selenium_startup"][browser] = benchmark_selenium_startup(browser)

            print(f"⏳ Benchmarking {browser} navigation...")
            results["navigation_speed"][browser] = benchmark_navigation(browser)

            print(f"⏳ Benchmarking {browser} infinite scroll...")
            results["infinite_scroll"][browser] = benchmark_infinite_scroll(browser)

        except Exception as e:
            print(f"⚠ {browser} failed benchmark: {e}")

    print("\n⏳ Benchmarking requests...")
    req_speed = benchmark_requests()

    # Determine winners
    fastest_scrape = min(results["navigation_speed"], key=results["navigation_speed"].get)
    fastest_interaction = min(results["selenium_startup"], key=results["selenium_startup"].get)

    # Weighted overall score
    overall_scores = {}
    for browser in browsers:
        if browser not in results["selenium_startup"]:
            continue

        score = (
            results["selenium_startup"][browser] * 0.4 +
            results["navigation_speed"][browser] * 0.4 +
            (1 / max(results["infinite_scroll"][browser], 1)) * 0.2
        )
        overall_scores[browser] = score

    overall_best = min(overall_scores, key=overall_scores.get)

    report = AutoTuningReport(
        fastest_scrape_browser=fastest_scrape,
        fastest_interaction_browser=fastest_interaction,
        overall_best=overall_best,
        selenium_startup=results["selenium_startup"],
        navigation_speed=results["navigation_speed"],
        infinite_scroll=results["infinite_scroll"],
        requests_speed=req_speed,
        timestamp=time.ctime()
    )

    save_benchmark(report.__dict__)
    return report


# ───────────────────────────────────────────────────────────────
# Auto‑Select Browser
# ───────────────────────────────────────────────────────────────
def auto_select_browser(task_type="scrape"):
    cached = load_benchmark()
    if not cached:
        cached = benchmark_browsers().__dict__

    if task_type == "scrape":
        return cached["fastest_scrape_browser"]

    if task_type == "interaction":
        return cached["fastest_interaction_browser"]

    return cached["overall_best"]


# ───────────────────────────────────────────────────────────────
# CLI Runner
# ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    report = benchmark_browsers()
    print("\n📊 Auto‑Tuning Report:")
    print(json.dumps(report.__dict__, indent=4))
