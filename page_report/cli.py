"""
Building the Command Line Interface
for our app
"""
import click
import validators

from page_report.page_scanner import HTTPError, print_report


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
    if not validators.url(url):
        mess = """
            {} is not a valid url,
            need something like https://www.example.com
            including protocol.'
            """.format(url)
        raise click.BadParameter(mess)
    try:
        print_report(url)
    except HTTPError:
        mess = 'failed to get web page from {}'.format(url)
        exception = click.ClickException
        exception.exit_code = 1
        raise exception(mess)
    success_mess = 'Report on {} written to {}.'
    click.echo(success_mess.format(url, outfile.name))
