# driver_manager/auto_select_driver_manager.py

import json
import os
from pathlib import Path
from src.driver_manager.manager import get_driver, driver_context

# This finds the absolute path to /src/driver_manager/
CURRENT_DIR = Path(__file__).parent
BENCHMARK_FILE = CURRENT_DIR / "browser_benchmark.json"

def get_recommended_config():
    """Reads the latest benchmark from the fixed location."""
    if not BENCHMARK_FILE.exists():
        print(f"⚠️ Benchmark not found at {BENCHMARK_FILE}. Using defaults.")
        return {"engine": "playwright", "browser": "firefox"}

    try:
        with open(BENCHMARK_FILE, "r") as f:
            data = json.load(f)
            return data.get("overall_best_config", {"engine": "playwright", "browser": "firefox"})
    except Exception as e:
        print(f"⚠️ Error reading benchmark: {e}")
        return {"engine": "playwright", "browser": "firefox"}


def get_auto_driver(**overrides):
    """
    Returns a driver based on the fastest benchmarked configuration.
    Example: driver = get_auto_driver(headless=False)
    """
    config = get_recommended_config()

    # Merge recommended config with any user overrides
    final_params = {
        "engine": config["engine"],
        "browser": config["browser"],
        "headless": True,
        "use_stealth": True
    }
    final_params.update(overrides)

    return get_driver(**final_params)


def auto_driver_context(**overrides):
    """
    Context manager version for the auto-selected driver.
    """
    config = get_recommended_config()
    final_params = {
        "engine": config["engine"],
        "browser": config["browser"]
    }
    final_params.update(overrides)

    return driver_context(**final_params)

if __name__ == "__main__":
    # print(get_recommended_config())
    # print(auto_driver_context(headless=False))
    print(get_auto_driver(headless=False))