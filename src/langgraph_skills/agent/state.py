from collections.abc import Sequence
from dataclasses import dataclass
from typing import Annotated

from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from langgraph_skills.agent.utils.skills import SkillRegistry
from langgraph_skills.constants import RetentionPolicy


class AgentState(TypedDict):
    """Represents the state of the LangGraph Skills agent."""

    messages: Annotated[list[BaseMessage], add_messages]
    active_skills: list[str]
    available_catalog: str


@dataclass
class Context:
    """Runtime context injected into nodes."""

    llm: ChatOpenAI
    registry: SkillRegistry
    meta_tools: Sequence[BaseTool]
    retention_policy: RetentionPolicy = RetentionPolicy.AUTO_EVICT
    max_active_skills: int = 1
