import asyncio
from playwright.async_api import async_playwright

async def test_block():
    print("We launch a regular bot (without protection)...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("Let's go to the Nordstrom website...")
        await page.goto("https://www.nordstrom.com")

        print("Let's see the result (Akamai should block access)...")
        print("You have 15 seconds to take a screenshot of 'Access Denied'!")
        await asyncio.sleep(1500) 

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_block())