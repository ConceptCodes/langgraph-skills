import argparse
import sys
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage

from langgraph_skills.agent.main import create_agent_app
from langgraph_skills.agent.utils import SkillRegistry
from langgraph_skills.colors import Colors as c
from langgraph_skills.config import get_config
from langgraph_skills.constants import RetentionPolicy


def print_catalog(registry: SkillRegistry) -> None:
    """Displays the Layer 1 discovery catalog and tool lists with rich terminal colors."""
    divider = c.color("=" * 66, c.CYAN, c.BOLD)
    print(f"\n{divider}")
    print(c.color(" 🧠 Available Agent Skills (Layer 1 Discovery Catalog)", c.BRIGHT_CYAN, c.BOLD))
    print(f"{divider}")

    if not registry.skills:
        print(c.color("No skills discovered in the 'skills/' directory.", c.YELLOW))
        print(f"{divider}\n")
        return

    for name, skill in sorted(registry.skills.items()):
        skill_header = (
            f"{c.color('📦 Skill:', c.BRIGHT_GREEN, c.BOLD)} "
            f"{c.color(name, c.BOLD, c.WHITE)} "
            f"{c.color(f'(v{skill.metadata.version})', c.DIM)}"
        )
        print(f"\n{skill_header}")
        print(f"   {c.color('Description:', c.YELLOW)} {skill.metadata.description}")

        if skill.metadata.tags:
            tags_formatted = ", ".join(c.color(t, c.MAGENTA) for t in skill.metadata.tags)
            print(f"   {c.color('Tags:', c.YELLOW)} [{tags_formatted}]")

        tool_names = [t.name for t in skill.tools]
        if tool_names:
            tools_formatted = ", ".join(c.color(t, c.BRIGHT_BLUE) for t in tool_names)
            tools_label = c.color(f"Tools ({len(tool_names)}):", c.YELLOW)
            print(f"   {tools_label} {tools_formatted}")
        else:
            print(f"   {c.color('Tools:', c.YELLOW)} {c.color('None', c.DIM)}")

    print(f"\n{divider}\n")


def run_interactive(app, context) -> None:
    """Runs an interactive conversational session with colorful terminal indicators."""
    config = get_config()
    if not config.openrouter_api_key or config.openrouter_api_key == "your_openrouter_api_key_here":
        print(
            c.color(
                "\n⚠️  No valid OPENROUTER_API_KEY found in environment or .env file.",
                c.RED,
                c.BOLD,
            )
        )
        print(
            c.color(
                "Please configure OPENROUTER_API_KEY in .env before running interactive queries.",
                c.YELLOW,
            )
        )
        print(c.color("Example: cp .env.example .env && edit .env\n", c.DIM))
        sys.exit(1)

    banner_border = c.color("-" * 55, c.MAGENTA)
    print(f"\n{banner_border}")
    print(c.color(" 🚀 LangGraph Skills Agent Ready", c.BRIGHT_GREEN, c.BOLD))
    print(
        f" Context Policy: {c.color(context.retention_policy.value, c.BRIGHT_CYAN, c.BOLD)} "
        f"(max active: {c.color(str(context.max_active_skills), c.BRIGHT_YELLOW)})"
    )
    print(c.color(" Type your prompt to chat, or 'exit' / 'quit' to stop.", c.DIM))
    print(f"{banner_border}\n")

    messages = []
    active_skills: list[str] = []

    while True:
        try:
            prompt_label = c.color("You > ", c.BRIGHT_GREEN, c.BOLD)
            user_input = input(prompt_label).strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print(c.color("Goodbye! 👋", c.BRIGHT_CYAN))
                break

            messages.append(HumanMessage(content=user_input))
            state_input = {
                "messages": messages,
                "active_skills": active_skills,
                "available_catalog": context.registry.get_catalog_summary(),
            }

            print(c.color("\n🤖 Thinking & selecting skills...", c.BRIGHT_YELLOW, c.DIM))
            result = app.invoke(state_input, context=context)

            # Update conversational state
            messages = result["messages"]
            active_skills = result.get("active_skills", [])

            # Print latest AI response
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) and msg.content:
                    agent_prefix = c.color("\nAgent > ", c.BRIGHT_CYAN, c.BOLD)
                    print(f"{agent_prefix}{msg.content}")
                    break

            if active_skills:
                active_str = ", ".join(c.color(s, c.BRIGHT_MAGENTA, c.BOLD) for s in active_skills)
                print(f"\n{c.color('⚡ Active Skills in Context:', c.MAGENTA)} [{active_str}]\n")
            else:
                print(f"\n{c.color('🧹 Operational Context Clean (0 active skills)', c.DIM)}\n")

        except (KeyboardInterrupt, EOFError):
            print(c.color("\nExiting session. 👋", c.BRIGHT_CYAN))
            break
        except Exception as e:
            print(c.color(f"\n❌ Error during execution: {e}", c.RED, c.BOLD))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LangGraph Skills: An agentic application showcasing dynamic skill utilization."
    )
    parser.add_argument(
        "--catalog",
        action="store_true",
        help="List all discovered skills in the catalog and exit.",
    )
    parser.add_argument(
        "--skills-dir",
        type=str,
        default="skills",
        help="Directory containing skill packages (default: 'skills')",
    )
    parser.add_argument(
        "--retention-policy",
        type=str,
        choices=["auto_evict", "ephemeral", "manual"],
        default=None,
        help="Context retention policy: 'auto_evict' (default), 'ephemeral', or 'manual'",
    )
    parser.add_argument(
        "--max-active-skills",
        type=int,
        default=None,
        help="Maximum concurrently active skills in state (default: 1)",
    )

    args = parser.parse_args()
    skills_path = Path(args.skills_dir).resolve()

    registry = SkillRegistry(skills_path)

    if args.catalog:
        print_catalog(registry)
        return

    print_catalog(registry)

    policy = RetentionPolicy(args.retention_policy) if args.retention_policy else None
    app, context = create_agent_app(
        skills_dir=skills_path,
        retention_policy=policy,
        max_active_skills=args.max_active_skills,
    )
    run_interactive(app, context)


if __name__ == "__main__":
    main()
