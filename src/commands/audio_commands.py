"""Click commands for audio (oral arguments) resource"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from pathlib import Path


@click.group()
def audio():
    """Manage oral argument recordings"""
    pass


@audio.command('list')
@click.option('--limit', default=20, help='Results per page')
@click.option('--offset', default=0, help='Pagination offset')
@click.option('--court', help='Filter by court')
@click.option('--year', type=int, help='Filter by year')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output',
              type=click.Path())
def list_audio(limit, offset, court, year, output_format, output_path):
    """List oral argument recordings"""
    client = CourtListenerClient()
    
    params = {'limit': limit, 'offset': offset}
    if court:
        params['court'] = court
    if year:
        params['date_argued_gte'] = f'{year}-01-01'
        params['date_argued_lte'] = f'{year}-12-31'
    
    try:
        result = client.get('/audio/', params=params)
        
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        if 'results' in result:
            if output_format == 'json':
                filepath = save_json(result, output_dir)
            elif output_format == 'csv':
                filepath = save_csv(result['results'], output_dir)
            else:  # xlsx
                filepath = save_xlsx(result['results'], output_dir)
            
            click.echo(f"✓ Retrieved {len(result['results'])} recordings")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No audio found")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@audio.command('get')
@click.argument('audio_id', type=int)
def get_audio(audio_id):
    """Get audio details by ID"""
    client = CourtListenerClient()
    
    try:
        result = client.get(f'/audio/{audio_id}/')
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
