"""Click commands for dockets resource"""

import csv
import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from ..pagination import paginate_endpoint
from pathlib import Path
from typing import List


def _read_batch_values(input_file: Path, column: str) -> List[str]:
    """Read query values from a CSV/XLSX file column."""
    suffix = input_file.suffix.lower()
    if suffix == '.csv':
        with open(input_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or column not in reader.fieldnames:
                raise ValueError(f"Column '{column}' not found in CSV file")
            return [
                str(row[column]).strip()
                for row in reader
                if row.get(column) is not None and str(row[column]).strip()
            ]

    if suffix == '.xlsx':
        try:
            from openpyxl import load_workbook
        except ImportError:
            raise ImportError("openpyxl required for XLSX input. Install: pip install openpyxl")

        wb = load_workbook(input_file, read_only=True, data_only=True)
        ws = wb.worksheets[0]
        rows = ws.iter_rows(values_only=True)
        headers = next(rows, None)
        if not headers:
            raise ValueError("Input XLSX file has no header row")
        header_index = {str(h).strip(): idx for idx, h in enumerate(headers) if h is not None}
        if column not in header_index:
            raise ValueError(f"Column '{column}' not found in XLSX first sheet")

        idx = header_index[column]
        values = []
        for row in rows:
            if row is None or idx >= len(row):
                continue
            value = row[idx]
            if value is None:
                continue
            value = str(value).strip()
            if value:
                values.append(value)
        return values

    raise ValueError("Unsupported input format. Use CSV or XLSX.")


@click.group()
def dockets():
    """Manage case dockets"""
    pass


@dockets.command('list')
@click.argument('input_file', required=False, type=click.Path(exists=True, dir_okay=False))
@click.option('--column', default=None,
              help='Column name in input CSV/XLSX containing docket numbers or IDs')
@click.option('--limit', default=20, type=int,
              help='Total results to export per request; use 0 with --max-pages 0 to export all results')
@click.option('--max-pages', default=10, type=int,
              help='Maximum pages to fetch (0 = no page cap)')
@click.option('--offset', default=0, help='Pagination offset')
@click.option('--court', help='Filter by court ID')
@click.option('--case-name', help='Filter by case name')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output',
              type=click.Path())
def list_dockets(input_file, column, limit, max_pages, offset, court, case_name, output_format, output_path):
    """List case dockets or batch query from input CSV/XLSX."""
    client = CourtListenerClient()

    try:
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)

        if input_file:
            if not column:
                raise ValueError("--column is required when input_file is provided")

            query_values = _read_batch_values(Path(input_file), column)
            results = []
            errors = 0
            pages_fetched = 0

            for idx, query_value in enumerate(query_values, start=1):
                click.echo(f"→ Query {idx}/{len(query_values)}: {query_value}")
                try:
                    if column.lower() in {'id', 'docket_id'}:
                        docket = client.get(f"/dockets/{query_value}/")
                        pages_fetched += 1
                        if isinstance(docket, dict):
                            docket['_query_value'] = query_value
                            results.append(docket)
                            click.echo(
                                f"  → Item page 1: +1 dockets (accumulated 1/1)"
                            )
                    else:
                        params = {
                            'limit': 100 if limit == 0 else max(limit, 1),
                            'offset': offset,
                            'docket_number': query_value
                        }
                        if court:
                            params['court'] = court
                        if case_name:
                            params['case_name'] = case_name
                        docket_page_data = paginate_endpoint(
                            fetch_page=lambda request_params: client.get('/dockets/', params=request_params),
                            initial_params=params,
                            limit=limit,
                            max_pages=max_pages,
                            progress_logger=lambda page, page_count, accumulated, target: click.echo(
                                f"  → Item page {page}: +{page_count} dockets "
                                f"(accumulated {accumulated}/{target if target is not None else 'all'})"
                            ),
                        )
                        pages_fetched += docket_page_data.get('pages_fetched', 0)
                        for docket in docket_page_data.get('results', []):
                            if isinstance(docket, dict):
                                docket['_query_value'] = query_value
                            results.append(docket)
                except Exception:
                    errors += 1

            if output_format == 'json':
                filepath = save_json(
                    {
                        'query_count': len(query_values),
                        'result_count': len(results),
                        'pages_fetched': pages_fetched,
                        'error_count': errors,
                        'results': results
                    },
                    output_dir
                )
            elif output_format == 'csv':
                filepath = save_csv(results, output_dir)
            else:  # xlsx
                filepath = save_xlsx(results, output_dir)

            click.echo(f"✓ Processed {len(query_values)} query values from {input_file}")
            click.echo(f"✓ Retrieved {len(results)} dockets")
            click.echo(f"✓ Fetched {pages_fetched} page(s)")
            if errors:
                click.echo(f"✗ Errors: {errors}")
            click.echo(f"✓ Saved to {filepath}")
        else:
            params = {'limit': 100 if limit == 0 else max(limit, 1), 'offset': offset}
            if court:
                params['court'] = court
            if case_name:
                params['case_name'] = case_name

            output_data = paginate_endpoint(
                fetch_page=lambda request_params: client.get('/dockets/', params=request_params),
                initial_params=params,
                limit=limit,
                max_pages=max_pages,
                progress_logger=lambda page, page_count, accumulated, target: click.echo(
                    f"→ Page {page}: +{page_count} dockets "
                    f"(accumulated {accumulated}/{target if target is not None else 'all'})"
                ),
            )

            if 'results' in output_data:
                if output_format == 'json':
                    filepath = save_json(output_data, output_dir)
                elif output_format == 'csv':
                    filepath = save_csv(output_data['results'], output_dir)
                else:  # xlsx
                    filepath = save_xlsx(output_data['results'], output_dir)

                click.echo(f"✓ Found {output_data.get('count', 0)} total dockets")
                click.echo(f"✓ Exported {output_data.get('returned_count', 0)} dockets")
                click.echo(f"✓ Fetched {output_data.get('pages_fetched', 0)} page(s)")
                click.echo(f"✓ Saved to {filepath}")
            else:
                click.echo("No dockets found")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@dockets.command('get')
@click.argument('docket_id', type=int)
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json']))
def get_docket(docket_id, output_format):
    """Get docket details by ID"""
    client = CourtListenerClient()
    
    try:
        result = client.get(f'/dockets/{docket_id}/')
        
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Docket {docket_id} details retrieved")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@dockets.command('entries')
@click.argument('docket_id', type=int)
@click.option('--limit', default=20, type=int,
              help='Total results to export; use 0 with --max-pages 0 to export all results')
@click.option('--max-pages', default=10, type=int,
              help='Maximum pages to fetch (0 = no page cap)')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output',
              type=click.Path())
def get_docket_entries(docket_id, limit, max_pages, output_format, output_path):
    """Get entries for a specific docket"""
    client = CourtListenerClient()
    
    params = {'docket': docket_id, 'limit': 100 if limit == 0 else max(limit, 1)}
    
    try:
        output_data = paginate_endpoint(
            fetch_page=lambda request_params: client.get('/docket-entries/', params=request_params),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
            progress_logger=lambda page, page_count, accumulated, target: click.echo(
                f"→ Page {page}: +{page_count} entries "
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
            
            click.echo(f"✓ Found {output_data.get('count', 0)} total entries")
            click.echo(f"✓ Exported {output_data.get('returned_count', 0)} entries")
            click.echo(f"✓ Fetched {output_data.get('pages_fetched', 0)} page(s)")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No entries found")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@dockets.command('count')
@click.option('--court', help='Filter by court ID')
@click.option('--case-name', help='Filter by case name')
def count_dockets(court, case_name):
    """Return total matching dockets count"""
    client = CourtListenerClient()

    params = {'limit': 1}
    if court:
        params['court'] = court
    if case_name:
        params['case_name'] = case_name

    try:
        result = client.get('/dockets/', params=params)
        click.echo(result.get('count', 0))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
