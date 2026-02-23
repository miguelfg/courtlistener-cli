"""Click commands for courts resource"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from pathlib import Path


@click.group()
def courts():
    """Manage court information"""
    pass


@courts.command('list')
@click.option('--limit', default=20, help='Results per page')
@click.option('--offset', default=0, help='Pagination offset')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output',
              type=click.Path())
def list_courts(limit, offset, output_format, output_path):
    """List all courts"""
    client = CourtListenerClient()
    
    params = {'limit': limit, 'offset': offset}
    
    try:
        result = client.get('/courts/', params=params)
        
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
            
            click.echo(f"✓ Retrieved {len(result['results'])} courts")
            click.echo(f"✓ Total available: {result.get('count', 0)}")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No courts found")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@courts.command('get')
@click.argument('court_id')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json']))
def get_court(court_id, output_format):
    """Get court details by ID"""
    client = CourtListenerClient()
    
    try:
        result = client.get(f'/courts/{court_id}/')
        
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Court {court_id} details retrieved")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@courts.command('search')
@click.option('--jurisdiction', help='Filter by jurisdiction')
@click.option('--court-type', help='Filter by court type (federal/state)')
@click.option('--limit', default=20, help='Results per page')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
def search_courts(jurisdiction, court_type, limit, output_format):
    """Search courts by jurisdiction or type"""
    client = CourtListenerClient()
    
    params = {'limit': limit}
    if jurisdiction:
        params['jurisdiction'] = jurisdiction
    if court_type:
        params['court_type'] = court_type
    
    try:
        result = client.get('/courts/', params=params)
        
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"✓ Found {result.get('count', 0)} courts")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
