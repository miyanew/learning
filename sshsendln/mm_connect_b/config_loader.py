import json
from typing import Any, Dict


def load_json_file(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}") from None
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in {file_path}") from None
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}") from e
