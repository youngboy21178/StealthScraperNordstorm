import logging
from config.settings import BrowserSettings
from camoufox.async_api  import AsyncCamoufox
from infrastructure.storage.cookies_manager import CookiesManager
from browserforge.fingerprints import Screen


class BrowserFactory:
    def __init__(
            self,
            browser_settings: BrowserSettings,
            cookies_manager: CookiesManager
        ):
        self.settings = browser_settings
        self.cookies_manager = cookies_manager
        self.logger = logging.getLogger(__name__)
        
        
        self._browser = None
        self._context = None
        
    async def create(self):
        """
        Method 1 (Create): Physically launches the browser and creates a context.
        Called ONCE at the start of the programme.
        """
        if self._browser is not None:
            self.logger.warning("Browser is already running!")
            return
    
        launch_config = {
            "headless": self.settings.headless,
            "os": self.settings.os,
            "screen": 
                Screen(
                    max_width=self.settings.window_width,
                    max_height=self.settings.window_height
                ),
            "webgl_config": 
                (
                    self.settings.webgl_vendor,
                    self.settings.webgl_renderer
                ),
            "humanize": self.settings.humanize,
            "locale": self.settings.locale
            
        }

        self._browser = await AsyncCamoufox(**launch_config).start()
        self.logger.info("Browser instance created.")

        if self.cookies_manager.has_cookies():
            self._context = await self._browser.new_context(
                storage_state=self.cookies_manager.cookies_path
            )
            self.logger.info("Context created WITH cookies.")
        else:
            self._context = await self._browser.new_context()
            self.logger.info("Context created WITHOUT cookies.")
        
    async def get_page(self):
        """
        Method 2 (Get): Returns a new tab (page) and context.
        Can be called MANY TIMES for different tasks.
        """
        if self._context is None:
            raise RuntimeError("Browser is not started! Call start() before get_page().")
            
        page = await self._context.new_page()
        return page, self._context

    async def stop(self) -> None:
        """
        Method 3 (Destroy): Correctly closes all resources.
        Called ONCE at the end of the programme.
        """
        if self._context:
            await self._context.close()
            self.logger.debug("Context closed.")
            
        if self._browser:
            await self._browser.close()
            self.logger.info("Browser safely closed.")