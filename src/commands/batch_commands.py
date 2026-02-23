"""Click commands for batch processing"""

import click
from pathlib import Path
from ..client import CourtListenerClient
from ..batch_processor import read_batch_file
from ..output import save_json, save_csv, save_xlsx


@click.group()
def batch():
    """Process batch requests from files"""
    pass


@batch.command('process')
@click.option('--input-file', required=True, type=click.Path(exists=True),
              help='Input CSV or JSON Lines file')
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']),
              help='Output format')
@click.option('--output', 'output_path', default='./output',
              type=click.Path(),
              help='Output directory')
@click.option('--limit', default=None, type=int,
              help='Process only first N requests')
@click.option('--verbose', is_flag=True, help='Show details for each request')
def process_batch(input_file, output_format, output_path, limit, verbose):
    """Process batch requests from CSV or JSON Lines file
    
    CSV Format: method,endpoint,param1,param2
    JSON Lines: One JSON object per line
    """
    try:
        # Read batch file
        requests = read_batch_file(Path(input_file))
        
        if limit:
            requests = requests[:limit]
        
        client = CourtListenerClient()
        results = []
        
        # Process each request
        with click.progressbar(requests, label='Processing requests') as bar:
            for req in bar:
                try:
                    method = req.get('method', 'GET').upper()
                    endpoint = req.get('endpoint', '/')
                    
                    # Extract parameters
                    params = {k: v for k, v in req.items() 
                             if k not in ['method', 'endpoint']}
                    
                    # Make request
                    if method == 'GET':
                        result = client.get(endpoint, params=params)
                    elif method == 'POST':
                        result = client.post(endpoint, data=params)
                    else:
                        result = client.request(method, endpoint, json=params)
                    
                    # Add to results
                    results.append({
                        'request': req,
                        'status': 'success',
                        'data': result
                    })
                    
                    if verbose:
                        click.echo(f"✓ {method} {endpoint}")
                
                except Exception as e:
                    results.append({
                        'request': req,
                        'status': 'error',
                        'error': str(e)
                    })
                    if verbose:
                        click.echo(f"✗ {method} {endpoint}: {e}")
        
        # Export results
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        if output_format == 'json':
            filepath = save_json(results, output_dir, include_timestamp=True)
        elif output_format == 'csv':
            # Flatten results for CSV
            flattened = []
            for r in results:
                flat = {
                    'request_method': r['request'].get('method', 'GET'),
                    'request_endpoint': r['request'].get('endpoint', '/'),
                    'status': r['status'],
                }
                if r['status'] == 'success' and isinstance(r.get('data'), dict):
                    flat.update(r['data'])
                else:
                    flat['result'] = str(r.get('data', r.get('error', '')))
                flattened.append(flat)
            filepath = save_csv(flattened, output_dir, include_timestamp=True)
        else:  # xlsx
            flattened = []
            for r in results:
                flat = {
                    'request_method': r['request'].get('method', 'GET'),
                    'request_endpoint': r['request'].get('endpoint', '/'),
                    'status': r['status'],
                }
                if r['status'] == 'success' and isinstance(r.get('data'), dict):
                    flat.update(r['data'])
                else:
                    flat['result'] = str(r.get('data', r.get('error', '')))
                flattened.append(flat)
            filepath = save_xlsx(flattened, output_dir, include_timestamp=True)
        
        # Summary
        success = sum(1 for r in results if r['status'] == 'success')
        errors = sum(1 for r in results if r['status'] == 'error')
        
        click.echo(f"\n✓ Processed {len(requests)} requests")
        click.echo(f"  ✓ Success: {success}")
        click.echo(f"  ✗ Errors: {errors}")
        click.echo(f"  ✓ Output: {filepath}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
