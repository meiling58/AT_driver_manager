import asyncio
from .browser_pool import BrowserPool


async def fetch_with_pool(pool: BrowserPool, url: str):
    ctx = await pool.get_context()
    page = await ctx.new_page()
    await page.goto(url)
    title = await page.title()
    await page.close()
    return url, title


async def run_with_pool(urls, pool_size=3, headless=True):
    pool = BrowserPool(size=pool_size, headless=headless)
    await pool.init()

    try:
        tasks = [fetch_with_pool(pool, url) for url in urls]
        return await asyncio.gather(*tasks)
    finally:
        await pool.close()
