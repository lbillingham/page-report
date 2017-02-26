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

def test_default_cli(runner):
    """does running with default args give expected result?"""
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Hello, world.'


def test_cli_with_option(runner):
    """do we resopnd to --flag option properly?"""
    result = runner.invoke(cli.main, ['--as-cowboy'])
    assert not result.exception
    assert result.exit_code == 0
    assert result.output.strip() == 'Howdy, world.'


def test_cli_with_arg(runner):
    """do we resopnd to positional arguments properly?"""
    result = runner.invoke(cli.main, ['Laurence'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Hello, Laurence.'

# pylint:enable=redefined-outer-name
