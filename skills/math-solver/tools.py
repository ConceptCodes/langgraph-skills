import ast
import math
import operator
import statistics

from langchain_core.tools import tool

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_SAFE_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "pow": pow,
    "abs": abs,
    "round": round,
}

_SAFE_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant: {node.value!r}")
    if isinstance(node, ast.Name):
        if node.id in _SAFE_CONSTANTS:
            return _SAFE_CONSTANTS[node.id]
        raise ValueError(f"Unsupported variable or constant: {node.id}")
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in _OPERATORS:
            return _OPERATORS[op_type](_eval_node(node.operand))
        raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in _OPERATORS:
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            return _OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct function calls are allowed")
        func_name = node.func.id
        if func_name not in _SAFE_FUNCTIONS:
            raise ValueError(f"Unsupported function: {func_name}")
        args = [_eval_node(arg) for arg in node.args]
        return float(_SAFE_FUNCTIONS[func_name](*args))
    raise ValueError(f"Unsupported expression syntax: {type(node).__name__}")


def safe_eval_expression(expression: str) -> float:
    tree = ast.parse(expression.strip(), mode="eval")
    return _eval_node(tree)


@tool
def calculate_expression(expression: str) -> dict:
    """Evaluates a mathematical expression safely using AST parsing.

    Supports standard math functions like sqrt, sin, cos, log, etc.

    Args:
        expression: The mathematical expression to evaluate (e.g. '25 * 4 + sqrt(144)').
    """
    try:
        result = safe_eval_expression(expression)
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
