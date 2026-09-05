import importlib.util
from pathlib import Path

import yaml

from langgraph_skills.models import Skill, SkillMetadata


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
        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return

        # Strip opening delimiter and split on closing delimiter
        parts = content[3:].split("---", 1)
        if len(parts) < 2:
            return

        frontmatter_yaml = parts[0].strip()
        instructions = parts[1].strip()
        metadata_dict = yaml.safe_load(frontmatter_yaml) or {}
        metadata = SkillMetadata(**metadata_dict)

        # Import tools if tools.py exists
        tools = []
        tools_py = folder / "tools.py"
        if tools_py.exists():
            spec = importlib.util.spec_from_file_location(f"skills.{folder.name}.tools", tools_py)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                tools = getattr(module, "SKILL_TOOLS", [])

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
