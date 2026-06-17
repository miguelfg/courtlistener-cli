"""Basic tests for CourtListener CLI"""

import csv
import json
from pathlib import Path
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


def test_dockets_list_batch_treats_docket_column_as_id(monkeypatch, tmp_path):
    """A docket column with numeric IDs should fetch docket detail endpoints."""
    input_file = tmp_path / "dockets.csv"
    with open(input_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["docket"])
        writer.writeheader()
        writer.writerow({"docket": "70265088"})

    calls = []

    def mock_get(self, endpoint, **kwargs):
        calls.append((endpoint, kwargs.get("params")))
        return {"id": 70265088, "case_name": "United States v. Loredo"}

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
            "docket",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0][0] == "/dockets/70265088/"


def test_dockets_list_filters_by_docket_number(monkeypatch, tmp_path):
    """Direct dockets list should support docket-number filtering."""
    calls = []

    def mock_get(self, endpoint, **kwargs):
        calls.append((endpoint, kwargs.get("params")))
        return {"count": 1, "results": [{"id": 4214664}]}

    monkeypatch.setattr("src.commands.dockets_commands.CourtListenerClient.get", mock_get)

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "dockets",
            "list",
            "--docket-number",
            "1:16-cv-00745",
            "--court",
            "dcd",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert calls[0][0] == "/dockets/"
    assert calls[0][1]["docket_number"] == "1:16-cv-00745"
    assert calls[0][1]["court"] == "dcd"


@pytest.mark.parametrize(
    ("folder_name_mode", "expected_suffix"),
    [
        ("case-name-number", "United States v. Keeton ; 2_22-cr-00327"),
        ("docket-id", "68608890"),
        ("none", ""),
    ],
)
def test_download_docs_folder_name_mode_controls_output_dir(monkeypatch, tmp_path,
                                                            folder_name_mode, expected_suffix):
    """download-docs should let users choose how the output folder is named."""
    calls = []

    def mock_get(self, endpoint, **kwargs):
        assert endpoint == "/dockets/68608890/"
        return {
            "case_name": "United States v. Keeton",
            "case_name_short": "Keeton",
            "docket_number": "2:22-cr-00327",
        }

    def mock_try_csv_export(url, client, case_dir):
        return []

    def mock_save_xlsx(data, output_path, include_timestamp=False, filename_stem="results",
                       concat_list_fields_char=';'):
        calls.append((Path(output_path), filename_stem))
        return Path(output_path) / f"{filename_stem}.xlsx"

    monkeypatch.setattr("src.commands.dockets_commands.CourtListenerClient.get", mock_get)
    monkeypatch.setattr("src.commands.dockets_commands._try_csv_export", mock_try_csv_export)
    monkeypatch.setattr("src.commands.dockets_commands.save_xlsx", mock_save_xlsx)

    output_dir = tmp_path / "pdfs" / "68608890"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "dockets",
            "download-docs",
            "68608890",
            "--output",
            str(output_dir),
            "--folder-name-mode",
            folder_name_mode,
        ],
    )

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0][0] == output_dir / expected_suffix
    assert calls[0][1] == "docs_68608890"


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


def test_opinions_list_paginates_until_limit(monkeypatch, tmp_path):
    """opinions list should aggregate multiple pages until requested total."""
    page_1 = {
        "count": 35,
        "results": [{"id": i} for i in range(1, 21)],
        "next": "https://www.courtlistener.com/api/rest/v4/opinions/?cursor=abc&limit=100&offset=0",
    }
    page_2 = {
        "count": 35,
        "results": [{"id": i} for i in range(21, 36)],
        "next": None,
    }

    def mock_get(self, endpoint, **kwargs):
        cursor = kwargs.get("params", {}).get("cursor")
        return page_1 if cursor is None else page_2

    monkeypatch.setattr("src.commands.opinions_commands.CourtListenerClient.get", mock_get)

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["opinions", "list", "--limit", "25", "--format", "json", "--output", str(output_dir)],
    )

    assert result.exit_code == 0
    payload = json.loads((output_dir / "results.json").read_text())
    assert payload["returned_count"] == 25
    assert payload["pages_fetched"] == 2


def test_courts_list_limit_zero_max_pages_zero_fetches_all(monkeypatch, tmp_path):
    """courts list should fetch all pages when both caps are zero."""
    pages = {
        None: {
            "count": 3,
            "results": [{"id": 1}],
            "next": "https://www.courtlistener.com/api/rest/v4/courts/?cursor=2",
        },
        "2": {
            "count": 3,
            "results": [{"id": 2}],
            "next": "https://www.courtlistener.com/api/rest/v4/courts/?cursor=3",
        },
        "3": {
            "count": 3,
            "results": [{"id": 3}],
            "next": None,
        },
    }

    def mock_get(self, endpoint, **kwargs):
        cursor = kwargs.get("params", {}).get("cursor")
        return pages[cursor]

    monkeypatch.setattr("src.commands.courts_commands.CourtListenerClient.get", mock_get)

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "courts",
            "list",
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
    assert payload["returned_count"] == 3
    assert payload["pages_fetched"] == 3


def test_people_list_limit_zero_respects_max_pages(monkeypatch, tmp_path):
    """people list with limit zero should still stop at max-pages."""

    def mock_get(self, endpoint, **kwargs):
        cursor = kwargs.get("params", {}).get("cursor")
        if cursor is None:
            return {
                "count": 5,
                "results": [{"id": 1}],
                "next": "https://www.courtlistener.com/api/rest/v4/people/?cursor=2",
            }
        return {
            "count": 5,
            "results": [{"id": 2}],
            "next": "https://www.courtlistener.com/api/rest/v4/people/?cursor=3",
        }

    monkeypatch.setattr("src.commands.people_commands.CourtListenerClient.get", mock_get)

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "people",
            "list",
            "--limit",
            "0",
            "--max-pages",
            "1",
            "--format",
            "json",
            "--output",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads((output_dir / "results.json").read_text())
    assert payload["returned_count"] == 1
    assert payload["pages_fetched"] == 1


def test_audio_list_paginates_until_limit(monkeypatch, tmp_path):
    """audio list should aggregate pages until requested limit."""
    page_1 = {
        "count": 30,
        "results": [{"id": i} for i in range(1, 21)],
        "next": "https://www.courtlistener.com/api/rest/v4/audio/?cursor=abc&limit=100&offset=0",
    }
    page_2 = {
        "count": 30,
        "results": [{"id": i} for i in range(21, 31)],
        "next": None,
    }

    def mock_get(self, endpoint, **kwargs):
        cursor = kwargs.get("params", {}).get("cursor")
        return page_1 if cursor is None else page_2

    monkeypatch.setattr("src.commands.audio_commands.CourtListenerClient.get", mock_get)

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["audio", "list", "--limit", "25", "--format", "json", "--output", str(output_dir)],
    )

    assert result.exit_code == 0
    payload = json.loads((output_dir / "results.json").read_text())
    assert payload["returned_count"] == 25
    assert payload["pages_fetched"] == 2


def test_docket_entries_paginates_until_limit(monkeypatch, tmp_path):
    """dockets entries should aggregate pages and truncate to limit."""
    page_1 = {
        "count": 30,
        "results": [{"id": i} for i in range(1, 21)],
        "next": "https://www.courtlistener.com/api/rest/v4/docket-entries/?cursor=abc&limit=100",
    }
    page_2 = {
        "count": 30,
        "results": [{"id": i} for i in range(21, 31)],
        "next": None,
    }

    def mock_get(self, endpoint, **kwargs):
        cursor = kwargs.get("params", {}).get("cursor")
        return page_1 if cursor is None else page_2

    monkeypatch.setattr("src.commands.dockets_commands.CourtListenerClient.get", mock_get)

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "dockets",
            "entries",
            "123",
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
    assert payload["returned_count"] == 25
    assert payload["pages_fetched"] == 2


@pytest.mark.parametrize(
    "command,module_path,expected_endpoint,expected_params",
    [
        (
            ["opinions", "count", "--search", "brown"],
            "src.commands.opinions_commands.CourtListenerClient.get",
            "/opinions/",
            {"page_size": 1, "search": "brown"},
        ),
        (
            ["courts", "count", "--jurisdiction", "federal", "--court-type", "federal"],
            "src.commands.courts_commands.CourtListenerClient.get",
            "/courts/",
            {"page_size": 1, "jurisdiction": "federal", "court_type": "federal"},
        ),
        (
            ["dockets", "count", "--court", "scotus", "--case-name", "Roe"],
            "src.commands.dockets_commands.CourtListenerClient.get",
            "/dockets/",
            {"page_size": 1, "court": "scotus", "case_name": "Roe"},
        ),
        (
            ["people", "count", "--name", "Smith"],
            "src.commands.people_commands.CourtListenerClient.get",
            "/people/",
            {"page_size": 1, "name_last": "Smith"},
        ),
        (
            ["audio", "count", "--court", "ca9", "--year", "2020"],
            "src.commands.audio_commands.CourtListenerClient.get",
            "/audio/",
            {"page_size": 1, "docket__court": "ca9", "date_argued_gte": "2020-01-01", "date_argued_lte": "2020-12-31"},
        ),
        (
            ["search", "count", "--q", "Miranda", "--type", "r"],
            "src.commands.search_commands.CourtListenerClient.get",
            "/search/",
            {"limit": 1, "q": "Miranda", "type": "r"},
        ),
    ],
)
def test_count_commands_return_only_total(monkeypatch, command, module_path, expected_endpoint, expected_params):
    """Count subcommands should print the API count and request minimal payloads."""
    calls = []

    def mock_get(self, endpoint, **kwargs):
        calls.append((endpoint, kwargs.get("params", {})))
        return {"count": 123, "results": [{"id": 1}]}

    monkeypatch.setattr(module_path, mock_get)

    runner = CliRunner()
    result = runner.invoke(main, command)

    assert result.exit_code == 0
    assert result.output.strip() == "123"
    assert len(calls) == 1
    assert calls[0][0] == expected_endpoint
    assert calls[0][1] == expected_params
