from langchain_openai import ChatOpenAI

from langgraph_skills.config import get_config


def get_llm(api_key: str = None, model: str = None, base_url: str = None) -> ChatOpenAI:
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


# Default module-level instance for convenience
config = get_config()
llm_model = ChatOpenAI(
    api_key=config.openrouter_api_key or "dummy-key-for-init",
    base_url=config.openrouter_api_base,
    model=config.openrouter_model,
    default_headers={
        "X-Title": "langgraph-skills",
        "HTTP-Referer": "https://github.com/davidojo/langgraph-skills",
    },
)
