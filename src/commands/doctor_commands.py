"""Local configuration checks for CourtListener CLI."""

from urllib.parse import urlparse

import click

from ..config import config


@click.command()
def doctor():
    """Check local configuration without making an API request."""
    valid = True

    if config.api_token:
        click.echo("✓ API token: loaded")
    else:
        click.echo("✗ COURTLISTENER_API_TOKEN is not configured")
        valid = False

    base_url = config.base_url
    parsed_url = urlparse(base_url)
    if parsed_url.scheme in {"http", "https"} and parsed_url.netloc:
        click.echo(f"✓ API base URL: {base_url}")
    else:
        click.echo(f"✗ API base URL is invalid: {base_url}")
        valid = False

    try:
        timeout = config.timeout
        if timeout <= 0:
            raise ValueError
    except ValueError:
        click.echo("✗ COURTLISTENER_TIMEOUT must be a positive integer")
        valid = False
    else:
        click.echo(f"✓ Timeout: {timeout}s")

    output_format = config.output_format
    if output_format in {"json", "csv", "xlsx"}:
        click.echo(f"✓ Output format: {output_format}")
    else:
        click.echo("✗ OUTPUT_FORMAT must be json, csv, or xlsx")
        valid = False

    if config.session_id:
        click.echo("✓ Session cookie: configured (optional)")
    else:
        click.echo("○ Session cookie: not configured (optional)")

    if not valid:
        raise SystemExit(1)
