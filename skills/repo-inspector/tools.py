import subprocess
from pathlib import Path

from langchain_core.tools import tool


@tool
def get_repo_status() -> dict:
    """Retrieves the current git status, including branch name, modified, and untracked files."""
    try:
        branch_proc = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        current_branch = branch_proc.stdout.strip()

        status_proc = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            check=True,
        )
        status_lines = [line.strip() for line in status_proc.stdout.splitlines() if line.strip()]

        return {
            "branch": current_branch or "detached",
            "has_changes": len(status_lines) > 0,
            "changed_files_count": len(status_lines),
            "status_summary": status_lines[:25],
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


@tool
def get_recent_commits(limit: int = 5) -> dict:
    """Retrieves recent git commit log entries.

    Args:
        limit: Maximum number of commits to retrieve (default is 5).
    """
    try:
        cmd = ["git", "log", f"-n{max(1, limit)}", "--pretty=format:%h|%an|%s|%cd", "--date=short"]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = []
        for line in proc.stdout.splitlines():
            if not line.strip():
                continue
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append(
                    {
                        "hash": parts[0],
                        "author": parts[1],
                        "message": parts[2],
                        "date": parts[3],
                    }
                )

        return {
            "commits": commits,
            "count": len(commits),
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


@tool
def list_workspace_files(directory: str = ".", pattern: str = "*") -> dict:
    """Lists files within a workspace directory matching a glob pattern.

    Args:
        directory: Relative path of the directory to search (default is current directory).
        pattern: Glob pattern to filter filenames (e.g. '*.py' or '*').
    """
    try:
        base_path = Path(directory).resolve()
        # Restrict listing to children under base_path
        matches = [
            str(p.relative_to(base_path))
            for p in sorted(base_path.glob(pattern))
            if not any(part.startswith(".") for part in p.parts)
        ]

        return {
            "directory": str(directory),
            "pattern": pattern,
            "count": len(matches),
            "files": matches[:50],
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


SKILL_TOOLS = [get_repo_status, get_recent_commits, list_workspace_files]
