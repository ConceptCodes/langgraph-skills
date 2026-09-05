from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from langgraph_skills.agent.nodes import agent_node, should_continue
from langgraph_skills.agent.state import AgentState, Context
from langgraph_skills.agent.tools import create_meta_tools
from langgraph_skills.agent.utils import SkillRegistry, get_llm
from langgraph_skills.config import get_config
from langgraph_skills.constants import Nodes, RetentionPolicy


def build_graph(
    registry: SkillRegistry,
    llm: ChatOpenAI,
    meta_tools: Sequence[BaseTool],
) -> CompiledStateGraph:
    """Builds and compiles the StateGraph with context_schema=Context."""
    # Collect all tools across all skills for the master ToolNode executor
    all_skill_tools: list[BaseTool] = []
    for s in registry.skills.values():
        all_skill_tools.extend(s.tools)

    all_tools = list(meta_tools) + all_skill_tools
    tool_node = ToolNode(all_tools)

    workflow = StateGraph(AgentState, context_schema=Context)
    workflow.add_node(Nodes.AGENT.value, agent_node)
    workflow.add_node(Nodes.TOOLS.value, tool_node)

    workflow.add_edge(START, Nodes.AGENT.value)
    workflow.add_conditional_edges(
        Nodes.AGENT.value,
        should_continue,
        {Nodes.TOOLS.value: Nodes.TOOLS.value, END: END},
    )
    workflow.add_edge(Nodes.TOOLS.value, Nodes.AGENT.value)

    return workflow.compile()


def create_agent_app(
    skills_dir: Path,
    llm: Optional[ChatOpenAI] = None,
    retention_policy: Optional[RetentionPolicy] = None,
    max_active_skills: Optional[int] = None,
) -> tuple[CompiledStateGraph, Context]:
    """Factory creating a ready-to-invoke compiled graph and its context."""
    config = get_config()
    policy = retention_policy or config.skill_retention_policy
    max_skills = max_active_skills or config.max_active_skills

    registry = SkillRegistry(skills_dir)
    meta_tools = create_meta_tools(registry)
    active_llm = llm or get_llm()

    context = Context(
        llm=active_llm,
        registry=registry,
        meta_tools=meta_tools,
        retention_policy=policy,
        max_active_skills=max_skills,
    )
    graph = build_graph(registry, active_llm, meta_tools)
    return graph, context
