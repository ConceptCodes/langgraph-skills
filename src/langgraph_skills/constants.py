from enum import Enum


class Nodes(str, Enum):
    AGENT = "agent"
    ROUTER = "router"
    TOOLS = "tools"


class RetentionPolicy(str, Enum):
    """Context engineering strategies for managing active skills in agent state."""

    AUTO_EVICT = "auto_evict"  # Activating a new skill evicts old skills (max_active_skills cap)
    EPHEMERAL = "ephemeral"  # Clears active skills when the final answer is delivered
    MANUAL = "manual"  # Skills persist until explicitly closed via deactivate_skill
