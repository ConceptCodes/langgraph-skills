"""Prompts for the LangGraph Skills agent."""

from langgraph_skills.agent.utils.skills import SkillRegistry
from langgraph_skills.constants import RetentionPolicy

SYSTEM_MESSAGE = """You are an intelligent assistant equipped with a dynamic Skill system.
You only have basic conversational and meta-tools initially.
When a user request requires specialized domain capabilities, use `activate_skill(skill_name)`
to load the necessary skill and its tools into your operational context.

### Available Skills Catalog:
{catalog}
"""


def get_system_message(
    catalog: str,
    active_skills: list[str],
    registry: SkillRegistry,
    retention_policy: RetentionPolicy = RetentionPolicy.AUTO_EVICT,
) -> str:
    """Builds dynamic system prompt with Layer 1 catalog, active SOPs, and policy instructions."""
    base = SYSTEM_MESSAGE.format(catalog=catalog)

    if retention_policy == RetentionPolicy.MANUAL:
        base += (
            "\n\n### Context Hygiene Rule:\n"
            "When you complete a domain task, call `deactivate_skill(skill_name)` "
            "to release its instructions and tools from operational memory."
        )

    if active_skills:
        base += "\n\n### ACTIVE SKILLS INSTRUCTIONS (SOPs):"
        for name in active_skills:
            if name in registry.skills:
                skill = registry.skills[name]
                base += f"\n\n--- [Skill: {name}] ---\n{skill.instructions}"
    return base
