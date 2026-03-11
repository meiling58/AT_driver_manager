# driver_manager/concurrency.py
# usage: gives massive speed
# import asyncio
# from concurrency import run_many
#
# results = asyncio.run(run_many(urls))

import asyncio
from playwright.async_api import async_playwright


async def fetch_page(url, headless=True):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url)
        title = await page.title()

        await browser.close()
        return url, title


async def run_concurrent(urls, headless=True):
    tasks = [fetch_page(url, headless) for url in urls]
    return await asyncio.gather(*tasks)


async def run_task(url, headless=True):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        html = await page.content()
        await browser.close()
        return html


async def run_many(urls, headless=True):
    tasks = [run_task(url, headless) for url in urls]
    return await asyncio.gather(*tasks)