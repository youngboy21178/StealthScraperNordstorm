import os
import logging

class CookiesManager:
    def __init__(self, cookies_path: str):
        self.cookies_path = cookies_path
        self.logger = logging.getLogger(__name__)

    def has_cookies(self) -> bool:
        """Check, if saved cookies exist"""
        return os.path.exists(self.cookies_path)

    async def save_cookies(self, context) -> None:
        """Save current browser state in file"""
        try:
            await context.storage_state(path=self.cookies_path)
            self.logger.debug("Cookies successfully saved.")
        except Exception as e:
            self.logger.error(f"Failed to save cookies: {e}")

    def clear_cookies(self) -> None:
        """Clear old cookies"""
        if self.has_cookies():
            os.remove(self.cookies_path)
            self.logger.info("Cookies cleared.")