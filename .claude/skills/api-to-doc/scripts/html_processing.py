#!/usr/bin/env python3
"""Utilities to clean noisy HTML and convert it to simple Markdown-friendly text."""

from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser

_NOISE_BLOCK_PATTERN = re.compile(
    r"<(script|style|noscript|svg|iframe)[^>]*>.*?</\\1>",
    flags=re.IGNORECASE | re.DOTALL,
)
_HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", flags=re.DOTALL)


class _SimpleMarkdownParser(HTMLParser):
    """Very small HTML->Markdown parser for API docs preprocessing."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._in_pre = False
        self._in_code = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self.parts.append("\n" + ("#" * level) + " ")
        elif tag == "p":
            self.parts.append("\n\n")
        elif tag in {"br", "hr"}:
            self.parts.append("\n")
        elif tag in {"ul", "ol"}:
            self.parts.append("\n")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag == "pre":
            self._in_pre = True
            self.parts.append("\n```\n")
        elif tag == "code":
            self._in_code = True
            if not self._in_pre:
                self.parts.append("`")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "pre":
            self._in_pre = False
            self.parts.append("\n```\n")
        elif tag == "code":
            if not self._in_pre:
                self.parts.append("`")
            self._in_code = False
        elif tag in {"p", "section", "article", "div"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        text = unescape(data)
        if not text.strip() and not self._in_pre:
            return

        if self._in_pre:
            self.parts.append(text)
            return

        normalized = re.sub(r"\\s+", " ", text)
        self.parts.append(normalized)


def clean_html(html: str) -> str:
    """Remove high-noise blocks and normalize whitespace to make parsing easier."""
    without_noise = _NOISE_BLOCK_PATTERN.sub(" ", html)
    without_comments = _HTML_COMMENT_PATTERN.sub(" ", without_noise)
    without_blank_lines = re.sub(r"\n\s*\n+", "\n\n", without_comments)
    return without_blank_lines.strip()


def html_to_markdown(html: str) -> str:
    """Convert HTML to a minimal markdown/plaintext representation."""
    parser = _SimpleMarkdownParser()
    parser.feed(clean_html(html))
    raw = "".join(parser.parts)

    # Keep docs compact and readable.
    raw = re.sub(r"[ \t]+\n", "\n", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip() + "\n"


def truncate_lines(text: str, max_lines: int) -> str:
    """Return first max_lines lines from text."""
    if max_lines <= 0:
        return text
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines]) + "\n"
