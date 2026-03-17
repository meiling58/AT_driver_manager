from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Get all device names
    all_devices = p.devices.keys()

    # Sort and print them
    for device in sorted(all_devices):
        print(device)