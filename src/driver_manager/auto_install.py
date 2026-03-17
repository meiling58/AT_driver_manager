import os
import shutil
import subprocess
import sys

def ensure_playwright_browsers():
    try:
        # Check for the browser directory directly
        base_dir = os.path.expanduser("~")
        possible_dir = os.path.join(base_dir, "AppData", "Local", "ms-playwright")

        if not os.path.exists(possible_dir):
            print("Playwright browsers missing. Installing...")
            # Use 'python -m playwright' instead of the naked 'playwright' command
            # This ensures it uses the version installed in your current venv
            subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
        else:
            # Silence the "Not found" message since we know browsers are there
            pass

    except Exception as e:
        print("Failed to auto-install Playwright browsers:", e)


# # driver_manager/auto_install.py
#
# import os
# import shutil
# import subprocess
#
# def ensure_playwright_browsers():
#     try:
#         if shutil.which("playwright") is None:
#             print("Playwright CLI not found.")
#             return
#
#         base_dir = os.path.expanduser("~")
#         possible_dir = os.path.join(base_dir, "AppData", "Local", "ms-playwright")
#
#         if not os.path.exists(possible_dir):
#             print("Playwright browsers missing. Installing...")
#             subprocess.run(["playwright", "install"], check=True)
#
#     except Exception as e:
#         print("Failed to auto-install Playwright browsers:", e)
