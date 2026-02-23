"""Click commands for opinions resource"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from pathlib import Path


@click.group()
def opinions():
    """Manage opinions (court decisions)"""
    pass


@opinions.command('list')
@click.option('--limit', default=20, help='Number of results per page')
@click.option('--offset', default=0, help='Pagination offset')
@click.option('--search', default=None, help='Full-text search')
@click.option('--format', 'output_format', default='json', 
              type=click.Choice(['json', 'csv', 'xlsx']),
              help='Output format')
@click.option('--output', 'output_path', default='./output', 
              type=click.Path(),
              help='Output directory')
def list_opinions(limit, offset, search, output_format, output_path):
    """List opinions with pagination"""
    client = CourtListenerClient()
    
    params = {'limit': limit, 'offset': offset}
    if search:
        params['search'] = search
    
    try:
        result = client.get('/opinions/', params=params)

        # Export results
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)

        if 'results' in result:
            if output_format == 'json':
                filepath = save_json(result, output_dir)
            elif output_format == 'csv':
                filepath = save_csv(result['results'], output_dir)
            else:  # xlsx
                filepath = save_xlsx(result['results'], output_dir)

            click.echo(f"✓ Saved {len(result['results'])} opinions to {filepath}")
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


@opinions.command('get')
@click.argument('opinion_id', type=int)
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
def get_opinion(opinion_id, output_format):
    """Get a specific opinion"""
    client = CourtListenerClient()
    
    try:
        result = client.get(f'/opinions/{opinion_id}/')
        
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Opinion {opinion_id} retrieved successfully")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
