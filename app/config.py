from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    gemini_api_key: str
    huggingface_api_token: str
    environment: str = "development"
    log_level: str = "INFO"
    app_name: str = "rag-triage-api"
    app_version: str = "0.1.0"
    domain: str = "health_and_social_care"


@lru_cache
def get_settings() -> Settings:
    return Settings()