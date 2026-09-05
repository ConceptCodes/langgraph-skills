from typing import Optional

from langchain_openai import ChatOpenAI

from langgraph_skills.config import get_config


def get_llm(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> ChatOpenAI:
    """Factory function to build a configured ChatOpenAI instance for OpenRouter."""
    config = get_config()
    return ChatOpenAI(
        api_key=api_key or config.openrouter_api_key or "dummy-key-for-init",
        base_url=base_url or config.openrouter_api_base,
        model=model or config.openrouter_model,
        default_headers={
            "X-Title": "langgraph-skills",
            "HTTP-Referer": "https://github.com/davidojo/langgraph-skills",
        },
    )
