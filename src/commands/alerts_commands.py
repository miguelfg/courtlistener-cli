"""Click commands for alerts (search alerts and docket alerts)"""

import click
import json
from ..client import CourtListenerClient
from ..output import save_json, save_csv, save_xlsx
from ..pagination import paginate_endpoint
from pathlib import Path


# ─── Search Alerts ────────────────────────────────────────────────────────────

@click.group()
def alerts():
    """Manage search alerts (email/webhook when new matching results appear)"""
    pass


@alerts.command('list')
@click.option('--limit', default=20, type=int,
              help='Total results to export; 0 with --max-pages 0 = all results')
@click.option('--max-pages', default=10, type=int)
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output', type=click.Path())
def list_alerts(limit, max_pages, output_format, output_path):
    """List your search alerts"""
    client = CourtListenerClient()

    params = {'limit': 100 if limit == 0 else max(limit, 1)}

    try:
        output_data = paginate_endpoint(
            fetch_page=lambda p: client.get('/alerts/', params=p),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
            progress_logger=lambda page, page_count, acc, target: click.echo(
                f"→ Page {page}: +{page_count} alerts "
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

            click.echo(f"✓ Exported {output_data.get('returned_count', 0)} alerts")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No alerts found")
    except Exception as e:
        error = str(e)
        if "401" in error or "Unauthorized" in error:
            click.echo("Authentication failed. Set COURTLISTENER_API_TOKEN with your API token.")
        else:
            click.echo(f"Error: {error}")
        raise SystemExit(1)


@alerts.command('create')
@click.option('--name', required=True, help='Human-friendly name for the alert')
@click.option('--query', required=True,
              help='URL-encoded query string from CourtListener front end (e.g. q=foo&type=o)')
@click.option('--rate', required=True,
              type=click.Choice(['rt', 'dly', 'wly', 'mly']),
              help='Email frequency: rt=real-time, dly=daily, wly=weekly, mly=monthly')
@click.option('--alert-type', default=None,
              help='For RECAP: d (dockets only) or r (dockets + filings)')
def create_alert(name, query, rate, alert_type):
    """Create a new search alert"""
    client = CourtListenerClient()

    data = {'name': name, 'query': query, 'rate': rate}
    if alert_type:
        data['alert_type'] = alert_type

    try:
        result = client.request('POST', '/alerts/', json=data)
        click.echo(json.dumps(result, indent=2))
        click.echo(f"✓ Alert created with ID {result.get('id')}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alerts.command('update')
@click.option('--id', 'alert_id', required=True, type=int, help='Alert ID to update')
@click.option('--name', default=None, help='New name')
@click.option('--query', default=None, help='New query string')
@click.option('--rate', default=None,
              type=click.Choice(['rt', 'dly', 'wly', 'mly']),
              help='New email frequency')
def update_alert(alert_id, name, query, rate):
    """Update an existing search alert (PATCH)"""
    client = CourtListenerClient()

    data = {}
    if name:
        data['name'] = name
    if query:
        data['query'] = query
    if rate:
        data['rate'] = rate

    if not data:
        click.echo("No fields to update. Provide --name, --query, or --rate.")
        raise SystemExit(1)

    try:
        result = client.request('PATCH', f'/alerts/{alert_id}/', json=data)
        click.echo(json.dumps(result, indent=2))
        click.echo(f"✓ Alert {alert_id} updated")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@alerts.command('delete')
@click.option('--id', 'alert_id', required=True, type=int, help='Alert ID to delete')
@click.option('--confirm', is_flag=True, required=True, help='Confirm deletion (required)')
def delete_alert(alert_id, confirm):
    """Delete a search alert"""
    client = CourtListenerClient()

    try:
        client.request('DELETE', f'/alerts/{alert_id}/')
        click.echo(f"✓ Alert {alert_id} deleted")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


# ─── Docket Alerts ────────────────────────────────────────────────────────────

@click.group()
def docket_alerts():
    """Manage docket alerts (notifications when a specific case is updated)"""
    pass


@docket_alerts.command('list')
@click.option('--limit', default=20, type=int)
@click.option('--max-pages', default=10, type=int)
@click.option('--format', 'output_format', default='json',
              type=click.Choice(['json', 'csv', 'xlsx']))
@click.option('--output', 'output_path', default='./output', type=click.Path())
def list_docket_alerts(limit, max_pages, output_format, output_path):
    """List your docket alerts"""
    client = CourtListenerClient()

    params = {'limit': 100 if limit == 0 else max(limit, 1)}

    try:
        output_data = paginate_endpoint(
            fetch_page=lambda p: client.get('/docket-alerts/', params=p),
            initial_params=params,
            limit=limit,
            max_pages=max_pages,
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
            click.echo(f"✓ Exported {output_data.get('returned_count', 0)} docket alerts")
            click.echo(f"✓ Saved to {filepath}")
        else:
            click.echo("No docket alerts found")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@docket_alerts.command('create')
@click.option('--docket', required=True, type=int, help='Docket ID to subscribe to')
@click.option('--alert-type', default=1, type=int,
              help='1=subscribe (default), 0=unsubscribe (@recap.email auto-subscribe only)')
def create_docket_alert(docket, alert_type):
    """Subscribe to updates for a specific docket"""
    client = CourtListenerClient()

    try:
        result = client.request('POST', '/docket-alerts/',
                                json={'docket': docket, 'alert_type': alert_type})
        click.echo(json.dumps(result, indent=2))
        click.echo(f"✓ Subscribed to docket {docket} (alert ID {result.get('id')})")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@docket_alerts.command('delete')
@click.option('--id', 'alert_id', required=True, type=int, help='Docket alert ID to delete')
@click.option('--confirm', is_flag=True, required=True, help='Confirm deletion (required)')
def delete_docket_alert(alert_id, confirm):
    """Unsubscribe from a docket alert"""
    client = CourtListenerClient()

    try:
        client.request('DELETE', f'/docket-alerts/{alert_id}/')
        click.echo(f"✓ Docket alert {alert_id} deleted")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
