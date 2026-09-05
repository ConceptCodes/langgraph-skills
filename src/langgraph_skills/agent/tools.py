from langchain_core.tools import BaseTool, tool


def create_meta_tools(registry) -> list[BaseTool]:
    """Factory creating meta-tools that manipulate skill state."""

    @tool
    def activate_skill(skill_name: str) -> str:
        """Activates a skill by name to gain access to its specialized instructions and tools.

        Args:
            skill_name: The name of the skill to activate.
        """
        if skill_name not in registry.skills:
            return (
                f"Error: Skill '{skill_name}' does not exist. "
                f"Available: {list(registry.skills.keys())}"
            )
        return (
            f"SUCCESS: Skill '{skill_name}' activated. "
            "Its instructions and tools are now bound to your context."
        )

    @tool
    def deactivate_skill(skill_name: str) -> str:
        """Deactivates an active skill when its task is complete, clearing context.

        Args:
            skill_name: The name of the skill to deactivate.
        """
        return f"SUCCESS: Skill '{skill_name}' deactivated."

    @tool
    def list_available_skills() -> str:
        """Lists all skills currently installed with their descriptions."""
        return registry.get_catalog_summary()

    return [activate_skill, deactivate_skill, list_available_skills]
