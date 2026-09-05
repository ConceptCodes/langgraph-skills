from langgraph.graph import END

from langgraph_skills.agent.state import AgentState
from langgraph_skills.constants import Nodes


def should_continue(state: AgentState) -> str:
    """Evaluates whether to continue to the ToolNode or conclude the run."""
    messages = state.get("messages", [])
    if not messages:
        return END

    last_message = messages[-1]
    if getattr(last_message, "tool_calls", None):
        return Nodes.TOOLS.value

    return END
