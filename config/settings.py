import yaml
import os
from pydantic import BaseModel


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CURRENT_DIR, "settings.yaml")


class ScraperSettings(BaseModel):
    base_url: str
    start_url: str
    timeout_ms: int
    min_default_delay_sec: int
    max_default_delay_sec: int
    max_retries: int

class DatabaseSettings(BaseModel):
    db_name: str
    schema_file: str

class StorageSettings(BaseModel):
    cookies_file: str
    state_file: str

class LoggingSettings(BaseModel):
    level: str
    format: str

class BrowserSettings(BaseModel):
    headless: bool
    os: str
    webgl_vendor: str
    webgl_renderer: str
    humanize: bool
    locale: str
    window_width: int
    window_height: int


class Settings(BaseModel):
    scraper: ScraperSettings
    database: DatabaseSettings
    storage: StorageSettings
    logging: LoggingSettings
    browser: BrowserSettings

    @classmethod
    def load(cls, config_path: str = CONFIG_PATH) -> "Settings":
        """Read YAML and validate it using Pydantic"""
        with open(config_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
            

        return cls(**raw_data)