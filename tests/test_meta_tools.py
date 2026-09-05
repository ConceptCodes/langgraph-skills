from pathlib import Path

from langgraph_skills.agent.tools import create_meta_tools
from langgraph_skills.agent.utils import SkillRegistry


def test_meta_tools_creation():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)
    meta_tools = create_meta_tools(registry)

    tools_map = {t.name: t for t in meta_tools}
    assert "activate_skill" in tools_map
    assert "deactivate_skill" in tools_map
    assert "list_available_skills" in tools_map


def test_meta_tools_activation():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)
    tools_map = {t.name: t for t in create_meta_tools(registry)}

    # Valid activation
    res = tools_map["activate_skill"].invoke({"skill_name": "text-analyzer"})
    assert "SUCCESS" in res
    assert "text-analyzer" in res

    # Invalid activation
    err = tools_map["activate_skill"].invoke({"skill_name": "unknown-skill"})
    assert "Error" in err


def test_meta_tools_deactivation():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)
    tools_map = {t.name: t for t in create_meta_tools(registry)}

    res = tools_map["deactivate_skill"].invoke({"skill_name": "text-analyzer"})
    assert "SUCCESS" in res
    assert "deactivated" in res


def test_meta_tools_list_catalog():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)
    tools_map = {t.name: t for t in create_meta_tools(registry)}

    catalog = tools_map["list_available_skills"].invoke({})
    assert "text-analyzer" in catalog
    assert "math-solver" in catalog
