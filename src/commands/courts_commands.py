"""Click commands for courts resource"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from ..pagination import paginate_endpoint
from pathlib import Path


@click.group()
def courts():
    """Manage court information"""
    pass


@courts.command('list')
@click.option('--limit', default=20, type=int,
              help='Total results to export; use 0 with --max-pages 0 to export all results')
@click.option('--max-pages', default=10, type=int,
              help='Maximum pages to fetch (0 = no page cap)')
@click.option('--offset', default=0, help='Pagination offset')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output',
              type=click.Path())
def list_courts(limit, max_pages, offset, output_format, output_path):
    """List all courts"""
    client = CourtListenerClient()
    
    params: dict = {}

    try:
        output_data = paginate_endpoint(
            fetch_page=lambda request_params: client.get('/courts/', params=request_params),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
            progress_logger=lambda page, page_count, accumulated, target: click.echo(
                f"→ Page {page}: +{page_count} courts "
                f"(accumulated {accumulated}/{target if target is not None else 'all'})"
            ),
        )
        
        # Export results
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        if 'results' in output_data:
            if output_format == 'json':
                filepath = save_json(output_data, output_dir)
            elif output_format == 'csv':
                filepath = save_csv(output_data['results'], output_dir)
            else:  # xlsx
                filepath = save_xlsx(output_data['results'], output_dir)
            
            click.echo(f"✓ Found {output_data.get('count', 0)} total courts")
            click.echo(f"✓ Exported {output_data.get('returned_count', 0)} courts")
            click.echo(f"✓ Fetched {output_data.get('pages_fetched', 0)} page(s)")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No courts found")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    
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
@click.option('--limit', default=20, type=int,
              help='Total results to export; use 0 with --max-pages 0 to export all results')
@click.option('--max-pages', default=10, type=int,
              help='Maximum pages to fetch (0 = no page cap)')
@click.option('--offset', default=0, help='Pagination offset')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output',
              type=click.Path())
def search_courts(jurisdiction, court_type, limit, max_pages, offset, output_format, output_path):
    """Search courts by jurisdiction or type"""
    client = CourtListenerClient()
    
    params: dict = {}
    if jurisdiction:
        params['jurisdiction'] = jurisdiction
    if court_type:
        params['court_type'] = court_type
    
    try:
        output_data = paginate_endpoint(
            fetch_page=lambda request_params: client.get('/courts/', params=request_params),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
            progress_logger=lambda page, page_count, accumulated, target: click.echo(
                f"→ Page {page}: +{page_count} courts "
                f"(accumulated {accumulated}/{target if target is not None else 'all'})"
            ),
        )

        if output_format == 'json':
            click.echo(json.dumps(output_data, indent=2))
        else:
            output_dir = Path(output_path)
            output_dir.mkdir(exist_ok=True)
            if output_format == 'csv':
                filepath = save_csv(output_data['results'], output_dir)
            else:  # xlsx
                filepath = save_xlsx(output_data['results'], output_dir)
            click.echo(f"✓ Found {output_data.get('count', 0)} total courts")
            click.echo(f"✓ Exported {output_data.get('returned_count', 0)} courts")
            click.echo(f"✓ Fetched {output_data.get('pages_fetched', 0)} page(s)")
            click.echo(f"✓ Saved to {filepath}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@courts.command('count')
@click.option('--jurisdiction', help='Filter by jurisdiction')
@click.option('--court-type', help='Filter by court type (federal/state)')
def count_courts(jurisdiction, court_type):
    """Return total matching courts count"""
    client = CourtListenerClient()

    params: dict = {'page_size': 1}
    if jurisdiction:
        params['jurisdiction'] = jurisdiction
    if court_type:
        params['court_type'] = court_type

    try:
        result = client.get('/courts/', params=params)
        click.echo(result.get('count', 0))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
