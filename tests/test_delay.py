from click.testing import CliRunner
from src.cli import main
from unittest.mock import patch


def test_global_delay_sets_config():
    runner = CliRunner()
    with patch("src.cli.config") as mock_config:
        # Use a command that exists to trigger the main callback
        runner.invoke(main, ["--delay", "5.5", "courts", "count"])
        # Verify config.inter_page_delay was set
        assert mock_config.inter_page_delay == 5.5


def test_courts_list_passes_delay_to_pagination():
    runner = CliRunner()
    # Mock CourtListenerClient.get to return a simple page
    mock_response = {
        "count": 1,
        "results": [{"id": "scotus", "full_name": "Supreme Court"}],
        "next": None,
    }

    with patch(
        "src.commands.courts_commands.CourtListenerClient.get",
        return_value=mock_response,
    ):
        with patch("src.commands.courts_commands.paginate_endpoint") as mock_paginate:
            runner.invoke(main, ["courts", "list", "--delay", "2.5"])

            # Check if paginate_endpoint was called with the correct delay
            args, kwargs = mock_paginate.call_args
            assert kwargs.get("delay") == 2.5


def test_pagination_uses_delay():
    from src.pagination import paginate_endpoint

    # Simple page generator
    pages = [
        {"count": 2, "results": [{}], "next": "http://api/next?page=2"},
        {"count": 2, "results": [{}], "next": None},
    ]

    call_count = 0

    def fetch_page(params):
        nonlocal call_count
        res = pages[call_count]
        call_count += 1
        return res

    # We want to verify that time.sleep is called with the specified delay
    with patch("time.sleep") as mock_sleep:
        paginate_endpoint(
            fetch_page=fetch_page,
            initial_params={},
            limit=0,
            max_pages=0,  # No page cap
            delay=3.3,
        )
        # Should sleep exactly once between page 1 and page 2
        # After page 2, next is None, so it breaks before sleep.
        mock_sleep.assert_called_once_with(3.3)
