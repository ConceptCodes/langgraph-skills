import importlib.util
import logging
from pathlib import Path

import yaml

from langgraph_skills.models import Skill, SkillMetadata

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Registry that discovers and manages skills from disk."""

    def __init__(self, skills_dir: Path) -> None:
        self.skills_dir = skills_dir
        self.skills: dict[str, Skill] = {}
        self.load_all()

    def load_all(self) -> None:
        """Scan skills directory and load all valid skills."""
        if not self.skills_dir.exists():
            return

        for skill_folder in self.skills_dir.iterdir():
            if not skill_folder.is_dir():
                continue
            skill_md = skill_folder / "SKILL.md"
            if not skill_md.exists():
                continue
            self._load_skill(skill_folder, skill_md)

    def _load_skill(self, folder: Path, skill_md: Path) -> None:
        try:
            content = skill_md.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning("Skipping skill '%s': Failed to read SKILL.md (%s)", folder.name, e)
            return

        if not content.startswith("---"):
            logger.warning(
                "Skipping skill '%s': Missing opening YAML frontmatter delimiter '---'",
                folder.name,
            )
            return

        # Strip opening delimiter and split on closing delimiter
        parts = content[3:].split("---", 1)
        if len(parts) < 2:
            logger.warning(
                "Skipping skill '%s': Missing closing YAML frontmatter delimiter '---'",
                folder.name,
            )
            return

        frontmatter_yaml = parts[0].strip()
        instructions = parts[1].strip()

        try:
            metadata_dict = yaml.safe_load(frontmatter_yaml) or {}
            metadata = SkillMetadata(**metadata_dict)
        except Exception as e:
            logger.warning("Skipping skill '%s': Invalid frontmatter metadata (%s)", folder.name, e)
            return

        # Import tools if tools.py exists
        tools = []
        tools_py = folder / "tools.py"
        if tools_py.exists():
            try:
                spec = importlib.util.spec_from_file_location(
                    f"skills.{folder.name}.tools", tools_py
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    tools = getattr(module, "SKILL_TOOLS", [])
            except Exception as e:
                logger.warning(
                    "Failed to load tools for skill '%s': %s",
                    folder.name,
                    e,
                )

        self.skills[metadata.name] = Skill(
            metadata=metadata,
            instructions=instructions,
            tools=tools,
        )

    def get_catalog_summary(self) -> str:
        """Returns Layer 1 summary of all available skills."""
        if not self.skills:
            return "No skills currently installed."

        lines = []
        for name, s in sorted(self.skills.items()):
            lines.append(f"- **{name}**: {s.metadata.description}")
        return "\n".join(lines)
