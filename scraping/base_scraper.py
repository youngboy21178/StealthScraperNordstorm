#base/scraper/scraper.py
import logging, asyncio, random
from abc import ABC, abstractmethod
from playwright.async_api import BrowserContext, Page, TimeoutError as PlaywrightTimeoutError
from config.settings import ScraperSettings

class Scraper : 
        """
        Base scraper class
        """
        def __init__(
                self, 
                settings: ScraperSettings,
                page: Page,
                context: BrowserContext
            ): 
            self.min_default_delay_sec = settings.min_default_delay_sec
            self.max_default_delay_sec = settings.min_default_delay_sec
            self.url = settings.start_url
            self.page = page
            self.context = context
            self.max_retries = settings.max_retries
            self.logger = logging.getLogger(__name__)

        def __str__(self) -> str:
                return f"Scraper(url='{self.url}')"
        
        @abstractmethod
        async def scrape(self):
            """
            The main method that MUST be implemented in every child class.
            """
            pass

        
        async def navigate(self, timeout: int = 30000) -> bool:
            """
            Safe transition to the error handling page.
            """
            self.logger.info(f"Navigating to {self.url} ...")
            try:
                await self.page.goto(self.url, wait_until="domcontentloaded", timeout=timeout)
                return True
            except PlaywrightTimeoutError:
                self.logger.error(f"Timeout while navigating to {self.url}")
                return False
            except Exception as e:
                self.logger.error(f"Failed to navigate: {e}")
                return False
        
        async def scroll_gradually(self) -> None:
            """
            Smooth scrolling in sections to simulate human behaviour 
            and lazy loading of product cards.
            """
            self.logger.debug("Gradually scrolling down...")
            
            steps = random.randint(5, 7)
            for _ in range(steps):
                scroll_amount = random.randint(600, 900)
                await self.page.mouse.wheel(0, scroll_amount)
                
                await self.random_delay()
        
        async def random_delay(self, min_sec: float = 0, max_sec: float = 0) -> None:
            """Makes a random pause."""
            if min_sec == 0 and max_sec == 0 :
                min_sec, max_sec = self.min_default_delay_sec, self.max_default_delay_sec
            delay = random.uniform(min_sec, max_sec)
            self.logger.debug(f"Sleeping for {delay:.2f} seconds...")
            await asyncio.sleep(delay)