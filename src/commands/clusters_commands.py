"""Click commands for clusters (opinion clusters) resource"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from ..pagination import paginate_endpoint
from pathlib import Path


@click.group()
def clusters():
    """Manage opinion clusters (groups of decisions for a single case)"""
    pass


@clusters.command("list")
@click.option(
    "--limit",
    default=20,
    type=int,
    help="Total results to export; 0 with --max-pages 0 = all results",
)
@click.option(
    "--max-pages", default=10, type=int, help="Maximum pages to fetch (0 = no page cap)"
)
@click.option("--docket", default=None, type=int, help="Filter by docket ID")
@click.option(
    "--docket-number",
    default=None,
    help="Filter by docket number (docket__docket_number)",
)
@click.option(
    "--court", default=None, help="Filter by court ID via join (docket__court)"
)
@click.option(
    "--date-filed-after", default=None, help="Filed on or after ISO-8601 date"
)
@click.option(
    "--date-filed-before", default=None, help="Filed on or before ISO-8601 date"
)
@click.option("--order-by", default=None, help="Sort field, prefix - for descending")
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
)
@click.option("--output", "output_path", default="./output", type=click.Path())
def list_clusters(
    limit,
    max_pages,
    docket,
    docket_number,
    court,
    date_filed_after,
    date_filed_before,
    order_by,
    output_format,
    output_path,
):
    """List opinion clusters with pagination"""
    client = CourtListenerClient()

    params = {"page_size": 100 if limit == 0 else max(limit, 1)}
    if docket:
        params["docket"] = docket
    if docket_number:
        params["docket__docket_number"] = docket_number
    if court:
        params["docket__court"] = court
    if date_filed_after:
        params["date_filed__gte"] = date_filed_after
    if date_filed_before:
        params["date_filed__lte"] = date_filed_before
    if order_by:
        params["order_by"] = order_by

    try:
        output_data = paginate_endpoint(
            fetch_page=lambda p: client.get("/clusters/", params=p),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
            progress_logger=lambda page, page_count, acc, target: click.echo(
                f"→ Page {page}: +{page_count} clusters "
                f"(accumulated {acc}/{target if target is not None else 'all'})"
            ),
        )

        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)

        if "results" in output_data:
            if output_format == "json":
                filepath = save_json(output_data, output_dir)
            elif output_format == "csv":
                filepath = save_csv(output_data["results"], output_dir)
            else:
                filepath = save_xlsx(output_data["results"], output_dir)

            click.echo(f"✓ Found {output_data.get('count', 0)} total clusters")
            click.echo(f"✓ Exported {output_data.get('returned_count', 0)} clusters")
            click.echo(f"✓ Fetched {output_data.get('pages_fetched', 0)} page(s)")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No results found")
    except Exception as e:
        error = str(e)
        if "401" in error or "Unauthorized" in error:
            click.echo(
                "Authentication failed. Set COURTLISTENER_API_TOKEN with your API token."
            )
        else:
            click.echo(f"Error: {error}")
        raise SystemExit(1)


@clusters.command("get")
@click.argument("cluster_id", type=int)
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
)
def get_cluster(cluster_id, output_format):
    """Get a specific opinion cluster by ID"""
    client = CourtListenerClient()

    try:
        result = client.get(f"/clusters/{cluster_id}/")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@clusters.command("count")
@click.option("--docket", default=None, type=int, help="Filter by docket ID")
@click.option("--court", default=None, help="Filter by court ID (docket__court)")
def count_clusters(docket, court):
    """Return total matching clusters count"""
    client = CourtListenerClient()

    params = {}
    if docket:
        params["docket"] = docket
    if court:
        params["docket__court"] = court

    try:
        click.echo(client.count("/clusters/", params))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
