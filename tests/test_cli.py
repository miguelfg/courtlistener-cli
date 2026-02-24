"""Basic tests for CourtListener CLI"""

import csv
import json
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


def test_search_query_paginates_until_requested_limit(monkeypatch, tmp_path):
    """Search should aggregate pages until it reaches requested total."""
    page_1 = {
        "count": 50,
        "results": [{"id": i} for i in range(1, 21)],
        "next": "https://www.courtlistener.com/api/rest/v4/search/?cursor=abc&limit=100&offset=0&q=test&type=r",
    }
    page_2 = {
        "count": 50,
        "results": [{"id": i} for i in range(21, 41)],
        "next": "https://www.courtlistener.com/api/rest/v4/search/?cursor=def&limit=100&offset=0&q=test&type=r",
    }

    def mock_get(self, endpoint, **kwargs):
        params = kwargs.get("params", {})
        cursor = params.get("cursor")
        if cursor is None:
            return page_1
        if cursor == "abc":
            return page_2
        raise AssertionError(f"Unexpected cursor: {cursor}")

    monkeypatch.setattr("src.commands.search_commands.CourtListenerClient.get", mock_get)

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "search",
            "query",
            "--q",
            "test",
            "--limit",
            "25",
            "--format",
            "json",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads((output_dir / "results.json").read_text())
    assert payload["count"] == 50
    assert payload["returned_count"] == 25
    assert len(payload["results"]) == 25


def test_search_query_without_limit_uses_default_limit(monkeypatch, tmp_path):
    """Omitting --limit should use default limit=20."""
    page_1 = {
        "count": 45,
        "results": [{"id": i} for i in range(1, 21)],
        "next": "https://www.courtlistener.com/api/rest/v4/search/?cursor=abc&limit=100&offset=0&q=test&type=r",
    }
    page_2 = {
        "count": 45,
        "results": [{"id": i} for i in range(21, 41)],
        "next": "https://www.courtlistener.com/api/rest/v4/search/?cursor=def&limit=100&offset=0&q=test&type=r",
    }
    page_3 = {
        "count": 45,
        "results": [{"id": i} for i in range(41, 46)],
        "next": None,
    }

    def mock_get(self, endpoint, **kwargs):
        params = kwargs.get("params", {})
        cursor = params.get("cursor")
        if cursor is None:
            return page_1
        if cursor == "abc":
            return page_2
        if cursor == "def":
            return page_3
        raise AssertionError(f"Unexpected cursor: {cursor}")

    monkeypatch.setattr("src.commands.search_commands.CourtListenerClient.get", mock_get)

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "search",
            "query",
            "--q",
            "test",
            "--format",
            "json",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads((output_dir / "results.json").read_text())
    assert payload["count"] == 45
    assert payload["returned_count"] == 20
    assert len(payload["results"]) == 20


def test_search_query_limit_zero_respects_default_max_pages(monkeypatch, tmp_path):
    """With --limit 0 and default max-pages, fetching should stop at 10 pages."""
    calls = []

    def mock_get(self, endpoint, **kwargs):
        params = kwargs.get("params", {})
        cursor = params.get("cursor")
        calls.append(cursor)

        if cursor is None:
            page_no = 1
        else:
            page_no = int(cursor)

        next_cursor = str(page_no + 1) if page_no < 12 else None
        next_url = (
            f"https://www.courtlistener.com/api/rest/v4/search/?cursor={next_cursor}"
            if next_cursor
            else None
        )
        return {
            "count": 12,
            "results": [{"id": page_no}],
            "next": next_url,
        }

    monkeypatch.setattr("src.commands.search_commands.CourtListenerClient.get", mock_get)

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "search",
            "query",
            "--q",
            "test",
            "--limit",
            "0",
            "--format",
            "json",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads((output_dir / "results.json").read_text())
    assert payload["count"] == 12
    assert payload["returned_count"] == 10
    assert len(payload["results"]) == 10
    assert "Fetched 10 page(s)" in result.output


def test_search_query_limit_zero_and_max_pages_zero_fetches_all(monkeypatch, tmp_path):
    """--limit 0 --max-pages 0 should follow pagination until next is null."""

    def mock_get(self, endpoint, **kwargs):
        params = kwargs.get("params", {})
        cursor = params.get("cursor")

        if cursor is None:
            page_no = 1
        else:
            page_no = int(cursor)

        next_cursor = str(page_no + 1) if page_no < 12 else None
        next_url = (
            f"https://www.courtlistener.com/api/rest/v4/search/?cursor={next_cursor}"
            if next_cursor
            else None
        )
        return {
            "count": 12,
            "results": [{"id": page_no}],
            "next": next_url,
        }

    monkeypatch.setattr("src.commands.search_commands.CourtListenerClient.get", mock_get)

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "search",
            "query",
            "--q",
            "test",
            "--limit",
            "0",
            "--max-pages",
            "0",
            "--format",
            "json",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads((output_dir / "results.json").read_text())
    assert payload["count"] == 12
    assert payload["returned_count"] == 12
    assert len(payload["results"]) == 12
    assert "Fetched 12 page(s)" in result.output
