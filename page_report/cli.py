"""
Building the Command Line Interface
for our app
"""
import click


@click.command()
@click.option('--outfile', '-o',
              type=click.File('wb'),
              default='page_report.html',
              help='Path on which to write report.')
@click.argument('url', required=True, metavar='<url>')
def main(url, outfile):
    """
    Page Report scrapes a URL and reports links, word counts, ...
    """
    success_mess = 'Report on {} written to {}.'
    click.echo(success_mess.format(url, outfile.name))
