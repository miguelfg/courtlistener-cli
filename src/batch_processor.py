"""Batch processing for CSV and JSON Lines input"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any


def read_csv_batch(input_file: Path) -> List[Dict[str, Any]]:
    """Read batch requests from CSV file"""
    requests = []
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            requests.append(row)
    return requests


def read_json_lines_batch(input_file: Path) -> List[Dict[str, Any]]:
    """Read batch requests from JSON Lines (TXT) file"""
    requests = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.strip():
                requests.append(json.loads(line))
    return requests


def detect_format(input_file: Path) -> str:
    """Detect input file format"""
    suffix = input_file.suffix.lower()
    if suffix == '.csv':
        return 'csv'
    elif suffix in ['.txt', '.jsonl']:
        return 'jsonl'
    else:
        # Try to detect by content
        with open(input_file, 'r') as f:
            first_line = f.readline()
            if '{' in first_line:
                return 'jsonl'
            return 'csv'


def read_batch_file(input_file: Path) -> List[Dict[str, Any]]:
    """Read batch file in any supported format"""
    fmt = detect_format(input_file)
    if fmt == 'csv':
        return read_csv_batch(input_file)
    else:
        return read_json_lines_batch(input_file)
