"""
run as if using CLI to test options/args
"""
import pytest
from click.testing import CliRunner
from page_report import cli


@pytest.fixture
def runner():
    """fake CLI interaction"""
    return CliRunner()

# pylint:disable=redefined-outer-name
#   otherwise pytest fixtures look like problems

def test_error_on_no_url(runner):
    """does running with default args give expected result?"""
    result = runner.invoke(cli.main)
    assert result.exit_code != 0
    assert result.exception
    for mess_part in ['Usage', 'url', 'Error', 'Missing argument']:
        assert mess_part in result.output


def test_cli_good_url_outfile_option(runner):
    """do we resopnd to --flag option propely?"""
    supplied_url = 'https://www.example.com'
    outfile = 'spam.html'
    options = [supplied_url, '-o {}'.format(outfile)]
    result = runner.invoke(cli.main, options)
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Report on {} written to  {}.'.format(
        supplied_url, outfile
    )

def test_cli_bad_url_provided(runner):
    """do we error on bad url"""
    bad_url = 'sdfsdsd'
    result = runner.invoke(cli.main, [bad_url])
    assert result.exit_code != 0
    assert result.exception
    for mess_part in ['not a valid url', bad_url]:
        assert mess_part in result.output


def test_cli_good_url_provided(runner):
    """do we resopnd to positional arguments properly?"""
    supplied_url = 'https://www.example.com'
    expect_outfile = 'page_report.html'
    result = runner.invoke(cli.main, [supplied_url])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Report on {} written to {}.'.format(
        supplied_url, expect_outfile
    )

# pylint:enable=redefined-outer-name
