"""Main Click CLI entry point for CourtListener"""

import click
from .commands.opinions_commands import opinions
from .commands.search_commands import search
from .commands.courts_commands import courts
from .commands.dockets_commands import dockets
from .commands.people_commands import people
from .commands.audio_commands import audio
from .commands.batch_commands import batch
from .commands.clusters_commands import clusters
from .commands.docket_entries_commands import docket_entries
from .commands.recap_documents_commands import recap_documents
from .commands.parties_commands import parties
from .commands.attorneys_commands import attorneys
from .commands.positions_commands import positions
from .commands.financial_disclosures_commands import financial
from .commands.alerts_commands import alerts, docket_alerts
from .commands.citation_lookup_commands import citation_lookup
from .commands.tags_commands import tags


@click.group()
@click.version_option(version='1.0.0')
@click.option('--no-cache', is_flag=True, help='Disable local caching for this request')
@click.option('--screen', is_flag=True, help='Print results to screen (JSON format)')
@click.pass_context
def main(ctx, no_cache, screen):
    """CourtListener REST API Python CLI Client

    Access federal and state case law, PACER data, RECAP Archive,
    oral arguments, judge information, and financial disclosures.
    """
    ctx.ensure_object(dict)
    ctx.obj['no_cache'] = no_cache
    ctx.obj['screen'] = screen


# Existing command groups
main.add_command(opinions)
main.add_command(search)
main.add_command(courts)
main.add_command(dockets)
main.add_command(people)
main.add_command(audio)
main.add_command(batch)

# New command groups from PRD scaffold
main.add_command(clusters)
main.add_command(docket_entries, 'docket-entries')
main.add_command(recap_documents, 'recap-documents')
main.add_command(parties)
main.add_command(attorneys)
main.add_command(positions)
main.add_command(financial)
main.add_command(alerts)
main.add_command(docket_alerts, 'docket-alerts')
main.add_command(citation_lookup, 'citation-lookup')
main.add_command(tags)


if __name__ == '__main__':
    main()
