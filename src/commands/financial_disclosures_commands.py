"""Click commands for financial disclosures and sub-resources.

Covers: financial-disclosures, investments, disclosure-positions,
agreements, non-investment-incomes, gifts, debts.
"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from ..pagination import paginate_endpoint
from pathlib import Path


def _list_endpoint(
    endpoint: str,
    resource_label: str,
    extra_params: dict,
    limit: int,
    max_pages: int,
    output_format: str,
    output_path: str,
):
    """Shared list logic for all financial sub-resources."""
    client = CourtListenerClient()

    params = {"page_size": 100 if limit == 0 else max(limit, 1), **extra_params}

    try:
        output_data = paginate_endpoint(
            fetch_page=lambda p: client.get(endpoint, params=p),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
            progress_logger=lambda page, page_count, acc, target: click.echo(
                f"→ Page {page}: +{page_count} {resource_label} "
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

            click.echo(f"✓ Found {output_data.get('count', 0)} total {resource_label}")
            click.echo(
                f"✓ Exported {output_data.get('returned_count', 0)} {resource_label}"
            )
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


# ─── Top-level group ──────────────────────────────────────────────────────────


@click.group()
def financial():
    """Financial disclosure records for federal judges (Ethics in Government Act)"""
    pass


# ─── Disclosures ──────────────────────────────────────────────────────────────


@financial.command("list")
@click.option("--person", default=None, type=int, help="Filter by judge person ID")
@click.option("--year", default=None, type=int, help="Filter by disclosure year")
@click.option("--limit", default=20, type=int)
@click.option("--max-pages", default=10, type=int)
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
)
@click.option("--output", "output_path", default="./output", type=click.Path())
def list_disclosures(person, year, limit, max_pages, output_format, output_path):
    """List financial disclosure records"""
    extra = {}
    if person is not None:
        extra["person"] = person
    if year is not None:
        extra["year"] = year
    _list_endpoint(
        "/financial-disclosures/",
        "disclosures",
        extra,
        limit,
        max_pages,
        output_format,
        output_path,
    )


@financial.command("get")
@click.argument("disclosure_id", type=int)
def get_disclosure(disclosure_id):
    """Get a specific financial disclosure by ID"""
    client = CourtListenerClient()
    try:
        result = client.get(f"/financial-disclosures/{disclosure_id}/")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


# ─── Investments ──────────────────────────────────────────────────────────────


@financial.command("investments")
@click.option(
    "--disclosure", default=None, type=int, help="Filter by financial disclosure ID"
)
@click.option(
    "--redacted",
    default=None,
    type=bool,
    help="Filter to rows with redacted data (True/False)",
)
@click.option(
    "--gross-value-code",
    default=None,
    help="Filter by gross value code (e.g. P4 for >$50M)",
)
@click.option("--limit", default=20, type=int)
@click.option("--max-pages", default=10, type=int)
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
)
@click.option("--output", "output_path", default="./output", type=click.Path())
def list_investments(
    disclosure, redacted, gross_value_code, limit, max_pages, output_format, output_path
):
    """List investment income holdings for financial disclosures"""
    extra = {}
    if disclosure is not None:
        extra["financial_disclosure"] = disclosure
    if redacted is not None:
        extra["redacted"] = redacted
    if gross_value_code:
        extra["gross_value_code"] = gross_value_code
    _list_endpoint(
        "/investments/",
        "investments",
        extra,
        limit,
        max_pages,
        output_format,
        output_path,
    )


# ─── Gifts ────────────────────────────────────────────────────────────────────


@financial.command("gifts")
@click.option(
    "--disclosure", default=None, type=int, help="Filter by financial disclosure ID"
)
@click.option(
    "--redacted", default=None, type=bool, help="Filter to rows with redacted data"
)
@click.option("--limit", default=20, type=int)
@click.option("--max-pages", default=10, type=int)
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
)
@click.option("--output", "output_path", default="./output", type=click.Path())
def list_gifts(disclosure, redacted, limit, max_pages, output_format, output_path):
    """List gifts received by judges in financial disclosures"""
    extra = {}
    if disclosure is not None:
        extra["financial_disclosure"] = disclosure
    if redacted is not None:
        extra["redacted"] = redacted
    _list_endpoint(
        "/gifts/", "gifts", extra, limit, max_pages, output_format, output_path
    )


# ─── Debts ────────────────────────────────────────────────────────────────────


@financial.command("debts")
@click.option(
    "--disclosure", default=None, type=int, help="Filter by financial disclosure ID"
)
@click.option(
    "--redacted", default=None, type=bool, help="Filter to rows with redacted data"
)
@click.option("--limit", default=20, type=int)
@click.option("--max-pages", default=10, type=int)
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
)
@click.option("--output", "output_path", default="./output", type=click.Path())
def list_debts(disclosure, redacted, limit, max_pages, output_format, output_path):
    """List liabilities reported in financial disclosures"""
    extra = {}
    if disclosure is not None:
        extra["financial_disclosure"] = disclosure
    if redacted is not None:
        extra["redacted"] = redacted
    _list_endpoint(
        "/debts/", "debts", extra, limit, max_pages, output_format, output_path
    )


# ─── Agreements ───────────────────────────────────────────────────────────────


@financial.command("agreements")
@click.option(
    "--disclosure", default=None, type=int, help="Filter by financial disclosure ID"
)
@click.option("--limit", default=20, type=int)
@click.option("--max-pages", default=10, type=int)
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
)
@click.option("--output", "output_path", default="./output", type=click.Path())
def list_agreements(disclosure, limit, max_pages, output_format, output_path):
    """List agreements or arrangements reported in financial disclosures"""
    extra = {}
    if disclosure is not None:
        extra["financial_disclosure"] = disclosure
    _list_endpoint(
        "/agreements/",
        "agreements",
        extra,
        limit,
        max_pages,
        output_format,
        output_path,
    )


# ─── Non-investment incomes ───────────────────────────────────────────────────


@financial.command("non-investment-incomes")
@click.option(
    "--disclosure", default=None, type=int, help="Filter by financial disclosure ID"
)
@click.option("--limit", default=20, type=int)
@click.option("--max-pages", default=10, type=int)
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
)
@click.option("--output", "output_path", default="./output", type=click.Path())
def list_non_investment_incomes(
    disclosure, limit, max_pages, output_format, output_path
):
    """List non-investment earned income (≥$200) in financial disclosures"""
    extra = {}
    if disclosure is not None:
        extra["financial_disclosure"] = disclosure
    _list_endpoint(
        "/non-investment-incomes/",
        "non-investment-incomes",
        extra,
        limit,
        max_pages,
        output_format,
        output_path,
    )


# ─── Disclosure positions (officer/director roles, separate from judge positions) ─


@financial.command("disclosure-positions")
@click.option(
    "--disclosure", default=None, type=int, help="Filter by financial disclosure ID"
)
@click.option("--limit", default=20, type=int)
@click.option("--max-pages", default=10, type=int)
@click.option(
    "--format",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "xlsx"]),
)
@click.option("--output", "output_path", default="./output", type=click.Path())
def list_disclosure_positions(disclosure, limit, max_pages, output_format, output_path):
    """List outside positions held (officer, director, trustee) from financial disclosures"""
    extra = {}
    if disclosure is not None:
        extra["financial_disclosure"] = disclosure
    _list_endpoint(
        "/disclosure-positions/",
        "disclosure-positions",
        extra,
        limit,
        max_pages,
        output_format,
        output_path,
    )
