from typing import Type
from scraping.browser_factory import BrowserFactory
from config.settings import ScraperSettings
from scraping.base_scraper import Scraper


class ScrapingService:
    def __init__(
            self,
            repository,
            browser_factory: BrowserFactory, 
            scraper_class: Type[Scraper],  
            scraper_settings: ScraperSettings
        ):
        self.browser_factory = browser_factory
        self.scraper_class = scraper_class
        self.repository = repository
        self.scraper_settings = scraper_settings


    async def run(self):
        await self.browser_factory.create()
        page, context = await self.browser_factory.get_page()
        
        try:

            scraper = self.scraper_class(
                settings=self.scraper_settings,
                page=page,
                context=context
            )
            
            products = await scraper.scrape()
            
            if products:
                self.repository.save_all(products)
            

            await self.browser_factory.cookies_manager.save(context)

        finally:
            await self.browser_factory.stop()