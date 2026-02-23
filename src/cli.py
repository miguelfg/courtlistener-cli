"""Main Click CLI entry point for CourtListener"""

import click
from .commands.opinions_commands import opinions


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


if __name__ == '__main__':
    main()
