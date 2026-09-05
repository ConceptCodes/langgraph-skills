from langchain_core.messages import SystemMessage
from langgraph.runtime import Runtime

from langgraph_skills.agent.prompts import get_system_message
from langgraph_skills.agent.state import AgentState, Context
from langgraph_skills.constants import RetentionPolicy


def agent_node(state: AgentState, runtime: Runtime[Context]) -> dict:
    """Core reasoning node with dynamic prompt synthesis and tool binding."""
    active_skills = state.get("active_skills") or []
    catalog = state.get("available_catalog") or runtime.context.registry.get_catalog_summary()
    policy = getattr(runtime.context, "retention_policy", RetentionPolicy.AUTO_EVICT)
    max_skills = getattr(runtime.context, "max_active_skills", 1)

    # 1. Synthesize dynamic prompt (Base + Active SOPs + Policy rules)
    sys_prompt = get_system_message(
        catalog=catalog,
        active_skills=active_skills,
        registry=runtime.context.registry,
        retention_policy=policy,
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

    # 4. Context engineering: update active_skills state based on policy and tool calls
    new_active = list(active_skills)
    has_tool_calls = bool(getattr(response, "tool_calls", None))

    if has_tool_calls:
        for tc in response.tool_calls:
            if tc["name"] == "activate_skill":
                s_name = tc["args"].get("skill_name")
                if s_name and s_name in runtime.context.registry.skills:
                    if policy == RetentionPolicy.AUTO_EVICT:
                        # Auto-evict older skills to respect max_active_skills limit
                        if s_name in new_active:
                            new_active.remove(s_name)
                        new_active.append(s_name)
                        if len(new_active) > max_skills:
                            new_active = new_active[-max_skills:]
                    else:
                        if s_name not in new_active:
                            new_active.append(s_name)

            elif tc["name"] == "deactivate_skill":
                s_name = tc["args"].get("skill_name")
                if s_name and s_name in new_active:
                    new_active.remove(s_name)
    else:
        # Final response delivered (no further tool calls)
        if policy == RetentionPolicy.EPHEMERAL:
            # Ephemeral: clear active skills to maintain a clean slate for the next query
            new_active = []

    return {
        "messages": [response],
        "active_skills": new_active,
        "available_catalog": catalog,
    }
