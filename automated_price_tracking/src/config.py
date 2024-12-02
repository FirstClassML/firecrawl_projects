from pydantic_settings import BaseSettings
from typing import Dict


class Settings(BaseSettings):
    FIRECRAWL_API_KEY: str
    DISCORD_WEBHOOK_URL: str
    PRICE_DROP_THRESHOLD: float = 0.05  # Minimum price drop percentage

    class Config:
        env_file = ".env"


settings = Settings()
