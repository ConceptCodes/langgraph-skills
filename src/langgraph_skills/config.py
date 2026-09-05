from pydantic_settings import BaseSettings
from functools import lru_cache

class Config(BaseSettings):
    class Config:
        env_file = ".env"

    # Openrouter
    openrouter_api_key: str
    openrouter_api_base: str
    openrouter_model: str



@lru_cache
def get_config() -> Config:
    return Config()
