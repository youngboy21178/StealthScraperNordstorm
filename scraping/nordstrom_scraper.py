import asyncio
import re
from playwright.async_api import Locator

from core.exceptions import OpenSalePageException, ProductsNotFound
from core.models import Product
from scraping.base_scraper import Scraper
from scraping.selectors import NordstromSelectors 

class NordstromScraper(Scraper):
    
    async def scrape(self) -> list[Product]:
        """
        The main method required by the base class.
        It combines verification and data collection.
        """
        if not await self.check_products_loaded(): 
            raise ProductsNotFound

        products_locator = self.page.locator(NordstromSelectors.PRODUCT_GRID_ARTICLE)
        items = await products_locator.all()

        products: list[Product] = [] 

        for item in items:
            title_element = item.locator(NordstromSelectors.PRODUCT_TITLE_LINK)
            if await title_element.count() > 0:
                title = await title_element.first.inner_text()
                link = await title_element.first.get_attribute("href")
            else:
                title = "Undefined Name"
                link = ""

            min_price, max_price, valute = await self._get_price(item)
            colors = await self._get_colors(item)
            
            products.append(
                Product(
                    title=title,
                    link=link,
                    max_price=max_price,
                    min_price=min_price,
                    valute=valute,
                    colors=colors,
                )
            )
            
        return products

    async def open_sale_page(self, try_count: int = 3) -> None:
        if try_count <= 0: 
            raise OpenSalePageException

        await self.page.get_by_role("button", name=NordstromSelectors.BTN_SALE, exact=True).click()
        self.logger.debug("The 'Sale' button was pressed")
        
        for attempt in range(try_count):
            try:
                await self.random_delay(1.0, 1.5) 
                
                link = self.page.get_by_role("link", name=NordstromSelectors.LINK_UNDER_50, exact=True)
                await link.hover()
                await self.random_delay(0.4, 0.6)
                
                await link.click()
                self.logger.debug(f"The 'Under $50' link was pressed (attempt {attempt + 1})")
                break 
                
            except Exception as e:
                self.logger.warning(f"Failed to press 'Under $50' link on attempt {attempt + 1}. Exception: {e}")
                
                if attempt == try_count - 1:
                    self.logger.error("Failed to click the link after all attempts.")
                    raise OpenSalePageException
                
                self.logger.info("Retrying...")
                await self.random_delay(2.0, 2.5)

        self.logger.debug("Waiting after clicking the link...")
        await self.random_delay(4.0, 6.0)
    
    async def choose_filters(self) -> None: 
        await self.check_products_loaded()
        
        await self.page.get_by_role("button", name=NordstromSelectors.BTN_FILTER, exact=True).click()
        self.logger.debug("The 'Filter' button was pressed")
        
        await self.page.get_by_role("button", name=NordstromSelectors.BTN_GENDER, exact=True).click()
        self.logger.debug("The 'Gender' button was pressed")
        
        await self.page.get_by_role("button", name=NordstromSelectors.BTN_BOYS, exact=True).click()
        self.logger.debug("The 'Boys' button was pressed")

        await self.page.get_by_role("button", name=NordstromSelectors.BTN_PRODUCT_TYPE, exact=True).click()
        self.logger.debug("The 'Product Type' button was pressed")
        
        await self.page.get_by_label(NordstromSelectors.LBL_PRODUCT_TYPE).get_by_role("button", name=NordstromSelectors.BTN_SHOES, exact=True).click()
        self.logger.debug("The 'Shoes' button was pressed")
        
        await self.page.get_by_role("button", name=NordstromSelectors.BTN_ALL_SHOES, exact=True).click()
        self.logger.debug("The 'All Shoes' button was pressed")

        await self.page.get_by_role("button", name=NordstromSelectors.BTN_VIEW_RESULTS, exact=True).click()
        self.logger.debug("The 'View Results' button was pressed")
    
    async def check_products_loaded(self) -> bool:
        self.logger.info("Checking if products are loaded...")
        products_locator = self.page.locator(NordstromSelectors.PRODUCT_GRID_ARTICLE)
        
        try:
            await products_locator.first.wait_for(state="visible", timeout=10000)
        except Exception:
            self.logger.warning("Timeout waiting for products to appear.")

        items_count = await products_locator.count()
        self.logger.debug(f"Found {items_count} product items.")

        if items_count > 0:
            self.logger.info("Products loaded successfully! Proceeding.")
            return True
        else:
            self.logger.warning("No products found! Reloading the page...")
            await self.page.get_by_role("button", name=NordstromSelectors.BTN_TOP, exact=True).click()
            await self.random_delay(4.0, 6.0) 
            return False
            
    async def _get_price(self, item: Locator) -> tuple[float, float, str]:
        price_element = item.get_by_text(re.compile(NordstromSelectors.PRICE_CURRENT_TEXT, re.IGNORECASE))
        
        if await price_element.count() > 0:
            raw_price = await price_element.first.inner_text()
            price_text = re.sub(NordstromSelectors.PRICE_CURRENT_TEXT, "", raw_price, flags=re.IGNORECASE).strip()
        else:
            fallback_price = item.locator(NordstromSelectors.PRICE_FALLBACK_TAG, has_text=NordstromSelectors.PRICE_FALLBACK_REGEX).first
            if await fallback_price.count() > 0:
                price_text = await fallback_price.inner_text()
            else:
                price_text = ""

        if price_text:
            numbers = re.findall(r"[\d.,]+", price_text)
            symbols_only = re.sub(r"[\d\s.,a-zA-Z\-]", "", price_text)
            valute = symbols_only[0] if symbols_only else ""

            if len(numbers) >= 2:
                min_price = float(numbers[0].replace(",", "."))
                max_price = float(numbers[-1].replace(",", "."))
            elif len(numbers) == 1:
                min_price = float(numbers[0].replace(",", "."))
                max_price = min_price
            else:
                min_price = max_price = 0.0
        else:
            min_price = max_price = 0.0
            valute = ""
            
        return min_price, max_price, valute

    async def _get_colors(self, item: Locator) -> list[str]:
        color_buttons = await item.locator(NordstromSelectors.COLOR_BUTTONS).all()
        
        colors = []
        for btn in color_buttons:
            color_name = await btn.get_attribute("aria-label")
            if color_name:
                colors.append(color_name)
                
        return colors