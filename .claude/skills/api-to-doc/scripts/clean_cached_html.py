#!/usr/bin/env python3
"""Clean cached HTML docs and optionally generate markdown versions."""

from __future__ import annotations

import argparse
from pathlib import Path

from html_processing import clean_html, html_to_markdown, truncate_lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean cached API docs HTML files and generate markdown companions.",
    )
    parser.add_argument(
        "cache_dir",
        nargs="?",
        default="/tmp/api-to-doc-cache",
        help="Directory containing cached HTML files.",
    )
    parser.add_argument(
        "--glob",
        default="*.html",
        help="Glob pattern used to select HTML files.",
    )
    parser.add_argument(
        "--out-dir",
        default="",
        help="Output directory (default: <cache_dir>/cleaned).",
    )
    parser.add_argument(
        "--skip-clean-html",
        action="store_true",
        help="Do not write cleaned HTML files.",
    )
    parser.add_argument(
        "--skip-markdown",
        action="store_true",
        help="Do not write markdown files.",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=0,
        help="Truncate generated markdown files to N lines (0 = no truncation).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cache_dir = Path(args.cache_dir)
    if not cache_dir.exists():
        raise SystemExit(f"Cache directory does not exist: {cache_dir}")

    out_dir = Path(args.out_dir) if args.out_dir else cache_dir / "cleaned"
    out_dir.mkdir(parents=True, exist_ok=True)

    html_files = sorted(cache_dir.glob(args.glob))
    if not html_files:
        print(f"No files matched {args.glob} in {cache_dir}")
        return

    converted = 0
    for html_path in html_files:
        html = html_path.read_text(encoding="utf-8", errors="ignore")
        cleaned_html = clean_html(html)
        markdown = truncate_lines(html_to_markdown(html), args.max_lines)

        stem = html_path.stem
        if not args.skip_clean_html:
            clean_path = out_dir / f"{stem}.clean.html"
            clean_path.write_text(cleaned_html, encoding="utf-8")
        if not args.skip_markdown:
            md_path = out_dir / f"{stem}.md"
            md_path.write_text(markdown, encoding="utf-8")

        converted += 1

    print(f"Processed {converted} cached HTML file(s) into {out_dir}")


if __name__ == "__main__":
    main()
