import asyncio

from services.scraping_service import ScrapingService
from scraping.browser_factory import BrowserFactory
from scraping.nordstrom_scraper import NordstromScraper
from infrastructure.database.connection import DatabaseConnection
from infrastructure.database.repositories import ProductRepository
from infrastructure.storage.cookies_manager import CookiesManager
from infrastructure.logging.logging_config import setup_logging
from config.settings import Settings


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

    # 4. Database
    db = DatabaseConnection(settings.db_path)
    repository = ProductRepository(db)

    # 5. Scraping service
    service = ScrapingService(
        browser_factory=browser_factory,
        scraper_class=NordstromScraper,
        repository=repository
    )

    await service.run()

    db.close()


if __name__ == "__main__":
    asyncio.run(main())