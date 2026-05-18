#!/usr/bin/env python3
"""Convert a long HTML document into simple markdown for easier inspection/parsing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from html_processing import html_to_markdown, truncate_lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert HTML (file or stdin) into simplified markdown.",
    )
    parser.add_argument("input", help="Input HTML file path or '-' for stdin")
    parser.add_argument("output", nargs="?", help="Optional output .md path")
    parser.add_argument(
        "--max-lines",
        type=int,
        default=0,
        help="Truncate markdown output to N lines (0 = no truncation)",
    )
    return parser.parse_args()


def read_input(input_arg: str) -> str:
    if input_arg == "-":
        return sys.stdin.read()
    return Path(input_arg).read_text(encoding="utf-8", errors="ignore")


def main() -> None:
    args = parse_args()
    html = read_input(args.input)
    markdown = html_to_markdown(html)
    markdown = truncate_lines(markdown, args.max_lines)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        print(f"Wrote markdown to {output_path}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
