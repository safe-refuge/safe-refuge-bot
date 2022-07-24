from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    telegram_key: str = Field("", env="TELEGRAM_KEY")
    google_api_key: str = Field("", env="GOOGLE_API_KEY")
    safe_refuge_root_url: str = Field("", env="SAFE_REFUGE_ROOT_URL")
    google_api_key: str = Field("", env="GOOGLE_API_KEY")

    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"
        
