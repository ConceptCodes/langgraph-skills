from langchain_core.messages import SystemMessage
from langgraph.runtime import Runtime

from langgraph_skills.agent.prompts import get_system_message
from langgraph_skills.agent.state import AgentState, Context


def agent_node(state: AgentState, runtime: Runtime[Context]) -> dict:
    """Core reasoning node with dynamic prompt synthesis and tool binding."""
    active_skills = state.get("active_skills") or []
    catalog = state.get("available_catalog") or runtime.context.registry.get_catalog_summary()

    # 1. Synthesize dynamic prompt (Base + Active SOPs)
    sys_prompt = get_system_message(
        catalog=catalog,
        active_skills=active_skills,
        registry=runtime.context.registry,
    )

    # 2. Dynamically resolve tools to bind (Meta-tools + Active Skill tools)
    bound_tools = list(runtime.context.meta_tools)
    for name in active_skills:
        if name in runtime.context.registry.skills:
            bound_tools.extend(runtime.context.registry.skills[name].tools)

    # 3. Bind tools and invoke the model
    llm = runtime.context.llm
    model_with_tools = llm.bind_tools(bound_tools)
    messages = [SystemMessage(content=sys_prompt)] + list(state["messages"])
    response = model_with_tools.invoke(messages)

    # 4. Check if active_skills state needs updating based on tool calls
    new_active = list(active_skills)
    if getattr(response, "tool_calls", None):
        for tc in response.tool_calls:
            if tc["name"] == "activate_skill":
                s_name = tc["args"].get("skill_name")
                if (
                    s_name
                    and s_name not in new_active
                    and s_name in runtime.context.registry.skills
                ):
                    new_active.append(s_name)
            elif tc["name"] == "deactivate_skill":
                s_name = tc["args"].get("skill_name")
                if s_name and s_name in new_active:
                    new_active.remove(s_name)

    return {
        "messages": [response],
        "active_skills": new_active,
        "available_catalog": catalog,
    }
