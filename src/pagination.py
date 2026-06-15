"""Pagination utilities for CourtListener list-style endpoints."""

import time
from urllib.parse import parse_qs, urlparse
from typing import Any, Callable, Dict, List, Optional
from .client import DailyQuotaExceeded
from .config import config

ProgressLogger = Callable[[int, int, int, Optional[int]], None]


def paginate_endpoint(
    fetch_page: Callable[[Dict[str, Any]], Dict[str, Any]],
    initial_params: Dict[str, Any],
    limit: int,
    max_pages: int,
    progress_logger: Optional[ProgressLogger] = None,
    delay: Optional[float] = None,
) -> Dict[str, Any]:
    """Fetch paginated results until result or page limits are reached.

    Semantics:
    - limit > 0: stop after collecting that many rows.
    - limit == 0 and max_pages > 0: no row limit, stop at page cap.
    - limit == 0 and max_pages == 0: fetch until API has no `next`.
    """
    if limit < 0:
        raise ValueError("--limit must be >= 0")
    if max_pages < 0:
        raise ValueError("--max-pages must be >= 0")

    inter_page_delay = delay if delay is not None else config.inter_page_delay
    target_total = None if limit == 0 else limit
    all_results: List[Dict[str, Any]] = []
    total_count = 0
    next_url: Optional[str] = None
    pages_fetched = 0

    while True:
        if max_pages > 0 and pages_fetched >= max_pages:
            break

        request_params = initial_params if next_url is None else _next_params(next_url)
        try:
            result = fetch_page(request_params)
        except DailyQuotaExceeded as exc:
            print(f'  ✗ {exc}')
            return {
                "count": total_count,
                "returned_count": len(all_results),
                "pages_fetched": pages_fetched,
                "results": all_results,
                "partial": True,
            }
        pages_fetched += 1

        raw_count = result.get("count")
        if isinstance(raw_count, int):
            total_count = raw_count
        page_results = result.get("results", []) or []
        if not isinstance(page_results, list):
            page_results = []

        all_results.extend(page_results)
        if progress_logger:
            progress_logger(pages_fetched, len(page_results), len(all_results), target_total)

        if target_total is not None and len(all_results) >= target_total:
            all_results = all_results[:target_total]
            break

        next_url = result.get("next")
        if not next_url or not page_results:
            break

        if inter_page_delay > 0:
            time.sleep(inter_page_delay)

    return {
        "count": total_count,
        "returned_count": len(all_results),
        "pages_fetched": pages_fetched,
        "results": all_results,
    }


def _next_params(next_url: str) -> Dict[str, Any]:
    parsed_qs = parse_qs(urlparse(next_url).query)
    params: Dict[str, Any] = {}
    for key, values in parsed_qs.items():
        if values:
            params[key] = values[0]
    return params
