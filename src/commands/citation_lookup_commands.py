"""Click commands for citation-lookup resource (POST endpoint).

Parses and verifies legal citations against CourtListener's 18M+ citation database.
"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json
from pathlib import Path


@click.group()
def citation_lookup():
    """Look up and verify legal citations (useful for detecting AI hallucinations)"""
    pass


@citation_lookup.command("text")
@click.option(
    "--text",
    required=True,
    help="Blob of text to scan for citations (max 64,000 characters)",
)
@click.option("--format", "output_format", default="json", type=click.Choice(["json"]))
@click.option("--output", "output_path", default="./output", type=click.Path())
def lookup_text(text, output_format, output_path):
    """Find and verify all citations in a block of text.

    Limits: 250 citations per request, 60 valid citations/minute, 64,000 chars max.
    Does not look up statutes, id., or supra citations.
    """
    if len(text) > 64000:
        click.echo("Error: text exceeds 64,000 character limit", err=True)
        raise SystemExit(1)

    client = CourtListenerClient()

    try:
        result = client.request("POST", "/citation-lookup/", json={"text": text})

        results = result if isinstance(result, list) else []
        found = [r for r in results if r.get("status") == 200]
        not_found = [r for r in results if r.get("status") == 404]
        ambiguous = [r for r in results if r.get("status") == 300]
        throttled = [r for r in results if r.get("status") == 429]

        click.echo(f"✓ Total citations parsed: {len(results)}")
        click.echo(
            f"  Found: {len(found)}, Not found: {len(not_found)}, "
            f"Ambiguous: {len(ambiguous)}, Throttled: {len(throttled)}"
        )

        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        filepath = save_json({"results": results, "count": len(results)}, output_dir)
        click.echo(f"✓ Saved to {filepath}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@citation_lookup.command("citation")
@click.option("--volume", required=True, type=int, help="Volume number")
@click.option("--reporter", required=True, help='Reporter abbreviation (e.g. "U.S.")')
@click.option("--page", required=True, help="Page number")
@click.option("--output", "output_path", default="./output", type=click.Path())
def lookup_citation(volume, reporter, page, output_path):
    """Look up a single citation by volume, reporter, and page."""
    client = CourtListenerClient()

    try:
        result = client.request(
            "POST",
            "/citation-lookup/",
            json={"volume": volume, "reporter": reporter, "page": page},
        )

        results = result if isinstance(result, list) else []
        click.echo(json.dumps(results, indent=2))

        if results:
            first = results[0]
            status = first.get("status")
            if status == 200:
                click.echo(f"✓ Found: {first.get('citation')}")
            elif status == 404:
                click.echo(
                    f"✗ Not found: {first.get('citation')} — {first.get('error_message')}"
                )
            elif status == 300:
                click.echo(
                    f"⚠ Ambiguous: {first.get('citation')} — "
                    f"{len(first.get('clusters', []))} possible matches"
                )
        else:
            click.echo("No citations returned")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
