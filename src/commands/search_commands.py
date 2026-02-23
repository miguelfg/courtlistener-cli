"""Click commands for search resource"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from pathlib import Path


@click.group()
def search():
    """Search across all legal data"""
    pass


@search.command('query')
@click.option('--q', required=True, help='Search query')
@click.option('--type', 'search_type', default='r',
              help='Type code (default: r).')
@click.option('--limit', default=20, help='Results per page')
@click.option('--offset', default=0, help='Pagination offset')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output',
              type=click.Path())
def search_query(q, search_type, limit, offset, output_format, output_path):
    """Search for opinions, dockets, and other data"""
    client = CourtListenerClient()
    
    params = {
        'q': q,
        'type': search_type,
        'limit': limit,
        'offset': offset
    }
    
    try:
        result = client.get('/search/', params=params)
        
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
            
            click.echo(f"✓ Found {result.get('count', 0)} results")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No results found")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@search.command('advanced')
@click.option('--court', help='Filter by court')
@click.option('--judge', help='Filter by judge')
@click.option('--date-from', help='Start date (YYYY-MM-DD)')
@click.option('--date-to', help='End date (YYYY-MM-DD)')
@click.option('--limit', default=20, help='Results per page')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
def advanced_search(court, judge, date_from, date_to, limit, output_format):
    """Advanced search with filters"""
    client = CourtListenerClient()
    
    params = {'limit': limit}
    if court:
        params['court'] = court
    if judge:
        params['judge'] = judge
    if date_from:
        params['date_filed_gte'] = date_from
    if date_to:
        params['date_filed_lte'] = date_to
    
    try:
        result = client.get('/opinions/', params=params)
        
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"✓ Found {result.get('count', 0)} results")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
