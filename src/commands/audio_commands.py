"""Click commands for audio (oral arguments) resource"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from ..pagination import paginate_endpoint
from pathlib import Path


@click.group()
def audio():
    """Manage oral argument recordings"""
    pass


@audio.command("list")
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
@click.option("--court", help="Filter by court")
@click.option("--year", type=int, help="Filter by year")
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
)
@click.option("--output", "output_path", default="./output", type=click.Path())
def list_audio(limit, max_pages, offset, court, year, output_format, output_path):
    """List oral argument recordings"""
    client = CourtListenerClient()

    params = {"page_size": 100 if limit == 0 else max(limit, 1)}
    if court:
        params["docket__court"] = court
    if year:
        params["date_argued_gte"] = f"{year}-01-01"
        params["date_argued_lte"] = f"{year}-12-31"

    try:
        output_data = paginate_endpoint(
            fetch_page=lambda request_params: client.get(
                "/audio/", params=request_params
            ),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
            progress_logger=lambda page, page_count, accumulated, target: click.echo(
                f"→ Page {page}: +{page_count} recordings "
                f"(accumulated {accumulated}/{target if target is not None else 'all'})"
            ),
        )

        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)

        if "results" in output_data:
            if output_format == "json":
                filepath = save_json(output_data, output_dir)
            elif output_format == "csv":
                filepath = save_csv(output_data["results"], output_dir)
            else:  # xlsx
                filepath = save_xlsx(output_data["results"], output_dir)

            click.echo(f"✓ Found {output_data.get('count', 0)} total recordings")
            click.echo(f"✓ Exported {output_data.get('returned_count', 0)} recordings")
            click.echo(f"✓ Fetched {output_data.get('pages_fetched', 0)} page(s)")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No audio found")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@audio.command("count")
@click.option("--court", help="Filter by court")
@click.option("--year", type=int, help="Filter by year")
def count_audio(court, year):
    """Return total matching recordings count"""
    client = CourtListenerClient()

    params = {"page_size": 1}
    if court:
        params["docket__court"] = court
    if year:
        params["date_argued_gte"] = f"{year}-01-01"
        params["date_argued_lte"] = f"{year}-12-31"

    try:
        result = client.get("/audio/", params=params)
        click.echo(result.get("count", 0))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@audio.command("get")
@click.argument("audio_id", type=int)
def get_audio(audio_id):
    """Get audio details by ID"""
    client = CourtListenerClient()

    try:
        result = client.get(f"/audio/{audio_id}/")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
