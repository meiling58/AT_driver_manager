# driver_manager/proxy_manager.py
# usage: use it in playwright
# proxy = proxy_manager.get_random()
# browser = p.chromium.launch(
#     headless=headless,
#     proxy={"server": proxy} if proxy else None
# )


import random

class ProxyManager:
    def __init__(self, proxies=None):
        self.proxies = proxies or []

    def add(self, proxy):
        self.proxies.append(proxy)

    def get_random(self):
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def get_next(self):
        if not self.proxies:
            return None
        proxy = self.proxies.pop(0)
        self.proxies.append(proxy)
        return proxy


GLOBAL_PROXY_MANAGER = ProxyManager()
