from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  """Application settings."""

  app_name: str = "FastAPI Application"
  database_url: str = "sqlite:///./dev.db"
  OPENROUTER_API_KEY: str
  TAVILY_API_KEY: str

  model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
