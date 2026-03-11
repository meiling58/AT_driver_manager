import asyncio
from playwright.async_api import async_playwright

class BrowserPool:
    def __init__(self, size=3, headless=True):
        self.size = size
        self.headless = headless
        self._playwright = None
        self._browsers = []
        self._contexts = []
        self._lock = asyncio.Lock()
        self._index = 0

    async def init(self):
        if self._playwright is not None:
            return

        self._playwright = await async_playwright().start()

        for _ in range(self.size):
            browser = await self._playwright.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            self._browsers.append(browser)
            self._contexts.append(context)

    async def get_context(self):
        async with self._lock:
            ctx = self._contexts[self._index]
            self._index = (self._index + 1) % self.size
            return ctx

    async def close(self):
        if self._playwright is None:
            return

        for ctx in self._contexts:
            await ctx.close()
        for browser in self._browsers:
            await browser.close()

        await self._playwright.stop()
        self._playwright = None
        self._browsers = []
        self._contexts = []
        self._index = 0
