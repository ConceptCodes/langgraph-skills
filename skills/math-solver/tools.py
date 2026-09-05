import math
import statistics

from langchain_core.tools import tool


@tool
def calculate_expression(expression: str) -> dict:
    """Evaluates a mathematical expression safely.

    Supports standard math functions like sqrt, sin, cos, log, etc.

    Args:
        expression: The mathematical expression to evaluate (e.g. '25 * 4 + sqrt(144)').
    """
    safe_dict = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
        "pow": pow,
        "abs": abs,
        "round": round,
    }

    try:
        # Evaluate with empty globals and restricted math locals
        result = eval(expression, {"__builtins__": {}}, safe_dict)  # noqa: S307
        return {
            "expression": expression,
            "result": result,
            "status": "success",
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
            "status": "error",
        }


@tool
def compute_statistics(numbers: list[float]) -> dict:
    """Computes summary statistics for a list of numeric values.

    Includes mean, median, std_dev, min, max, count.

    Args:
        numbers: List of float or integer numbers.
    """
    if not numbers:
        return {"error": "Empty list provided", "status": "error"}

    try:
        n = len(numbers)
        total = sum(numbers)
        mean = statistics.mean(numbers)
        median = statistics.median(numbers)
        stdev = statistics.stdev(numbers) if n > 1 else 0.0

        return {
            "count": n,
            "sum": round(total, 4),
            "mean": round(mean, 4),
            "median": round(median, 4),
            "std_dev": round(stdev, 4),
            "min": min(numbers),
            "max": max(numbers),
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


SKILL_TOOLS = [calculate_expression, compute_statistics]
