#!/usr/bin/env python3
"""
Extract links from HTML documentation and identify API-related pages to crawl.
Helps discover related documentation pages for comprehensive API extraction.
"""

import json
import re
import sys
from html.parser import HTMLParser
from typing import Dict, List
from urllib.parse import urljoin, urlparse


class LinkExtractor(HTMLParser):
    """Extract links from HTML and categorize them."""

    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.links = []
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.in_script = True
        elif tag == "style":
            self.in_style = True
        elif tag == "a":
            for attr, value in attrs:
                if attr == "href" and value:
                    # Normalize URL
                    url = urljoin(self.base_url, value)
                    if url not in [link["url"] for link in self.links]:
                        self.links.append(
                            {
                                "url": url,
                                "href": value,
                                "relative": not value.startswith(("http://", "https://", "/")),
                            }
                        )

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
        elif tag == "style":
            self.in_style = False


def extract_links(content: str, base_url: str) -> List[Dict]:
    """Extract all links from HTML content."""
    extractor = LinkExtractor(base_url)
    try:
        extractor.feed(content)
    except Exception as e:
        print(f"Warning: Error parsing HTML: {e}", file=sys.stderr)
    return extractor.links


def categorize_links(links: List[Dict], base_url: str) -> Dict[str, List[Dict]]:
    """Categorize links by relevance to API documentation."""
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc

    categories = {
        "api_docs": [],  # Core API documentation
        "related_api": [],  # Related API/resource pages
        "endpoints": [],  # Endpoint-specific pages
        "guides": [],  # Getting started, guides, tutorials
        "auth": [],  # Authentication documentation
        "examples": [],  # Code examples, samples
        "reference": [],  # API reference pages
        "other": [],  # Everything else
    }

    # Patterns for categorization
    api_keywords = r"(?:api|endpoint|method|resource|operation)"
    auth_keywords = r"(?:auth|oauth|token|key|credential|permission)"
    guide_keywords = r"(?:guide|tutorial|getting.*started|quickstart|intro|overview)"
    example_keywords = r"(?:example|sample|code|snippet|demo|playground)"
    reference_keywords = r"(?:reference|spec|schema|definition|documentation)"
    endpoint_keywords = r"(?:endpoint|path|route|url|action)"

    for link in links:
        url = link["url"]
        href = link["href"].lower()
        parsed = urlparse(url)

        # Skip certain URL patterns
        if any(skip in href for skip in ["#", "javascript:", "mailto:", ".pdf", ".zip"]):
            continue

        # Skip non-same-domain links unless clearly API-related
        if parsed.netloc != base_domain:
            if re.search(api_keywords, href):
                categories["related_api"].append(link)
            continue

        # Categorize by keyword patterns
        if re.search(auth_keywords, href):
            categories["auth"].append(link)
        elif re.search(endpoint_keywords, href):
            categories["endpoints"].append(link)
        elif re.search(example_keywords, href):
            categories["examples"].append(link)
        elif re.search(reference_keywords, href):
            categories["reference"].append(link)
        elif re.search(guide_keywords, href):
            categories["guides"].append(link)
        elif re.search(api_keywords, href):
            categories["api_docs"].append(link)
        else:
            categories["other"].append(link)

    return categories


def filter_crawlable_links(links: List[Dict], max_depth: int = 2) -> List[Dict]:
    """Filter links to focus on crawlable documentation pages."""
    crawlable = []

    for link in links:
        url = link["url"]
        parsed = urlparse(url)
        path = parsed.path

        # Skip certain paths
        if any(
            skip in path.lower()
            for skip in [
                "/search",
                "/tag/",
                "/category/",
                "/page/",
                "/blog/",
                "/news/",
                "/forum/",
                "/community/",
                "/download",
                "/pricing",
                "/contact",
                "/about",
                "/support",
                "/help",
                "/faq",
            ]
        ):
            continue

        # Skip anchors-only
        if url.endswith("#") or "#" in url and url.count("/") < 3:
            continue

        # Check path depth (relative to base)
        depth = path.count("/")
        if depth <= max_depth:
            crawlable.append(link)

    return crawlable


def save_links_to_file(links: Dict, output_path: str) -> bool:
    """Save categorized links to a JSON file."""
    try:
        with open(output_path, "w") as f:
            json.dump(links, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving links: {e}", file=sys.stderr)
        return False


def main():
    """Extract links from fetched HTML content."""
    if len(sys.argv) < 3:
        print("Usage: link_extractor.py <html_file> <base_url> [output_file]")
        print("  html_file: Path to HTML file or '-' for stdin")
        print("  base_url: Base URL for resolving relative links")
        print("  output_file: Optional output JSON file (default: stdout)")
        sys.exit(1)

    html_file = sys.argv[1]
    base_url = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    # Read HTML content
    try:
        if html_file == "-":
            content = sys.stdin.read()
        else:
            with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
    except Exception as e:
        print(f"Error reading HTML: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract and categorize links
    links = extract_links(content, base_url)
    categorized = categorize_links(links, base_url)

    # Get crawlable links
    crawlable = []
    for category in ["api_docs", "endpoints", "reference", "guides", "auth", "examples"]:
        crawlable.extend(categorized[category])

    result = {
        "base_url": base_url,
        "total_links": len(links),
        "categorized": {
            "api_docs": len(categorized["api_docs"]),
            "endpoints": len(categorized["endpoints"]),
            "reference": len(categorized["reference"]),
            "guides": len(categorized["guides"]),
            "auth": len(categorized["auth"]),
            "examples": len(categorized["examples"]),
            "related_api": len(categorized["related_api"]),
            "other": len(categorized["other"]),
        },
        "crawlable_count": len(crawlable),
        "crawlable_links": crawlable[:20],  # Top 20 most relevant
        "all_categorized": categorized,
    }

    # Save or print
    if output_file:
        if save_links_to_file(result, output_file):
            print(f"✅ Links saved to {output_file}")
            print(f"   Total: {len(links)} links")
            print(f"   Crawlable: {len(crawlable)} links")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
