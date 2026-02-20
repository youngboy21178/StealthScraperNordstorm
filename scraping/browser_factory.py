from playwright.async_api import async_playwright


class BrowserFactory:

    def __init__(self, headless: bool, cookies_manager):
        self.headless = headless
        self.cookies_manager = cookies_manager

    async def create(self):

        playwright = await async_playwright().start()

        browser = await playwright.chromium.launch(
            headless=self.headless
        )

        context = await browser.new_context()

        # Завантаження cookies
        cookies = self.cookies_manager.load()
        if cookies:
            await context.add_cookies(cookies)

        return browser, context