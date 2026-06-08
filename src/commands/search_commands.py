"""Click commands for search resource"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from ..pagination import paginate_endpoint
from pathlib import Path


@click.group()
def search():
    """Search across all legal data"""
    pass


@search.command('query')
@click.option('--q', required=True, help='Search query')
@click.option('--type', 'search_type', default='r',
              help='Type code (default: r).')
@click.option('--court', default=None,
              help='Filter by court ID (e.g. dcd, ca9). Matches court_id field in results.')
@click.option('--limit', default=20, type=int,
              help='Total results to export; use 0 with --max-pages 0 to export all results')
@click.option('--max-pages', default=10, type=int,
              help='Maximum pages to fetch (0 = no page cap)')
@click.option('--offset', default=0, help='Pagination offset')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output',
              type=click.Path())
@click.option('--slim', is_flag=True, default=False,
              help='Also export a slim version with key fields only')
@click.option('--filename', 'filename_stem', default='results',
              help='Output filename stem (without extension)')
@click.option('--list-sep', 'list_sep', default=';',
              help='Separator for list fields in CSV/XLSX (empty string or "none" to keep as JSON)')
def search_query(q, search_type, court, limit, max_pages, offset, output_format, output_path, slim, filename_stem, list_sep):
    """Search for opinions, dockets, and other data"""
    client = CourtListenerClient()

    try:
        params = {
            'q': q,
            'type': search_type,
            'limit': 100 if limit == 0 else max(limit, 1),
            'offset': offset
        }
        if court:
            params['court'] = court
        output_data = paginate_endpoint(
            fetch_page=lambda request_params: client.get('/search/', params=request_params),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
            progress_logger=lambda page, page_count, accumulated, target: click.echo(
                f"→ Page {page}: +{page_count} results "
                f"(accumulated {accumulated}/{target if target is not None else 'all'})"
            ),
        )

        # Export results
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)

        sep = None if (not list_sep or list_sep.lower() == 'none') else list_sep
        is_partial = output_data.get('partial', False)
        returned = output_data.get('returned_count', 0)
        effective_stem = f"{filename_stem}_partial_{returned}" if is_partial else filename_stem

        if 'results' in output_data:
            if output_format == 'json':
                filepath = save_json(output_data, output_dir, filename_stem=effective_stem)
            elif output_format == 'csv':
                filepath = save_csv(output_data['results'], output_dir, filename_stem=effective_stem, concat_list_fields_char=sep)
            else:  # xlsx
                filepath = save_xlsx(output_data['results'], output_dir, filename_stem=effective_stem, concat_list_fields_char=sep)

            if is_partial:
                click.echo(f"⚠ Partial export — daily quota hit after {output_data.get('pages_fetched', 0)} page(s)")
            click.echo(f"✓ Found {output_data.get('count', 0)} total results")
            click.echo(f"✓ Exported {returned} results")
            click.echo(f"✓ Fetched {output_data.get('pages_fetched', 0)} page(s)")
            click.echo(f"✓ Saved to {filepath}")

            if slim:
                from ..reducers import slim_results
                slim_data = slim_results(output_data['results'])
                slim_payload = {"count": output_data.get("count"), "results": slim_data}
                slim_stem = f"{effective_stem}_slim"
                if output_format == 'json':
                    slim_path = save_json(slim_payload, output_dir, filename_stem=slim_stem)
                elif output_format == 'csv':
                    slim_path = save_csv(slim_data, output_dir, filename_stem=slim_stem, concat_list_fields_char=sep)
                else:
                    slim_path = save_xlsx(slim_data, output_dir, filename_stem=slim_stem, concat_list_fields_char=sep)
                click.echo(f"✓ Slim export saved to {slim_path}")

            if is_partial:
                resume_next_offset = (offset or 0) + returned
                parts = [
                    "courtlistener-cli search query",
                    f"--q {q!r}",
                    f"--type {search_type}",
                    f"--offset {resume_next_offset}",
                    "--limit 0 --max-pages 0",
                    f"--format {output_format}",
                    f"--filename {filename_stem}",
                ]
                if court:
                    parts.append(f"--court {court}")
                if slim:
                    parts.append("--slim")
                if list_sep != ';':
                    parts.append(f"--list-sep {list_sep!r}")
                if output_path != './output':
                    parts.append(f"--output {output_path!r}")
                click.echo(f"\n  Resume tomorrow with:\n  uv run {' '.join(parts)}")
        else:
            click.echo("No results found")

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
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


@search.command('count')
@click.option('--q', required=True, help='Search query')
@click.option('--type', 'search_type', default='r',
              help='Type code (default: r).')
@click.option('--court', default=None,
              help='Filter by court ID (e.g. dcd, ca9). Matches court_id field in results.')
def count_search(q, search_type, court):
    """Return total matching search results count"""
    client = CourtListenerClient()

    try:
        params = {
            'q': q,
            'type': search_type,
            'limit': 1,
        }
        if court:
            params['court'] = court
        result = client.get('/search/', params=params)
        click.echo(result.get('count', 0))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
