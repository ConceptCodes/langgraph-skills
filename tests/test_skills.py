from pathlib import Path

from langgraph_skills.agent.utils import SkillRegistry


def test_skill_registry_loads_sample_skills():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)

    expected_skills = [
        "data-converter",
        "datetime-utility",
        "math-solver",
        "repo-inspector",
        "text-analyzer",
    ]
    for skill_name in expected_skills:
        assert skill_name in registry.skills

    # Verify text-analyzer
    text_skill = registry.skills["text-analyzer"]
    assert text_skill.metadata.name == "text-analyzer"
    assert "nlp" in text_skill.metadata.tags
    assert len(text_skill.tools) == 3
    tool_names = [t.name for t in text_skill.tools]
    assert "count_words_and_characters" in tool_names
    assert "analyze_sentiment" in tool_names
    assert "calculate_reading_time" in tool_names

    # Verify math-solver
    math_skill = registry.skills["math-solver"]
    assert math_skill.metadata.name == "math-solver"
    assert len(math_skill.tools) == 2
    math_tools = [t.name for t in math_skill.tools]
    assert "calculate_expression" in math_tools
    assert "compute_statistics" in math_tools

    # Verify repo-inspector
    repo_skill = registry.skills["repo-inspector"]
    assert len(repo_skill.tools) == 3
    repo_tools = [t.name for t in repo_skill.tools]
    assert "get_repo_status" in repo_tools
    assert "get_recent_commits" in repo_tools
    assert "list_workspace_files" in repo_tools

    # Verify data-converter
    data_skill = registry.skills["data-converter"]
    assert len(data_skill.tools) == 4
    data_tools = [t.name for t in data_skill.tools]
    assert "csv_to_json" in data_tools
    assert "json_to_csv" in data_tools

    # Verify datetime-utility
    dt_skill = registry.skills["datetime-utility"]
    assert len(dt_skill.tools) == 3
    dt_tools = [t.name for t in dt_skill.tools]
    assert "get_current_time" in dt_tools
    assert "calculate_date_difference" in dt_tools


def test_catalog_summary_formatting():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)
    catalog = registry.get_catalog_summary()

    assert "- **text-analyzer**:" in catalog
    assert "- **math-solver**:" in catalog
    assert "- **repo-inspector**:" in catalog
    assert "- **data-converter**:" in catalog
    assert "- **datetime-utility**:" in catalog


def test_text_analyzer_tools_execution():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)
    tools_map = {t.name: t for t in registry.skills["text-analyzer"].tools}

    # Word & Char count
    wc_tool = tools_map["count_words_and_characters"]
    wc_result = wc_tool.invoke({"text": "Hello world from LangGraph skills!"})
    assert wc_result["word_count"] == 5
    assert wc_result["char_count"] == 34

    # Sentiment
    sent_tool = tools_map["analyze_sentiment"]
    pos_res = sent_tool.invoke({"text": "This is an amazing and excellent tool."})
    assert pos_res["polarity"] == "positive"
    assert pos_res["score"] > 0

    # Reading time
    read_tool = tools_map["calculate_reading_time"]
    read_res = read_tool.invoke({"text": "One two three four five.", "wpm": 100})
    assert read_res["estimated_minutes"] == 0.05


def test_math_solver_tools_execution():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)
    tools_map = {t.name: t for t in registry.skills["math-solver"].tools}

    calc_tool = tools_map["calculate_expression"]
    calc_res = calc_tool.invoke({"expression": "25 * 4 + sqrt(144)"})
    assert calc_res["status"] == "success"
    assert calc_res["result"] == 112.0

    stat_tool = tools_map["compute_statistics"]
    stat_res = stat_tool.invoke({"numbers": [10.0, 20.0, 30.0, 40.0]})
    assert stat_res["status"] == "success"
    assert stat_res["mean"] == 25.0
    assert stat_res["min"] == 10.0
    assert stat_res["max"] == 40.0


def test_repo_inspector_tools_execution():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)
    tools_map = {t.name: t for t in registry.skills["repo-inspector"].tools}

    status_tool = tools_map["get_repo_status"]
    status_res = status_tool.invoke({})
    assert status_res["status"] == "success"
    assert "branch" in status_res

    commits_tool = tools_map["get_recent_commits"]
    commits_res = commits_tool.invoke({"limit": 2})
    assert commits_res["status"] == "success"
    assert commits_res["count"] > 0

    files_tool = tools_map["list_workspace_files"]
    files_res = files_tool.invoke({"directory": "src", "pattern": "*.py"})
    assert files_res["status"] == "success"


def test_data_converter_tools_execution():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)
    tools_map = {t.name: t for t in registry.skills["data-converter"].tools}

    # CSV to JSON
    csv_input = "name,age\nAlice,30\nBob,25"
    c2j = tools_map["csv_to_json"].invoke({"csv_text": csv_input})
    assert c2j["status"] == "success"
    assert c2j["record_count"] == 2

    # JSON to CSV
    j2c = tools_map["json_to_csv"].invoke({"json_text": c2j["json_data"]})
    assert j2c["status"] == "success"
    assert "Alice" in j2c["csv_data"]

    # JSON to YAML
    j2y = tools_map["json_to_yaml"].invoke({"json_text": '{"project": "langgraph-skills"}'})
    assert j2y["status"] == "success"
    assert "project: langgraph-skills" in j2y["yaml_data"]

    # Validate JSON
    v_res = tools_map["validate_json"].invoke({"json_text": '{"valid": true}'})
    assert v_res["is_valid"] is True


def test_datetime_utility_tools_execution():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)
    tools_map = {t.name: t for t in registry.skills["datetime-utility"].tools}

    # Current time
    time_tool = tools_map["get_current_time"]
    time_res = time_tool.invoke({})
    assert time_res["status"] == "success"
    assert "current_iso" in time_res

    # Date diff
    diff_tool = tools_map["calculate_date_difference"]
    diff_res = diff_tool.invoke({"date_start": "2026-01-01", "date_end": "2026-01-11"})
    assert diff_res["status"] == "success"
    assert diff_res["days_difference"] == 10

    # Date offset
    offset_tool = tools_map["offset_date"]
    offset_res = offset_tool.invoke({"base_date": "2026-01-01", "days": 5})
    assert offset_res["status"] == "success"
    assert offset_res["result_date"] == "2026-01-06"
