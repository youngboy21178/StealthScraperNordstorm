import asyncio
import sys

from scraping.browser_factory import BrowserFactory
from scraping.base_scraper import Scraper
from infrastructure.storage.cookies_manager import CookiesManager
from infrastructure.logging.logging_config import setup_logging
from config.settings import Settings

class TestScraper(Scraper):
    async def scrape(self):
        await self.navigate()
        await asyncio.sleep(600)

async def main():
    settings = Settings.load()
    setup_logging(
        level=settings.logging.level,
        format=settings.logging.format,
    )
    

    cookies_manager = CookiesManager(settings.storage.cookies_file)

    browser_factory = BrowserFactory(
        browser_settings=settings.browser,
        cookies_manager=cookies_manager
    )

    await browser_factory.create()
    page, context = await browser_factory.get_page()

            
    try:

        scraper = TestScraper(
            settings=settings.scraper,
            page=page,
            context=context
        )
            
        await scraper.scrape()
            
    finally:
        await browser_factory.stop()

if __name__ == "__main__":
    asyncio.run(main())

