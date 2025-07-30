"""Configuration management using Pydantic."""
from pydantic import BaseSettings, Field
from dotenv import load_dotenv
import os

load_dotenv()

class AppSettings(BaseSettings):
    """
    Pydantic model for application settings, loaded from environment variables.
    """
    discord_bot_token: str = Field(..., env="DISCORD_BOT_TOKEN")
    config_file_path: str = Field("data/server_configs.json", env="CONFIG_FILE_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
try:
    settings = AppSettings()
except Exception as e:
    # Fallback for when .env is missing
    import os
    from typing import Any
    
    class FallbackSettings:
        discord_bot_token: str = os.getenv("DISCORD_BOT_TOKEN", "")
        config_file_path: str = os.getenv("CONFIG_FILE_PATH", "data/server_configs.json")
    
    settings: Any = FallbackSettings()

