"""
Output formatting and export helpers.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


def _as_frame(payload: Any) -> pd.DataFrame:
    """Convert arbitrary API payload into a DataFrame."""
    if isinstance(payload, list):
        return pd.json_normalize(payload)
    if isinstance(payload, dict):
        return pd.json_normalize([payload])
    return pd.DataFrame([{"value": payload}])


def save_output(
    payload: Any,
    output_format: str,
    output_dir: str,
    stem: str = "results",
    include_timestamp: bool = True,
    timestamp_format: str = "{TIMESTAMP_FORMAT}",
) -> Path:
    """Save output in json/csv/xlsx/sqlite format."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = stem
    if include_timestamp:
        filename = f"{stem}_{datetime.now().strftime(timestamp_format)}"

    if output_format == "json":
        path = out_dir / f"{filename}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
        return path

    frame = _as_frame(payload)
    if output_format == "csv":
        path = out_dir / f"{filename}.csv"
        frame.to_csv(path, index=False)
        return path

    if output_format == "xlsx":
        path = out_dir / f"{filename}.xlsx"
        frame.to_excel(path, index=False, engine="openpyxl")
        return path

    if output_format == "sqlite":
        path = out_dir / f"{filename}.sqlite"
        with sqlite3.connect(path) as conn:
            frame.to_sql("results", conn, if_exists="replace", index=False)
        return path

    raise ValueError(f"Unsupported output format: {output_format}")
