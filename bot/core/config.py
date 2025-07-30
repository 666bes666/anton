
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

class AppSettings(BaseModel):
    """
    Pydantic model for application settings, loaded from environment variables.
    """
    discord_bot_token: str = Field(..., env="DISCORD_BOT_TOKEN")
    config_file_path: str = Field("data/server_configs.json", env="CONFIG_FILE_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = AppSettings()

