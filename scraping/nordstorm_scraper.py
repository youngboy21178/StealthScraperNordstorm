import asyncio, re
from core.exceptions import OpenSalePageException, ProductsNotFound
from core.models import Product

from scraping.base_scraper import Scraper

class NordstromScraper(Scraper):
    async def scrape(self) :
        pass
    async def open_sale_page(self, try_count: int = 3) -> None:
        if try_count <= 0: 
            raise OpenSalePageException

        await self.page.get_by_role("button", name="Sale", exact=True).click()
        self.logger.debug("The 'Sale' button was pressed")
        
        for attempt in range(try_count):
            try:
                await asyncio.sleep(1) 
                
                link = self.page.get_by_role("link", name="Under $50", exact=True)
                
                await link.hover()
                await asyncio.sleep(0.4)
                
                await link.click()
                self.logger.debug(f"The 'Under $50' link was pressed (attempt {attempt + 1})")
                break 
                
            except Exception as e:
                self.logger.warning(f"Failed to press 'Under $50' link on attempt {attempt + 1}. Exception: {e}")
                
                if attempt == try_count - 1:
                    self.logger.error("Failed to click the link after all attempts.")
                    raise OpenSalePageException
                
                self.logger.info("Retrying...")
                await asyncio.sleep(2)

        self.logger.debug("5 seconds delay")
        await asyncio.sleep(5)
    
    async def choose_filters(self): 
        await self.check_products_loaded()
        await self.page.get_by_role("button", name="Filter", exact=True).click()
        self.logger.debug("The 'Filter' button was pressed")
        await self.page.get_by_role("button", name="Gender", exact=True).click()
        self.logger.debug("The 'Gender' button was pressed")
        await self.page.get_by_role("button", name="Boys", exact=True).click()
        self.logger.debug("The 'Boys' button was pressed")

        await self.page.get_by_role("button", name="Product Type", exact=True).click()
        self.logger.debug("The 'Product Type' button was pressed")
        await self.page.get_by_label("Product Type").get_by_role("button", name="Shoes", exact=True).click()
        self.logger.debug("The 'Shoes' button was pressed")
        await self.page.get_by_role("button", name="All Shoes", exact=True).click()
        self.logger.debug("The 'All Shoes' button was pressed")

        await self.page.get_by_role("button", name="View Results", exact=True).click()
        self.logger.debug("The 'View Results' button was pressed")

    
    async def check_products_loaded(self) -> bool:
        self.logger.info("Checking if products are loaded...")
        products_locator = self.page.locator('div[data-container-type="product-grid"] article')
        
        try:
            await products_locator.first.wait_for(state="visible", timeout=10000)
        except Exception:
            self.logger.warning("Timeout waiting for products to appear.")

        items_count = await products_locator.count()
        self.logger.debug(f"Found {items_count} product items.")

        if items_count > 0:
            self.logger.info("Products loaded successfully! Proceeding to filters.")
            return True
        else:
            self.logger.warning("No products found! Reloading the page...")
            await self.page.get_by_role("button", name="Top", exact=True).click()
            await asyncio.sleep(5) 
            return False
    
    async def scrap_products(self) -> list[ProductDTO]:
        if not await self.check_products_loaded(): 
            raise ProductsNotFound

        products_locator = self.page.locator('div[data-container-type="product-grid"] article')
        items = await products_locator.all()

        products: list[ProductDTO] = [] 

        for item in items:
            title_element = item.locator("h3 a")
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

    async def _get_price(self, item: Locator)-> tuple[float, float, str]:
        price_element = item.get_by_text(re.compile("Current Price", re.IGNORECASE))
        if await price_element.count() > 0:
            raw_price = await price_element.first.inner_text()
            price_text = raw_price.replace("Current Price", "").strip()
        else:
            fallback_price = item.locator("span", has_text=re.compile(r"\d+[,.]\d{2}")).first
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
        color_buttons = await item.locator("ul li button[aria-label]").all()
        
        colors = []
        for btn in color_buttons:
            color_name = await btn.get_attribute("aria-label")
            if color_name:
                colors.append(color_name)
                
        return colors