#!/usr/bin/env python3
"""
Interactive fallback for manually defining API endpoints when auto-detection fails.
"""

import json
import sys


def ask_api_details() -> dict:
    """Interactive Q&A for API details."""
    print("\n=== API Configuration ===\n")

    title = input("API Title (e.g., 'Petstore API'): ").strip() or "API"
    version = input("API Version (default: 1.0.0): ").strip() or "1.0.0"
    base_url = (
        input("Base URL (e.g., https://api.example.com): ").strip() or "http://localhost:8000"
    )
    description = input("Description (optional): ").strip() or ""

    return {
        "title": title,
        "version": version,
        "base_url": base_url,
        "description": description,
        "endpoints": [],
    }


def ask_endpoints(config: dict) -> dict:
    """Interactively collect endpoint definitions."""
    print("\n=== Define Endpoints ===")
    print("Enter endpoint details. Leave method blank to stop.\n")

    endpoint_count = 0
    while True:
        endpoint_count += 1
        print(f"Endpoint {endpoint_count}:")

        method = input("  Method (GET/POST/PUT/DELETE/PATCH, or blank to finish): ").strip().upper()
        if not method:
            break

        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            print(f"  Invalid method: {method}")
            continue

        path = input("  Path (e.g., /users, /posts/{id}): ").strip()
        if not path:
            print("  Path required")
            continue

        description = input("  Description (optional): ").strip() or f"{method} {path}"
        tag = input("  Tag/Category (default: 'default'): ").strip() or "default"

        config["endpoints"].append(
            {"method": method, "path": path, "description": description, "tag": tag}
        )

        print()

    return config


def main():
    """Main interactive flow."""
    print("API Documentation to OpenAPI Generator - Interactive Mode\n")

    config = ask_api_details()
    config = ask_endpoints(config)

    if not config["endpoints"]:
        print("No endpoints defined. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Output as JSON for downstream processing
    print("\n" + json.dumps(config, indent=2))


if __name__ == "__main__":
    main()
