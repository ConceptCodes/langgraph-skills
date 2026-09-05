import argparse
import sys
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage

from langgraph_skills.agent.main import create_agent_app
from langgraph_skills.agent.utils import SkillRegistry
from langgraph_skills.config import get_config


def print_catalog(registry: SkillRegistry) -> None:
    """Displays the Layer 1 discovery catalog and tool lists."""
    print("=" * 60)
    print(" Available Agent Skills (Layer 1 Discovery)")
    print("=" * 60)
    if not registry.skills:
        print("No skills discovered in the 'skills/' directory.")
        return

    for name, skill in sorted(registry.skills.items()):
        print(f"\n📦 Skill: {name} (v{skill.metadata.version})")
        print(f"   Description: {skill.metadata.description}")
        print(f"   Tags: {', '.join(skill.metadata.tags)}")
        tool_names = [t.name for t in skill.tools]
        print(f"   Tools ({len(tool_names)}): {', '.join(tool_names) if tool_names else 'None'}")
    print("\n" + "=" * 60)


def run_interactive(app, context) -> None:
    """Runs an interactive conversational session with the skills agent."""
    config = get_config()
    if not config.openrouter_api_key or config.openrouter_api_key == "your_openrouter_api_key_here":
        print("\n⚠️  No valid OPENROUTER_API_KEY found in environment or .env file.")
        print("Please configure OPENROUTER_API_KEY in .env before running interactive queries.")
        print("Example: cp .env.example .env && edit .env\n")
        sys.exit(1)

    print("\nStarting LangGraph Skills Agent (type 'exit' or 'quit' to stop)...")
    messages = []
    active_skills: list[str] = []

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            messages.append(HumanMessage(content=user_input))
            state_input = {
                "messages": messages,
                "active_skills": active_skills,
                "available_catalog": context.registry.get_catalog_summary(),
            }

            print("\n🤖 Thinking & selecting skills...")
            result = app.invoke(state_input, context=context)

            # Update conversational state
            messages = result["messages"]
            active_skills = result.get("active_skills", [])

            # Print latest AI response
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) and msg.content:
                    print(f"\nAgent > {msg.content}")
                    break

            if active_skills:
                print(f"\n[Active Skills in Context: {', '.join(active_skills)}]")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        except Exception as e:
            print(f"\n❌ Error during execution: {e}")


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

    args = parser.parse_args()
    skills_path = Path(args.skills_dir).resolve()

    registry = SkillRegistry(skills_path)

    if args.catalog:
        print_catalog(registry)
        return

    print_catalog(registry)
    app, context = create_agent_app(skills_path)
    run_interactive(app, context)


if __name__ == "__main__":
    main()
