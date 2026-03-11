"""HTTP client for CourtListener API using httpx"""

import httpx
from typing import Any, Dict, Optional
from .config import config


class CourtListenerClient:
    """HTTP client wrapper for CourtListener API"""
    
    def __init__(self, api_token: Optional[str] = None, base_url: Optional[str] = None):
        self.api_token = api_token if api_token is not None else config.api_token
        self.base_url = base_url or config.base_url
        self.timeout = config.timeout
        self.client = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'courtlistener-cli/1.0.0'
        }
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        return headers
    
    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        with httpx.Client(headers=headers, timeout=self.timeout) as client:
            response = client.request(method, url, **kwargs)
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
