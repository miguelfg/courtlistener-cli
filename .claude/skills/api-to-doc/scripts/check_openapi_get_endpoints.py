#!/usr/bin/env python3
"""
Validate GET endpoints in a generated OpenAPI YAML using curl probes.
"""

import argparse
import subprocess
import sys
from urllib.parse import urljoin

import yaml

EXISTENCE_STATUS_CODES = {400, 401, 403, 405, 406, 409, 415, 422, 429}


def probe(url: str, timeout: int) -> tuple[bool, int]:
    """Probe URL with curl and return (exists, status_code)."""
    try:
        result = subprocess.run(
            [
                "curl",
                "-s",
                "-L",
                "-o",
                "/dev/null",
                "-w",
                "%{http_code}",
                "--max-time",
                str(timeout),
                url,
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 2,
            check=False,
        )
        status_text = (result.stdout or "").strip()
        if not status_text.isdigit():
            return False, 0
        code = int(status_text)
        if 200 <= code < 400 or code in EXISTENCE_STATUS_CODES:
            return True, code
        return False, code
    except Exception:
        return False, 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check GET endpoint existence from OpenAPI YAML via curl."
    )
    parser.add_argument("openapi_yaml", help="Path to OpenAPI YAML file")
    parser.add_argument("--timeout", type=int, default=8, help="curl timeout per endpoint")
    parser.add_argument(
        "--fail-on-any-get-failure",
        action="store_true",
        help="Exit non-zero if any probed GET endpoint fails.",
    )
    args = parser.parse_args()

    with open(args.openapi_yaml, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f) or {}

    servers = spec.get("servers") or []
    if not servers or not servers[0].get("url"):
        print("Error: missing servers[0].url in OpenAPI spec", file=sys.stderr)
        return 2

    base_url = servers[0]["url"].rstrip("/") + "/"
    paths = spec.get("paths") or {}

    attempted = passed = failed = 0
    print(f"Base URL: {base_url}")

    for path, operations in paths.items():
        if "get" not in (operations or {}):
            continue
        if "{" in path and "}" in path:
            # Skip templated paths unless caller provides concrete substitutions.
            continue

        attempted += 1
        target = urljoin(base_url, path.lstrip("/"))
        exists, status = probe(target, args.timeout)
        status_label = "PASS" if exists else "FAIL"
        print(f"[{status_label}] GET {path} -> HTTP {status or '000'}")
        if exists:
            passed += 1
        else:
            failed += 1

    print(f"\nSummary: attempted={attempted} passed={passed} failed={failed}")

    if attempted > 0 and passed == 0:
        return 1
    if args.fail_on_any_get_failure and failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
