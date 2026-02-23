"""Click commands for people (judges/attorneys) resource"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from pathlib import Path


@click.group()
def people():
    """Manage judge and attorney information"""
    pass


@people.command('list')
@click.option('--limit', default=20, help='Results per page')
@click.option('--offset', default=0, help='Pagination offset')
@click.option('--name', help='Filter by person name')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output',
              type=click.Path())
def list_people(limit, offset, name, output_format, output_path):
    """List judges and attorneys"""
    client = CourtListenerClient()
    
    params = {'limit': limit, 'offset': offset}
    if name:
        params['name'] = name
    
    try:
        result = client.get('/people/', params=params)
        
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        if 'results' in result:
            if output_format == 'json':
                filepath = save_json(result, output_dir)
            elif output_format == 'csv':
                filepath = save_csv(result['results'], output_dir)
            else:  # xlsx
                filepath = save_xlsx(result['results'], output_dir)
            
            click.echo(f"✓ Retrieved {len(result['results'])} people")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No people found")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@people.command('get')
@click.argument('person_id', type=int)
def get_person(person_id):
    """Get person details by ID"""
    client = CourtListenerClient()
    
    try:
        result = client.get(f'/people/{person_id}/')
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
