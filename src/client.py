"""HTTP client for CourtListener API using httpx"""

import time
import logging
import httpx
import click
from typing import Any, Dict, Optional
from .config import config

logger = logging.getLogger(__name__)

_DEFAULT_RETRY_WAIT = 60   # seconds to wait on 429 when no Retry-After header
_MAX_RETRY_WAIT = 3600     # treat as daily quota only if server asks to wait > 1 hour
_MAX_RETRIES = 5


class DailyQuotaExceeded(Exception):
    """Raised when the API signals a daily rate limit with a long Retry-After."""
    def __init__(self, wait: int):
        self.wait = wait
        hours, rem = divmod(wait, 3600)
        minutes = rem // 60
        super().__init__(
            f'Daily rate limit exceeded. CourtListener asks to wait {wait}s '
            f'({hours}h {minutes}m). Try again later.'
        )


class CourtListenerClient:
    """HTTP client wrapper for CourtListener API"""

    def __init__(self, api_token: Optional[str] = None, base_url: Optional[str] = None, no_cache: Optional[bool] = None):
        self.api_token = api_token if api_token is not None else config.api_token
        self.base_url = base_url or config.base_url
        self.timeout = config.timeout
        
        # Detect no_cache from click context if not provided
        if no_cache is None:
            ctx = click.get_current_context(silent=True)
            if ctx and ctx.obj:
                no_cache = ctx.obj.get('no_cache', False)
        
        self.no_cache = no_cache or False
        self.client = None

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'courtlistener-cli/1.0.0'
        }
        if self.api_token:
            headers['Authorization'] = f'Token {self.api_token}'
        if self.no_cache:
            headers['Cache-Control'] = 'no-cache'
        return headers

    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the API, retrying on 429 with backoff."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        for attempt in range(1, _MAX_RETRIES + 1):
            with httpx.Client(headers=headers, timeout=self.timeout) as client:
                response = client.request(method, url, **kwargs)

            if response.status_code == 429:
                wait = int(response.headers.get('Retry-After', _DEFAULT_RETRY_WAIT))
                if wait > _MAX_RETRY_WAIT:
                    raise DailyQuotaExceeded(wait)
                logger.warning('Rate limited (429). Waiting %ds before retry %d/%d…', wait, attempt, _MAX_RETRIES)
                print(f'  ⏳ Rate limited — waiting {wait}s before retry {attempt}/{_MAX_RETRIES}…')
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response.json() if response.text else {}

        # Final attempt after all retries exhausted
        response.raise_for_status()
        return response.json() if response.text else {}
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request"""
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request"""
        return self.request('POST', endpoint, json=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Make a PUT request"""
        return self.request('PUT', endpoint, json=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request"""
        return self.request('DELETE', endpoint, **kwargs)
