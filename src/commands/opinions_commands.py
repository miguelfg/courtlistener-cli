"""Click commands for opinions resource"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from ..pagination import paginate_endpoint
from pathlib import Path


@click.group()
def opinions():
    """Manage opinions (court decisions)"""
    pass


@opinions.command("list")
@click.option(
    "--limit",
    default=20,
    type=int,
    help="Total results to export; use 0 with --max-pages 0 to export all results",
)
@click.option(
    "--max-pages", default=10, type=int, help="Maximum pages to fetch (0 = no page cap)"
)
@click.option("--offset", default=0, help="Pagination offset")
@click.option("--search", default=None, help="Full-text search (via /search/ endpoint)")
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
    help="Output format",
)
@click.option(
    "--output",
    "output_path",
    default="./output",
    type=click.Path(),
    help="Output directory",
)
def list_opinions(limit, max_pages, offset, search, output_format, output_path):
    """List opinions with pagination"""
    client = CourtListenerClient()

    # /opinions/ has no full-text filter in v4 — full-text queries go to /search/
    endpoint = "/search/" if search else "/opinions/"
    params = {"page_size": 100 if limit == 0 else max(limit, 1)}
    if search:
        params.update({"q": search, "type": "o"})

    try:
        output_data = paginate_endpoint(
            fetch_page=lambda request_params: client.get(
                endpoint, params=request_params
            ),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
            progress_logger=lambda page, page_count, accumulated, target: click.echo(
                f"→ Page {page}: +{page_count} opinions "
                f"(accumulated {accumulated}/{target if target is not None else 'all'})"
            ),
        )

        # Export results
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)

        if "results" in output_data:
            if output_format == "json":
                filepath = save_json(output_data, output_dir)
            elif output_format == "csv":
                filepath = save_csv(output_data["results"], output_dir)
            else:  # xlsx
                filepath = save_xlsx(output_data["results"], output_dir)

            click.echo(f"✓ Found {output_data.get('count', 0)} total opinions")
            click.echo(f"✓ Exported {output_data.get('returned_count', 0)} opinions")
            click.echo(f"✓ Fetched {output_data.get('pages_fetched', 0)} page(s)")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No results found")
    except ValueError as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)
    except Exception as e:
        error = str(e)
        if "401" in error or "Unauthorized" in error:
            click.echo(
                "Authentication failed. Set COURTLISTENER_API_TOKEN with your API token."
            )
        else:
            click.echo(f"Error: {error}")
        raise SystemExit(1)


@opinions.command("count")
@click.option("--search", default=None, help="Full-text search (via /search/ endpoint)")
def count_opinions(search):
    """Return total matching opinions count"""
    client = CourtListenerClient()

    try:
        if search:
            # /opinions/ has no full-text filter in v4 — full text lives in /search/
            result = client.get(
                "/search/", params={"q": search, "type": "o", "limit": 1}
            )
            click.echo(result.get("count", 0))
        else:
            click.echo(client.count("/opinions/"))
    except Exception as e:
        error = str(e)
        if "401" in error or "Unauthorized" in error:
            click.echo(
                "Authentication failed. Set COURTLISTENER_API_TOKEN with your API token.",
                err=True,
            )
        else:
            click.echo(f"Error: {error}", err=True)
        raise SystemExit(1)


@opinions.command("get")
@click.argument("opinion_id", type=int)
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
)
def get_opinion(opinion_id, output_format):
    """Get a specific opinion"""
    client = CourtListenerClient()

    try:
        result = client.get(f"/opinions/{opinion_id}/")

        if output_format == "json":
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Opinion {opinion_id} retrieved successfully")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
