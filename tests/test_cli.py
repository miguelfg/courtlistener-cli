"""Basic tests for CourtListener CLI"""

import pytest
from click.testing import CliRunner
from src.cli import main


def test_cli_help():
    """Test CLI help command"""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'CourtListener' in result.output


def test_cli_version():
    """Test CLI version"""
    runner = CliRunner()
    result = runner.invoke(main, ['--version'])
    assert result.exit_code == 0
    assert '1.0.0' in result.output


def test_opinions_help():
    """Test opinions command help"""
    runner = CliRunner()
    result = runner.invoke(main, ['opinions', '--help'])
    assert result.exit_code == 0
    assert 'opinions' in result.output.lower()


def test_opinions_list_shows_token_hint_on_auth_error(monkeypatch):
    """List command should fail gracefully with a token hint."""

    def mock_get(self, endpoint, **kwargs):
        raise Exception("401 Unauthorized")

    monkeypatch.setattr("src.commands.opinions_commands.CourtListenerClient.get", mock_get)

    runner = CliRunner()
    result = runner.invoke(main, ["opinions", "list", "--limit", "10"])

    assert result.exit_code == 1
    assert "COURTLISTENER_API_TOKEN" in result.output
