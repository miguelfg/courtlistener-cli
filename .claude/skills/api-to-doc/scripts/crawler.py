#!/usr/bin/env python3
"""
Crawl API documentation across multiple pages to gather comprehensive endpoint information.
Uses link extraction to discover and traverse related documentation pages.
"""

import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse


def fetch_with_curl(url: str) -> Optional[str]:
    """Fetch a URL with cURL."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "-A", "Mozilla/5.0", url],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout if result.returncode == 0 else None
    except FileNotFoundError:
        print("Error: curl not found", file=sys.stderr)
        return None


def extract_links_from_html(content: str, base_url: str) -> Set[str]:
    """Extract all absolute URLs from HTML content."""
    import re

    links = set()

    # Extract from href attributes
    href_pattern = r'href=["\']((?:https?://|/)[^\s"\'<>]+)'
    for match in re.finditer(href_pattern, content, re.IGNORECASE):
        href = match.group(1)
        if href.startswith("/"):
            # Relative URL
            parsed = urlparse(base_url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        links.add(href)

    return links


def filter_crawlable(links: Set[str], base_domain: str, max_depth: int = 2) -> List[str]:
    """Filter links to crawlable documentation pages."""
    crawlable = []

    for url in links:
        parsed = urlparse(url)

        # Only same domain
        if parsed.netloc != base_domain:
            continue

        # Skip certain paths
        if any(
            skip in parsed.path.lower()
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
                "/cdn-cgi",
                "/accounts",
                "/login",
                "/signup",
            ]
        ):
            continue

        # Skip anchors and query params
        if url.endswith("#"):
            continue

        # Check path depth
        depth = parsed.path.count("/")
        if depth <= max_depth:
            crawlable.append(url)

    return sorted(list(set(crawlable)))


def crawl_documentation(start_url: str, max_pages: int = 10, max_depth: int = 2) -> Dict:
    """Crawl API documentation starting from a URL."""
    parsed = urlparse(start_url)
    base_domain = parsed.netloc

    visited = set()
    to_visit = [start_url]
    crawl_results = {
        "start_url": start_url,
        "base_domain": base_domain,
        "started_at": datetime.now().isoformat(),
        "max_pages": max_pages,
        "pages": [],
        "total_endpoints": 0,
        "total_links_found": 0,
    }

    page_count = 0

    while to_visit and page_count < max_pages:
        url = to_visit.pop(0)

        if url in visited:
            continue

        visited.add(url)
        page_count += 1

        print(f"[{page_count}/{max_pages}] Crawling: {url}", file=sys.stderr)

        # Fetch content
        content = fetch_with_curl(url)
        if not content:
            print("  ⚠️  Failed to fetch", file=sys.stderr)
            continue

        # Extract links
        links = extract_links_from_html(content, url)
        crawlable = filter_crawlable(links, base_domain, max_depth)

        print(f"  ✓ Found {len(links)} links, {len(crawlable)} crawlable", file=sys.stderr)

        # Add new crawlable links to queue
        for link in crawlable[:5]:  # Limit to top 5 per page
            if link not in visited and link not in to_visit:
                to_visit.append(link)

        # Extract endpoints from this page
        endpoints = extract_endpoints_from_content(content)

        page_result = {
            "url": url,
            "status": "success",
            "content_length": len(content),
            "links_found": len(links),
            "crawlable_links": len(crawlable),
            "endpoints": endpoints,
        }

        crawl_results["pages"].append(page_result)
        crawl_results["total_endpoints"] += len(endpoints)
        crawl_results["total_links_found"] += len(links)

    crawl_results["ended_at"] = datetime.now().isoformat()
    crawl_results["pages_crawled"] = page_count
    crawl_results["pages_visited"] = list(visited)

    return crawl_results


def extract_endpoints_from_content(content: str) -> List[Dict]:
    """Extract endpoints from HTML content."""
    import re

    endpoints = []

    # Pattern: HTTP method + path
    http_pattern = r"(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(/[^\s<\n]+)"
    matches = re.findall(http_pattern, content)

    seen = set()
    for method, path in matches:
        key = (method, path)
        if key not in seen:
            seen.add(key)
            endpoints.append({"method": method, "path": path})

    return endpoints


def main():
    """Main crawler entry point."""
    if len(sys.argv) < 2:
        print("Usage: crawler.py <start_url> [max_pages] [max_depth]")
        print("  start_url: URL to start crawling from")
        print("  max_pages: Maximum pages to crawl (default: 10)")
        print("  max_depth: Maximum URL path depth (default: 2)")
        sys.exit(1)

    start_url = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    print(f"Starting crawl from: {start_url}", file=sys.stderr)
    print(f"Max pages: {max_pages}, Max depth: {max_depth}", file=sys.stderr)
    print("", file=sys.stderr)

    results = crawl_documentation(start_url, max_pages=max_pages, max_depth=max_depth)

    print("", file=sys.stderr)
    print("✅ Crawl complete!", file=sys.stderr)
    print(f"   Pages crawled: {results['pages_crawled']}", file=sys.stderr)
    print(f"   Endpoints found: {results['total_endpoints']}", file=sys.stderr)
    print(f"   Total links discovered: {results['total_links_found']}", file=sys.stderr)

    # Output results as JSON
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
