import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "FastAPI Application"
    database_url: str = "sqlite:///./dev.db"
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
