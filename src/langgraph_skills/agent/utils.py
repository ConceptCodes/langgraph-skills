from langchain_openai import OpenAI
from langgraph_skills.config import get_config

config = get_config()
llm = OpenAI(
    openai_api_key=config.openrouter_api_key,
    openai_api_base=config.openrouter_api_base,
    model=config.openrouter_model,
    default_headers={"X-Title": "langgraph-skills"},
)