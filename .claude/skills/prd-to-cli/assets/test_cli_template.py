"""
Basic CLI smoke tests for generated projects.
"""

import importlib.util

from click.testing import CliRunner
from src.cli import cli


def test_root_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "batch" in result.output


def test_batch_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["batch", "--help"])
    assert result.exit_code == 0


def test_selected_http_library_dependency_is_available():
    assert importlib.util.find_spec("{HTTP_LIBRARY}") is not None
