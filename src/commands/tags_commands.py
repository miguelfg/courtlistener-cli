"""Click commands for tags resource"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from ..pagination import paginate_endpoint
from pathlib import Path


@click.group()
def tags():
    """Manage user-created tags linked to dockets"""
    pass


@tags.command('list')
@click.option('--limit', default=20, type=int,
              help='Total results to export; 0 with --max-pages 0 = all results')
@click.option('--max-pages', default=10, type=int)
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output', type=click.Path())
def list_tags(limit, max_pages, output_format, output_path):
    """List user-created tags"""
    client = CourtListenerClient()

    params = {'page_size': 100 if limit == 0 else max(limit, 1)}

    try:
        output_data = paginate_endpoint(
            fetch_page=lambda p: client.get('/tag/', params=p),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
            progress_logger=lambda page, page_count, acc, target: click.echo(
                f"→ Page {page}: +{page_count} tags "
                f"(accumulated {acc}/{target if target is not None else 'all'})"
            ),
        )

        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)

        if 'results' in output_data:
            if output_format == 'json':
                filepath = save_json(output_data, output_dir)
            elif output_format == 'csv':
                filepath = save_csv(output_data['results'], output_dir)
            else:
                filepath = save_xlsx(output_data['results'], output_dir)

            click.echo(f"✓ Found {output_data.get('count', 0)} total tags")
            click.echo(f"✓ Exported {output_data.get('returned_count', 0)} tags")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No results found")
    except Exception as e:
        error = str(e)
        if "401" in error or "Unauthorized" in error:
            click.echo("Authentication failed. Set COURTLISTENER_API_TOKEN with your API token.")
        else:
            click.echo(f"Error: {error}")
        raise SystemExit(1)


@tags.command('get')
@click.argument('tag_id', type=int)
def get_tag(tag_id):
    """Get a specific tag by ID"""
    client = CourtListenerClient()

    try:
        result = client.get(f'/tag/{tag_id}/')
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
