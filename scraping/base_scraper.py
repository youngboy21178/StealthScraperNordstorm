#base/scraper/scraper.py
import logging, asyncio, random
from abc import ABC, abstractmethod
from playwright.async_api import BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

class Scraper : 
        """
        Base scraper class
        """
        def __init__(
                self,
                url : str,
                page: Page,
                context: BrowserContext,
                timeout_ms: int
            ): 
            self.timeout_ms = timeout_ms
            self.url = url
            self.page = page
            self.context = context
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
                
                await self.random_delay(0.3, 0.8)
        
        async def random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0) -> None:
            """Makes a random pause."""
            delay = random.uniform(min_sec, max_sec)
            self.logger.debug(f"Sleeping for {delay:.2f} seconds...")
            await asyncio.sleep(delay)