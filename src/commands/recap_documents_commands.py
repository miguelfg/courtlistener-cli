"""Click commands for recap-documents resource (PACER PDFs in RECAP Archive)"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from ..pagination import paginate_endpoint
from pathlib import Path


@click.group()
def recap_documents():
    """Manage RECAP Archive documents (PDFs from PACER)"""
    pass


@recap_documents.command('list')
@click.option('--docket-entry', default=None, type=int, help='Filter by docket entry ID')
@click.option('--is-available', default=None, type=bool,
              help='Filter to documents available in RECAP (True/False)')
@click.option('--limit', default=20, type=int,
              help='Total results to export; 0 with --max-pages 0 = all results')
@click.option('--max-pages', default=10, type=int,
              help='Maximum pages to fetch (0 = no page cap)')
@click.option('--order-by', default=None, help='Sort field, prefix - for descending')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output', type=click.Path())
def list_recap_documents(docket_entry, is_available, limit, max_pages, order_by,
                         output_format, output_path):
    """List RECAP documents. Omit plain_text for faster responses."""
    client = CourtListenerClient()

    # Exclude plain_text by default — it is large and significantly slows responses
    params = {
        'limit': 100 if limit == 0 else max(limit, 1),
        'fields!': 'plain_text',
    }
    if docket_entry is not None:
        params['docket_entry'] = docket_entry
    if is_available is not None:
        params['is_available'] = is_available
    if order_by:
        params['order_by'] = order_by

    try:
        output_data = paginate_endpoint(
            fetch_page=lambda p: client.get('/recap-documents/', params=p),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
            progress_logger=lambda page, page_count, acc, target: click.echo(
                f"→ Page {page}: +{page_count} documents "
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

            click.echo(f"✓ Found {output_data.get('count', 0)} total documents")
            click.echo(f"✓ Exported {output_data.get('returned_count', 0)} documents")
            click.echo(f"✓ Fetched {output_data.get('pages_fetched', 0)} page(s)")
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


@recap_documents.command('get')
@click.argument('document_id', type=int)
def get_recap_document(document_id):
    """Get a specific RECAP document by ID"""
    client = CourtListenerClient()

    try:
        result = client.get(f'/recap-documents/{document_id}/')
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@recap_documents.command('query')
@click.option('--court', required=True, help='Court ID (matches PACER subdomain)')
@click.option('--pacer-doc-id', required=True,
              help='Comma-separated PACER document IDs (up to 300); 4th digit normalized to 0')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output', type=click.Path())
def query_recap(court, pacer_doc_id, output_format, output_path):
    """Fast lookup: check if PACER documents are available in RECAP Archive.

    Note: This endpoint is only available to select users.
    """
    client = CourtListenerClient()

    params = {
        'docket_entry__docket__court': court,
        'pacer_doc_id__in': pacer_doc_id,
    }

    try:
        result = client.get('/recap-query/', params=params)

        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)

        results = result.get('results', result if isinstance(result, list) else [])
        if output_format == 'json':
            filepath = save_json({'results': results, 'count': len(results)}, output_dir)
        elif output_format == 'csv':
            filepath = save_csv(results, output_dir)
        else:
            filepath = save_xlsx(results, output_dir)

        click.echo(f"✓ Found {len(results)} document(s) in RECAP")
        click.echo(f"✓ Saved to {filepath}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
