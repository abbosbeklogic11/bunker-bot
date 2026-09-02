"""
Bot settings loaded from environment variables via pydantic-settings or os.environ fallback.
"""
from __future__ import annotations
from typing import Any, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from pydantic import field_validator
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        """Application-wide settings resolved from .env / environment."""

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )

        BOT_TOKEN: str = ""
        DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/bunker_db"
        REDIS_URL: str = "redis://localhost:6379/0"
        ADMIN_IDS: list[int] = []

        @field_validator("ADMIN_IDS", mode="before")
        @classmethod
        def parse_admin_ids(cls, v: Any) -> list[int]:
            if isinstance(v, str):
                return [int(x.strip()) for x in v.split(",") if x.strip()]
            if isinstance(v, (list, tuple)):
                return [int(x) for x in v]
            return []

        DEBUG: bool = False
        LOG_LEVEL: str = "INFO"

        WEBHOOK_URL: Optional[str] = None
        WEBHOOK_PATH: str = "/webhook"
        WEB_SERVER_HOST: str = "0.0.0.0"
        WEB_SERVER_PORT: int = 8080

        @property
        def webhook_enabled(self) -> bool:
            return bool(self.WEBHOOK_URL)

        @property
        def full_webhook_url(self) -> Optional[str]:
            if self.WEBHOOK_URL:
                return f"{self.WEBHOOK_URL.rstrip('/')}{self.WEBHOOK_PATH}"
            return None

    settings = Settings()

except ImportError:
    class SettingsFallback:
        def __init__(self):
            self.BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
            self.DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bunker_db")
            self.REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            
            admin_raw = os.getenv("ADMIN_IDS", "")
            self.ADMIN_IDS: list[int] = [int(x.strip()) for x in admin_raw.split(",") if x.strip()]
            
            self.DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
            self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
            self.WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL")
            self.WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/webhook")
            self.WEB_SERVER_HOST: str = os.getenv("WEB_SERVER_HOST", "0.0.0.0")
            self.WEB_SERVER_PORT: int = int(os.getenv("WEB_SERVER_PORT", "8080"))

        @property
        def webhook_enabled(self) -> bool:
            return bool(self.WEBHOOK_URL)

        @property
        def full_webhook_url(self) -> Optional[str]:
            if self.WEBHOOK_URL:
                return f"{self.WEBHOOK_URL.rstrip('/')}{self.WEBHOOK_PATH}"
            return None

    settings = SettingsFallback()
