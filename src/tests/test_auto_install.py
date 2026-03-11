import os
import time
import shutil

from src.driver_manager.auto_install import ensure_playwright_browsers


def test_auto_install():
    ensure_playwright_browsers()
    print("Auto-install check complete.")


if __name__ == "__main__":
    print("==== Test Goal ====")
    print("Confirm that missing browsers trigger auto-install.")
    check = input("Did you temporarily rename your Playwright browser folder? (yes/no): ").strip().lower()

    if check not in ("yes", "y"):
        print("Cannot test now. Please rename your Playwright browser folder first.")
        exit(0)

    print("\n===== Expected behavior =====")
    print("Playwright browsers missing. Installing...")
    print("Then downloads Chromium, Firefox, WebKit")
    print("Then prints: Auto-install check complete.")
    print("\nTest starting...\n")

    # Path to Playwright browser folder
    base_dir = os.path.expanduser("~")
    original_path = os.path.join(base_dir, "AppData", "Local", "ms-playwright")
    backup_path = original_path + "-backup"

    # Safety check
    if not os.path.exists(backup_path):
        print(f"Backup folder not found at: {backup_path}")
        print("Did you rename it correctly?")
        exit(0)

    start_time = time.time()
    test_auto_install()
    end_time = time.time()

    # Cleanup step
    print("\nCleaning up backup folder...")

    try:
        # If auto-install recreated ms-playwright, delete backup
        if os.path.exists(original_path):
            print("Playwright browsers reinstalled. Deleting backup folder...")
            shutil.rmtree(backup_path)
        else:
            # If auto-install failed, restore backup
            print("Auto-install did not recreate folder. Restoring backup...")
            os.rename(backup_path, original_path)

        print("Cleanup complete.")

    except Exception as e:
        print("Cleanup failed:", e)

    total_seconds = round(end_time - start_time, 2)
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60

    print("\n⏱ Test completed!")
    print(f"Total runtime: {minutes} minutes {seconds:.2f} seconds")
