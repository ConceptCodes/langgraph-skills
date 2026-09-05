from pathlib import Path

from langgraph_skills.main import main


def test_main_importable():
    assert callable(main)


def test_main_catalog_cli_flag(capsys):
    skills_dir = Path(__file__).parent.parent / "skills"
    main(["--catalog", "--skills-dir", str(skills_dir)])
    captured = capsys.readouterr()
    assert "Available Agent Skills" in captured.out
    assert "text-analyzer" in captured.out
    assert "math-solver" in captured.out
    assert "repo-inspector" in captured.out
