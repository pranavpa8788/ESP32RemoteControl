import configparser
import ctypes
from time import sleep
import asyncio

from playwright.async_api import async_playwright

class StreamController:
    def __init__(self):
        pass

    async def init_browser(self, playwright):
        self.browser = await playwright.webkit.launch(headless=False)
        self.page = await self.browser.new_page()


    async def run(self, playwright):
        await self.init_browser(playwright)

        url_list = ['https://awish.pro/e/dttzss4mowrm', 'https://dood.wf/e/aodssu8m08zz', 'https://alions.pro/v/kk8d3lf1zh5e']

        for url in url_list:
            await self.page.goto(url)

            await self.browser.close()

    async def main(self):
        async with async_playwright() as playwright:
            await self.run(playwright)

if __name__ == "__main__":
    stream_controller = StreamController()
    asyncio.run(stream_controller.main())

# import asyncio
# from playwright.async_api import async_playwright, Playwright
#
# async def run(playwright: Playwright):
#     chromium = playwright.chromium # or "firefox" or "webkit".
#     browser = await chromium.launch(headless=False)
#     page = await browser.new_page()
#     await page.goto("http://example.com")
#     sleep(100)
#     # other actions...
#     await browser.close()
#
# async def main():
#     async with async_playwright() as playwright:
#         await run(playwright)
# asyncio.run(main())
