"""Main Click CLI entry point for CourtListener"""

import click
from .commands.opinions_commands import opinions
from .commands.search_commands import search
from .commands.courts_commands import courts
from .commands.dockets_commands import dockets
from .commands.people_commands import people
from .commands.audio_commands import audio
from .commands.batch_commands import batch


@click.group()
@click.version_option(version='1.0.0')
def main():
    """CourtListener REST API Python CLI Client

    Access federal and state case law, PACER data, RECAP Archive,
    oral arguments, judge information, and financial disclosures.
    """
    pass


# Register command groups
main.add_command(opinions)
main.add_command(search)
main.add_command(courts)
main.add_command(dockets)
main.add_command(people)
main.add_command(audio)
main.add_command(batch)


if __name__ == '__main__':
    main()
