#!/usr/bin/env python3
"""
Fetch API documentation from a URL using cURL and parse common documentation patterns.
Supports HTML documentation, Swagger/OpenAPI specs, and API reference pages.
Fail-fast: if documentation cannot be reliably retrieved/extracted, exit non-zero.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, deque
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qsl, urljoin, urlparse

from html_processing import html_to_markdown, truncate_lines

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency guard
    yaml = None


def get_tmp_cache_dir() -> Path:
    """Get or create the /tmp cache directory for API documentation."""
    cache_dir = Path("/tmp/api-to-doc-cache")
    cache_dir.mkdir(exist_ok=True, parents=True)
    return cache_dir


def get_html_cache_path(url: str) -> Path:
    """Generate a unique cache file path for a URL."""
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    parsed = urlparse(url)
    domain = parsed.netloc.replace(".", "_")
    path_part = parsed.path.replace("/", "_")[:30]
    filename = f"{domain}_{path_part}_{url_hash}.html"
    return get_tmp_cache_dir() / filename


def save_html_page(url: str, content: str) -> Optional[Path]:
    """Save HTML page to /tmp cache directory."""
    try:
        cache_path = get_html_cache_path(url)
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(content)
        return cache_path
    except Exception as e:
        print(f"Warning: Could not save HTML to cache: {e}", file=sys.stderr)
        return None


def fetch_url(url: str, use_cache: bool = True) -> tuple:
    """Fetch content from URL using cURL.

    Returns: (content, cache_path)
    """
    # Check cache first if enabled
    if use_cache:
        cache_path = get_html_cache_path(url)
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return f.read(), cache_path
            except Exception:
                pass

    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "-A", "Mozilla/5.0", url],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout:
            # Save to cache
            cache_path = save_html_page(url, result.stdout)
            return result.stdout, cache_path
        # If cURL fails or returns empty, fail-fast upstream.
        print(f"⚠️  cURL returned limited results for {url}.", file=sys.stderr)
        return result.stdout if result.stdout else "", None
    except FileNotFoundError:
        print("⚠️  curl not found.", file=sys.stderr)
        return "", None


def extract_links_from_html(content: str, base_url: str) -> set[str]:
    """Extract and normalize links from HTML."""
    links = set()
    href_pattern = r'href=["\']((?:https?://|/)[^\s"\'<>]+)'
    for match in re.finditer(href_pattern, content, re.IGNORECASE):
        href = match.group(1)
        if href.startswith("/"):
            parsed = urlparse(base_url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        links.add(href.split("#")[0])
    return links


def get_root_domain(hostname: str) -> str:
    """Return a coarse root domain (last two labels)."""
    if not hostname:
        return ""
    parts = hostname.split(".")
    if len(parts) < 2:
        return hostname
    return ".".join(parts[-2:])


def filter_api_doc_links(links: set[str], start_url: str, max_depth: int = 6) -> list[str]:
    """Keep same-domain API-doc-like links for crawling."""
    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc
    base_root_domain = get_root_domain(base_domain)
    start_path = parsed_start.path
    start_root = "/" + "/".join([p for p in start_path.split("/") if p][:2]) if start_path else ""

    filtered = []
    for url in links:
        parsed = urlparse(url)
        if get_root_domain(parsed.netloc) != base_root_domain:
            continue
        if parsed.query and "lang=" in parsed.query.lower():
            continue
        path_lower = parsed.path.lower()
        if any(
            skip in path_lower
            for skip in [
                "/search",
                "/blog",
                "/pricing",
                "/contact",
                "/about",
                "/support",
                "/login",
                "/signup",
                "/dashboard",
                "/changelog",
            ]
        ):
            continue
        # Prefer links under the same docs subtree.
        if start_root and not parsed.path.startswith(start_root):
            # Keep links near API docs only (avoid unrelated docs sections).
            if "/api/" not in path_lower and not path_lower.endswith("/api"):
                continue
        if parsed.path.count("/") > max_depth:
            continue
        filtered.append(url)
    return sorted(set(filtered))


def discover_openapi_links(content: str, base_url: str) -> list[str]:
    """Find likely OpenAPI/Swagger spec URLs from HTML."""
    candidates = set()

    href_pattern = r'href=["\']([^"\']+)["\']'
    for raw_href in re.findall(href_pattern, content, re.IGNORECASE):
        href = urljoin(base_url, raw_href)
        href_lower = href.lower()
        if any(token in href_lower for token in ["openapi", "swagger", "spec"]) and any(
            href_lower.endswith(ext) for ext in [".json", ".yaml", ".yml"]
        ):
            candidates.add(href)

    # Conventional spec paths on the same host.
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    for path in [
        "/openapi.json",
        "/openapi.yaml",
        "/openapi.yml",
        "/swagger.json",
        "/v1/openapi.json",
        "/api/openapi.json",
    ]:
        candidates.add(root + path)

    return sorted(candidates)


def fetch_first_openapi_spec(
    content: str, base_url: str
) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Try discovered candidate links and return first parseable OpenAPI/Swagger spec."""
    for candidate in discover_openapi_links(content, base_url):
        spec_text, _ = fetch_url(candidate, use_cache=False)
        if not spec_text:
            continue

        parsed_spec = None
        try:
            parsed_spec = json.loads(spec_text)
        except Exception:
            if yaml is not None:
                try:
                    parsed_spec = yaml.safe_load(spec_text)
                except Exception:
                    parsed_spec = None

        if isinstance(parsed_spec, dict) and any(
            key in parsed_spec for key in ["openapi", "swagger", "paths"]
        ):
            return parsed_spec, candidate

    return None, None


def discover_markdown_links(content: str, base_url: str) -> list[str]:
    """Find markdown documentation links in the HTML page."""
    candidates = []
    for raw_href in re.findall(r'href=["\']([^"\']+)["\']', content, re.IGNORECASE):
        href = urljoin(base_url, raw_href)
        href_lower = href.lower()
        if (
            href_lower.endswith(".md")
            or "markdown" in href_lower
            or "view-as-markdown" in href_lower
        ):
            candidates.append(href)
    return sorted(set(candidates))


def fetch_markdown_doc(content: str, base_url: str) -> tuple[Optional[str], Optional[str]]:
    """Fetch preferred markdown doc content when available."""
    for md_link in discover_markdown_links(content, base_url):
        md_text, _ = fetch_url(md_link, use_cache=False)
        if md_text and len(md_text.strip()) > 200:
            return md_text, md_link
    return None, None


def crawl_and_extract_related_endpoints(
    start_url: str,
    use_cache: bool = True,
    max_pages: int = 80,
    max_depth: int = 6,
) -> tuple[list[dict], str]:
    """
    Crawl related docs pages and aggregate extracted endpoints.
    Returns (endpoints, detected_base_url).
    """
    visited = set()
    queue = deque([start_url.split("#")[0]])
    all_endpoints = []
    base_url_candidates = []
    pages = 0

    while queue and pages < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        pages += 1

        content, _ = fetch_url(url, use_cache=use_cache)
        if not content:
            continue

        page_endpoints = extract_endpoints_from_html(content)
        all_endpoints.extend(page_endpoints)
        base_url_candidates.append(extract_base_url(url, content))

        links = extract_links_from_html(content, url)
        crawlable = filter_api_doc_links(links, start_url, max_depth=max_depth)
        # Keep queue growth bounded but allow broad exploration.
        for link in crawlable[:40]:
            if link not in visited:
                queue.append(link)

    dedup = {}
    for ep in all_endpoints:
        key = (ep.get("method", "GET"), ep.get("path", "/"))
        dedup[key] = ep

    final_base_url = ""
    if base_url_candidates:
        counts = Counter(base_url_candidates)
        final_base_url = counts.most_common(1)[0][0]

    return list(dedup.values()), final_base_url


def detect_api_type(content: str, url: str) -> str:
    """Detect if content is OpenAPI, Swagger, or HTML documentation."""
    content_lower = content.lower()

    # Check for existing OpenAPI/Swagger specs
    if "openapi:" in content_lower or "swagger:" in content_lower:
        return "openapi"

    if '"openapi"' in content_lower or '"swagger"' in content_lower:
        return "swagger_json"

    # Check for common API documentation patterns
    if any(
        pattern in content_lower
        for pattern in [
            "api endpoint",
            "rest api",
            "http method",
            "request example",
            "response example",
            "authentication",
        ]
    ):
        return "html_docs"

    # Check URL hints
    if any(
        pattern in url.lower()
        for pattern in [
            "/api/docs",
            "/docs",
            "/swagger",
            "/openapi",
            "/api-reference",
            "/api/reference",
        ]
    ):
        return "html_docs"

    return "unknown"


class HTMLContentExtractor(HTMLParser):
    """Parse HTML to extract text, code blocks, and structure."""

    def __init__(self):
        super().__init__()
        self.text_content = []
        self.code_blocks = []
        self.current_code = ""
        self.in_code = False
        self.in_pre = False
        self.headers = []

    def handle_starttag(self, tag, attrs):
        if tag in ["code", "pre"]:
            self.in_code = True
            if tag == "pre":
                self.in_pre = True
        elif tag == "h1":
            self.headers.append(("h1", ""))
        elif tag in ["h2", "h3", "h4", "h5"]:
            self.headers.append((tag, ""))

    def handle_endtag(self, tag):
        if tag in ["code", "pre"]:
            self.in_code = False
            if self.current_code.strip():
                self.code_blocks.append(self.current_code.strip())
                self.current_code = ""
            if tag == "pre":
                self.in_pre = False

    def handle_data(self, data):
        if self.in_code:
            self.current_code += data
        else:
            self.text_content.append(data)


def extract_endpoints_from_html(content: str) -> list:
    """Extract endpoints from HTML documentation with improved patterns."""
    endpoints = []

    def normalize_endpoint_path(raw_path: str) -> str:
        """Normalize example-instance paths into parameterized paths."""
        path = raw_path.split("?")[0].strip()
        if not path.startswith("/"):
            path = "/" + path

        normalized_parts = []
        for part in path.split("/"):
            if not part:
                continue
            token = part.strip()
            lowered = token.lower()

            # Keep version/static tokens untouched.
            if re.match(r"^v\d+$", lowered):
                normalized_parts.append(token)
                continue

            # Convert Stripe-like object IDs (acct_..., ch_..., *_test_...) to path params.
            # Only rewrite tokens containing digits to avoid static snake_case segments.
            has_digit = any(ch.isdigit() for ch in token)
            if has_digit:
                m_test = re.match(r"^([a-z][a-z0-9]*)_test_[A-Za-z0-9]+$", token)
                if m_test:
                    normalized_parts.append(f"{{{m_test.group(1)}_id}}")
                    continue

                m_prefixed = re.match(r"^([a-z][a-z0-9]*)_[A-Za-z0-9]+$", token)
                if m_prefixed:
                    normalized_parts.append(f"{{{m_prefixed.group(1)}_id}}")
                    continue

                # Generic long alnum IDs.
                if re.match(r"^[A-Za-z0-9]{12,}$", token):
                    normalized_parts.append("{id}")
                    continue

            normalized_parts.append(token)

        return "/" + "/".join(normalized_parts)

    # Pattern 1: Code blocks with HTTP methods (most reliable)
    http_pattern = r"(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(/[^\s<\n]+)"
    matches = re.findall(http_pattern, content)
    for method, path in matches:
        path = normalize_endpoint_path(path)
        endpoints.append(
            {
                "method": method,
                "path": path,
                "description": "",
                "parameters": [],
                "request_examples": [],
                "response_examples": [],
            }
        )

    # Pattern 2: API endpoints in headers or list items
    endpoint_pattern = (
        r"<(?:h[2-4]|li|td)>.*?(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s<]+).*?</(?:h[2-4]|li|td)>"
    )
    matches = re.findall(endpoint_pattern, content, re.IGNORECASE | re.DOTALL)
    for method, path in matches:
        path = normalize_endpoint_path(path)
        endpoints.append(
            {
                "method": method.upper(),
                "path": path,
                "description": "",
                "parameters": [],
                "request_examples": [],
                "response_examples": [],
            }
        )

    # Pattern 3: Explicit endpoint declarations without method.
    # Example: "The API endpoint /v1/forecast accepts ..."
    endpoint_only_pattern = r"api\s+endpoint[^<\n]*?(/v\d+/[a-zA-Z0-9_/\-]+)"
    for path in re.findall(endpoint_only_pattern, content, re.IGNORECASE):
        path = normalize_endpoint_path(path)
        endpoints.append(
            {
                "method": "GET",
                "path": path,
                "description": "",
                "parameters": [],
                "request_examples": [],
                "response_examples": [],
            }
        )

    # Pattern 3b: Endpoint wrapped in markup (e.g., "<mark>/v1/flood</mark>").
    endpoint_mark_pattern = r"api\s+endpoint.*?<mark>\s*(/v\d+/[a-zA-Z0-9_/\-]+)\s*</mark>"
    for path in re.findall(endpoint_mark_pattern, content, re.IGNORECASE | re.DOTALL):
        path = normalize_endpoint_path(path)
        endpoints.append(
            {
                "method": "GET",
                "path": path,
                "description": "",
                "parameters": [],
                "request_examples": [],
                "response_examples": [],
            }
        )

    # Pattern 4: Absolute API URLs in forms/links.
    absolute_api_pattern = r'https?://api[.\-][^"\'<>\s]+(/v\d+/[a-zA-Z0-9_/\-]+)'
    for path in re.findall(absolute_api_pattern, content, re.IGNORECASE):
        path = normalize_endpoint_path(path)
        endpoints.append(
            {
                "method": "GET",
                "path": path,
                "description": "",
                "parameters": [],
                "request_examples": [],
                "response_examples": [],
            }
        )

    # Deduplicate
    seen = set()
    unique = []
    for ep in endpoints:
        key = (ep["method"], ep["path"])
        if key not in seen:
            seen.add(key)
            unique.append(ep)

    return unique


def extract_parameters_for_endpoint(content: str, endpoint_path: str) -> Dict[str, List[Dict]]:
    """Extract query, path, and body parameters for a specific endpoint."""
    params = {"path": [], "query": [], "body": []}

    def _query_param_exists(name: str) -> bool:
        return any(p["name"] == name for p in params["query"])

    def _add_query_param(name: str, param_type: str = "string", required: bool = False):
        if not name or _query_param_exists(name):
            return
        params["query"].append(
            {
                "name": name,
                "type": param_type,
                "required": required,
            }
        )

    def _infer_type(type_text: str) -> str:
        t = (type_text or "").strip().lower()
        if any(k in t for k in ["int", "integer"]):
            return "integer"
        if any(k in t for k in ["float", "double", "decimal", "number"]):
            return "number"
        if "bool" in t:
            return "boolean"
        if "array" in t or "list" in t:
            return "array"
        if "object" in t or "json" in t:
            return "object"
        return "string"

    # Extract path parameters (e.g., {id}, :id, [id])
    path_param_pattern = r"[{:\[]([a-zA-Z_][a-zA-Z0-9_]*)[}\]:]"
    path_params = re.findall(path_param_pattern, endpoint_path)
    for param in path_params:
        params["path"].append({"name": param, "type": "string", "required": True})

    # Look for parameter documentation patterns near the endpoint
    context_pattern = (
        r"(?:"
        + re.escape(endpoint_path)
        + r"|"
        + endpoint_path.split("/")[1]
        + r").*?(?=(?:GET|POST|PUT|DELETE|PATCH|####|###|##|$))"
    )
    context = re.search(context_pattern, content, re.IGNORECASE | re.DOTALL)

    if context:
        context_text = context.group(0)

        # Query parameters
        query_pattern = r"(?:Query\s+Parameters|Query\s+String|Optional\s+Parameters|Parameters)[\s:]*\n(.*?)(?=(?:Request|Response|Request Body|Status|####|###|##|$))"
        query_match = re.search(query_pattern, context_text, re.IGNORECASE | re.DOTALL)
        if query_match:
            query_text = query_match.group(1)
            # Find parameter names in the context
            param_names = re.findall(
                r'(?:param|parameter|query|option)[\s:]*["\']?([a-zA-Z_][a-zA-Z0-9_]*)',
                query_text,
                re.IGNORECASE,
            )
            for name in param_names:
                if name not in [p["name"] for p in params["query"]]:
                    _add_query_param(name, "string", False)

        # Request body parameters
        body_pattern = r"(?:Request\s+Body|Body\s+Parameters|Body|Payload)[\s:]*\n(.*?)(?=(?:Response|Status|####|###|##|$))"
        body_match = re.search(body_pattern, context_text, re.IGNORECASE | re.DOTALL)
        if body_match:
            body_text = body_match.group(1)
            param_names = re.findall(r'["\']?([a-zA-Z_][a-zA-Z0-9_]*)["\']?\s*(?::|=)', body_text)
            for name in param_names:
                if name not in [p["name"] for p in params["body"]]:
                    params["body"].append({"name": name, "type": "string", "required": False})

        # Parse concrete API URL examples and query strings in endpoint context.
        decoded_context = unescape(context_text)
        absolute_url_pattern = r'https?://api[.\-][^"\'<>\s]+'
        for full_url in re.findall(absolute_url_pattern, decoded_context, re.IGNORECASE):
            try:
                parsed_url = urlparse(full_url)
                if parsed_url.path != endpoint_path:
                    continue
                for key, _ in parse_qsl(parsed_url.query, keep_blank_values=True):
                    _add_query_param(key, "string", False)
            except Exception:
                pass

        # Handle inline URL fragments like &hourly=temperature_2m in docs text.
        for key in re.findall(r"(?:\?|&)([a-zA-Z_][a-zA-Z0-9_\-]*)=", decoded_context):
            _add_query_param(key, "string", False)

    # Parse common API docs parameter tables:
    # <tr><th>param</th><td>String array</td><td>No</td>...</tr>
    table_row_pattern = (
        r"<tr[^>]*>\s*<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>"
    )
    for raw_name, raw_type, raw_required in re.findall(
        table_row_pattern, content, re.IGNORECASE | re.DOTALL
    ):
        name = re.sub(r"<[^>]+>", " ", unescape(raw_name)).strip().lower()
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_\-]*$", name):
            continue
        type_text = re.sub(r"<[^>]+>", " ", unescape(raw_type)).strip()
        req_text = re.sub(r"<[^>]+>", " ", unescape(raw_required)).strip().lower()
        required = req_text in {"yes", "required", "true"}
        _add_query_param(name, _infer_type(type_text), required)

    # Parse forms that submit directly to this endpoint and capture named inputs/selects.
    endpoint_form_pattern = (
        r'<form[^>]*action=["\']https?://[^"\']*'
        + re.escape(endpoint_path)
        + r'[^"\']*["\'][^>]*>(.*?)</form>'
    )
    for form_block in re.findall(endpoint_form_pattern, content, re.IGNORECASE | re.DOTALL):
        for name in re.findall(r'\bname=["\']([a-zA-Z_][a-zA-Z0-9_\-]*)["\']', form_block):
            _add_query_param(name, "string", False)

    return params


def extract_examples_from_content(content: str, endpoint_path: str) -> Dict[str, List[str]]:
    """Extract request and response examples for an endpoint."""
    examples = {"request": [], "response": []}

    # Find context around the endpoint
    context_pattern = (
        r"(?:" + re.escape(endpoint_path) + r").*?(?=(?:GET|POST|PUT|DELETE|PATCH|###|##|$))"
    )
    context = re.search(context_pattern, content, re.IGNORECASE | re.DOTALL)

    if not context:
        return examples

    context_text = context.group(0)

    # Extract request examples (JSON code blocks)
    request_pattern = r"(?:Request\s+Example|Example\s+Request|Request)[\s:]*\n```(?:json|javascript|js)?\s*(.*?)```"
    request_matches = re.findall(request_pattern, context_text, re.IGNORECASE | re.DOTALL)
    examples["request"].extend(request_matches)

    # Extract response examples
    response_pattern = r"(?:Response\s+Example|Example\s+Response|Response)[\s:]*\n```(?:json|javascript|js)?\s*(.*?)```"
    response_matches = re.findall(response_pattern, context_text, re.IGNORECASE | re.DOTALL)
    examples["response"].extend(response_matches)

    # Fallback: extract JSON objects from <pre> or <code> tags
    if not examples["request"] or not examples["response"]:
        json_pattern = r"(?:<pre>|<code>)(.*?)(?:</pre>|</code>)"
        json_blocks = re.findall(json_pattern, context_text, re.DOTALL)
        for block in json_blocks:
            if "{" in block:
                # Try to parse as JSON
                try:
                    json.loads(block)
                    if "request" in context_text[: context_text.find(block)].lower():
                        examples["request"].append(block.strip())
                    else:
                        examples["response"].append(block.strip())
                except json.JSONDecodeError:
                    pass

    return examples


def extract_base_url(url: str, content: str) -> str:
    """Extract base URL from documentation or use the fetched URL."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    # Prefer explicit API hosts when present in docs.
    # Supports hosts like:
    # - https://api.open-meteo.com/v1/forecast
    # - https://flood-api.open-meteo.com/v1/flood
    api_url_match = re.search(
        r"(https?://[a-zA-Z0-9.\-]*api[a-zA-Z0-9.\-]*)(?:/v\d+/[a-zA-Z0-9_/\-]*)?",
        content,
        re.IGNORECASE,
    )
    if api_url_match:
        return api_url_match.group(1).rstrip("/")

    # Try to find API base URL in content
    patterns = [
        r'base\s*(?:url|uri|endpoint)[\s:]*["\']?(https?://[^\s"\'<]+)',
        r'api\s*endpoint[\s:]*["\']?(https?://[^\s"\'<]+)',
        r'server[\s:]*["\']?(https?://[^\s"\'<]+)',
        r'https?://[^\s"\'<]+/api(?:/v\d+)?',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            url_match = match.group(0) if pattern.startswith("https") else match.group(1)
            return url_match.rstrip("/")

    return base


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch API docs and extract endpoint information.")
    parser.add_argument("url", help="API docs URL")
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable HTML caching and force fresh download",
    )
    parser.add_argument(
        "--prefer-md-extraction",
        action="store_true",
        help="Use HTML->Markdown normalized text to extract endpoints/metadata",
    )
    parser.add_argument(
        "--save-md-cache",
        action="store_true",
        help="Save a markdown companion file next to cached HTML",
    )
    parser.add_argument(
        "--md-max-lines",
        type=int,
        default=0,
        help="Truncate generated markdown cache to N lines (0 = no truncation)",
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    url = args.url
    use_cache = not args.no_cache

    content, cache_path = fetch_url(url, use_cache=use_cache)

    if not content:
        print("Failed to fetch content", file=sys.stderr)
        sys.exit(1)

    normalized_markdown = html_to_markdown(content)
    if args.md_max_lines > 0:
        normalized_markdown = truncate_lines(normalized_markdown, args.md_max_lines)

    markdown_cache_path = None
    if args.save_md_cache and cache_path:
        markdown_cache_path = cache_path.with_suffix(".md")
        markdown_cache_path.write_text(normalized_markdown, encoding="utf-8")

    # Priority 1: discover and use a linked machine-readable OpenAPI/Swagger spec if available.
    linked_spec, linked_spec_url = fetch_first_openapi_spec(content, url)
    if linked_spec is not None:
        result = {
            "url": url,
            "api_type": "openapi",
            "content_length": len(content),
            "content_preview": content[:500],
            "is_spec": True,
            "spec": linked_spec,
            "spec_source": linked_spec_url,
            "cache": {
                "saved": cache_path is not None,
                "path": str(cache_path) if cache_path else None,
                "markdown_path": str(markdown_cache_path) if markdown_cache_path else None,
                "cache_dir": str(get_tmp_cache_dir()),
            },
            "extraction_notes": [
                "Linked OpenAPI/Swagger schema discovered and prioritized over doc scraping"
            ],
        }
        print(json.dumps(result, indent=2))
        return

    api_type = detect_api_type(content, url)

    result = {
        "url": url,
        "api_type": api_type,
        "content_length": len(content),
        "content_preview": content[:500],
        "cache": {
            "saved": cache_path is not None,
            "path": str(cache_path) if cache_path else None,
            "markdown_path": str(markdown_cache_path) if markdown_cache_path else None,
            "cache_dir": str(get_tmp_cache_dir()),
        },
    }

    if api_type == "openapi" or api_type == "swagger_json":
        result["is_spec"] = True
        try:
            result["spec"] = json.loads(content)
        except json.JSONDecodeError:
            result["spec"] = None

    elif api_type == "html_docs":
        result["is_spec"] = False
        # Priority 2: prefer markdown docs when available, otherwise HTML.
        markdown_doc, markdown_source_url = fetch_markdown_doc(content, url)
        if markdown_doc:
            extraction_source = markdown_doc
            result["preferred_doc_source"] = "markdown"
            result["preferred_doc_url"] = markdown_source_url
        else:
            extraction_source = normalized_markdown if args.prefer_md_extraction else content
            result["preferred_doc_source"] = (
                "normalized_markdown" if args.prefer_md_extraction else "html"
            )
        endpoints = extract_endpoints_from_html(extraction_source)
        base_url = extract_base_url(url, extraction_source)

        # Auto-fallback: for docs sites with sparse top-level endpoints, crawl related pages.
        if len(endpoints) < 5:
            crawled_endpoints, crawled_base_url = crawl_and_extract_related_endpoints(
                url,
                use_cache=use_cache,
                max_pages=25,
                max_depth=6,
            )
            if len(crawled_endpoints) > len(endpoints):
                endpoints = crawled_endpoints
            if crawled_base_url:
                base_url = crawled_base_url

        # Strict quality gate: no endpoint extraction means retrieval was not usable.
        if not endpoints:
            print(
                "Failed to extract real API endpoints from documentation. "
                "Failing instead of generating speculative output.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Extract detailed information for each endpoint
        for endpoint in endpoints:
            endpoint["parameters"] = extract_parameters_for_endpoint(
                extraction_source, endpoint["path"]
            )
            endpoint["examples"] = extract_examples_from_content(
                extraction_source, endpoint["path"]
            )

        result["endpoints"] = endpoints
        result["base_url"] = base_url
        result["endpoint_count"] = len(endpoints)
        result["extraction_notes"] = [
            "Source preference order: linked OpenAPI schema > markdown docs > HTML pages",
            "Parameters extracted from documentation patterns",
            "Request/response examples sourced from code blocks",
            "HTML page saved to cache for link extraction",
            "Optional HTML-to-Markdown preprocessing available for long pages",
            "Automatic multi-page crawl used for sparse top-level docs",
            "Fail-fast enabled when endpoint extraction is empty",
        ]
    else:
        print(
            "Unable to determine API documentation type from fetched content. "
            "Failing instead of generating speculative output.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
