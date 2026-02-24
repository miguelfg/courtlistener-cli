"""Click commands for search resource"""

import click
import json
from urllib.parse import parse_qs, urlparse
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
@click.option('--limit', default=None, type=int,
              help='Total results to export; use 0 with --max-pages 0 to export all results')
@click.option('--max-pages', default=10, type=int,
              help='Maximum pages to fetch (0 = no page cap)')
@click.option('--offset', default=0, help='Pagination offset')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output',
              type=click.Path())
def search_query(q, search_type, limit, max_pages, offset, output_format, output_path):
    """Search for opinions, dockets, and other data"""
    client = CourtListenerClient()

    # CourtListener search endpoint can return smaller pages than requested.
    # Follow pagination until we gather the requested total (or all results).
    if limit is not None and limit < 0:
        click.echo("Error: --limit must be >= 0", err=True)
        raise SystemExit(1)
    if max_pages < 0:
        click.echo("Error: --max-pages must be >= 0", err=True)
        raise SystemExit(1)

    fetch_all = limit is None or limit == 0
    target_total = None if fetch_all else limit
    request_page_size = 100 if fetch_all else max(limit, 1)

    params = {
        'q': q,
        'type': search_type,
        'limit': request_page_size,
        'offset': offset
    }

    def _next_params(next_url):
        parsed = urlparse(next_url)
        parsed_qs = parse_qs(parsed.query)
        next_query_params = {}
        for key, values in parsed_qs.items():
            if values:
                next_query_params[key] = values[0]
        return next_query_params

    try:
        all_results = []
        total_count = 0
        next_url = None

        pages_fetched = 0
        while True:
            if max_pages > 0 and pages_fetched >= max_pages:
                break

            request_params = params if next_url is None else _next_params(next_url)
            result = client.get('/search/', params=request_params)
            pages_fetched += 1

            total_count = result.get('count', total_count)
            page_results = result.get('results', [])
            all_results.extend(page_results)

            if target_total is not None and len(all_results) >= target_total:
                all_results = all_results[:target_total]
                break

            next_url = result.get('next')
            if not next_url or not page_results:
                break

        output_data = {
            'count': total_count,
            'returned_count': len(all_results),
            'results': all_results
        }

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

            click.echo(f"✓ Found {output_data.get('count', 0)} total results")
            click.echo(f"✓ Exported {output_data.get('returned_count', 0)} results")
            click.echo(f"✓ Fetched {pages_fetched} page(s)")
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
