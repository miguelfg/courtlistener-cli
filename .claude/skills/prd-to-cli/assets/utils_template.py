"""
Shared utility helpers for generated CLI projects.
"""

from typing import Any


def parse_env_value(value: str) -> Any:
    """Convert .env string values into primitive Python types when possible."""
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"none", "null"}:
        return None

    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value
