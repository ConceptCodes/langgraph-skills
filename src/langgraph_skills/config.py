from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenRouter credentials and model settings
    openrouter_api_key: str = ""
    openrouter_api_base: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-4o-mini"


@lru_cache
def get_config() -> Config:
    return Config()
