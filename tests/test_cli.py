"""Basic tests for CourtListener CLI"""

import csv
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


def test_dockets_list_batch_requires_column(tmp_path):
    """Batch input mode requires --column."""
    input_file = tmp_path / "dockets.csv"
    input_file.write_text("docketNumber\nA-123\n")

    runner = CliRunner()
    result = runner.invoke(main, ["dockets", "list", str(input_file)])

    assert result.exit_code == 1
    assert "--column is required" in result.output


def test_dockets_list_batch_csv_uses_column_values(monkeypatch, tmp_path):
    """Batch dockets list should query each value from the selected column."""
    input_file = tmp_path / "dockets.csv"
    with open(input_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["docketNumber"])
        writer.writeheader()
        writer.writerow({"docketNumber": "A-123"})
        writer.writerow({"docketNumber": "B-456"})

    calls = []

    def mock_get(self, endpoint, **kwargs):
        calls.append((endpoint, kwargs.get("params")))
        return {"count": 1, "results": [{"id": len(calls), "case_name": "Case"}]}

    monkeypatch.setattr("src.commands.dockets_commands.CourtListenerClient.get", mock_get)

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "dockets",
            "list",
            str(input_file),
            "--column",
            "docketNumber",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert len(calls) == 2
    assert calls[0][0] == "/dockets/"
    assert calls[0][1]["docket_number"] == "A-123"
    assert calls[1][1]["docket_number"] == "B-456"
