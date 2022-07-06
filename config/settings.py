from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    telegram_key: str = Field("", env="TELEGRAM_KEY")

    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"
        
