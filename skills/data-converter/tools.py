import csv
import io
import json

import yaml
from langchain_core.tools import tool


@tool
def csv_to_json(csv_text: str) -> dict:
    """Converts a CSV formatted string into a JSON formatted array of records.

    Args:
        csv_text: String content in comma-separated values format.
    """
    try:
        reader = csv.DictReader(io.StringIO(csv_text.strip()))
        rows = list(reader)
        json_output = json.dumps(rows, indent=2)
        return {
            "record_count": len(rows),
            "json_data": json_output,
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


@tool
def json_to_csv(json_text: str) -> dict:
    """Converts a JSON list of objects into a standard CSV string.

    Args:
        json_text: JSON string containing an array of uniform dictionary objects.
    """
    try:
        data = json.loads(json_text)
        if not isinstance(data, list):
            return {
                "error": "Input JSON must be an array of objects to convert to CSV",
                "status": "error",
            }
        if not data:
            return {"csv_data": "", "record_count": 0, "status": "success"}

        output = io.StringIO()
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

        return {
            "record_count": len(data),
            "fieldnames": fieldnames,
            "csv_data": output.getvalue(),
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


@tool
def json_to_yaml(json_text: str) -> dict:
    """Converts a valid JSON string into a formatted YAML string.

    Args:
        json_text: Valid JSON string representation.
    """
    try:
        data = json.loads(json_text)
        yaml_output = yaml.dump(data, sort_keys=False)
        return {
            "yaml_data": yaml_output,
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


@tool
def validate_json(json_text: str) -> dict:
    """Validates whether a string is well-formed JSON and returns its type and top-level keys.

    Args:
        json_text: String to parse and validate as JSON.
    """
    try:
        parsed = json.loads(json_text)
        payload_type = type(parsed).__name__
        info = {
            "is_valid": True,
            "type": payload_type,
            "status": "success",
        }
        if isinstance(parsed, dict):
            info["key_count"] = len(parsed.keys())
            info["keys"] = list(parsed.keys())
        elif isinstance(parsed, list):
            info["item_count"] = len(parsed)
        return info
    except Exception as e:
        return {
            "is_valid": False,
            "error": str(e),
            "status": "error",
        }


SKILL_TOOLS = [csv_to_json, json_to_csv, json_to_yaml, validate_json]
