from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from langgraph_skills.constants import RetentionPolicy


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenRouter credentials and model settings
    openrouter_api_key: str = ""
    openrouter_api_base: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-4o-mini"

    # Context Engineering: Skill Retention Policy
    # Options: "auto_evict" (default), "ephemeral", "manual"
    skill_retention_policy: RetentionPolicy = RetentionPolicy.AUTO_EVICT
    max_active_skills: int = 1


@lru_cache
def get_config() -> Config:
    return Config()
