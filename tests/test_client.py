"""Tests for CourtListener HTTP client."""

from src.client import CourtListenerClient


def test_headers_without_api_token_omit_authorization():
    client = CourtListenerClient(api_token="")
    headers = client._get_headers()

    assert "Authorization" not in headers
    assert headers["Content-Type"] == "application/json"
    assert headers["User-Agent"] == "courtlistener-cli/1.0.0"


def test_headers_with_api_token_include_authorization():
    client = CourtListenerClient(api_token="abc123")
    headers = client._get_headers()

    assert headers["Authorization"] == "Bearer abc123"
