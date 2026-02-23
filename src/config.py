"""Configuration management for CourtListener CLI"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration handler"""
    
    def __init__(self):
        # Load .env file
        env_file = Path('.env')
        if env_file.exists():
            load_dotenv(env_file)
    
    @property
    def api_token(self) -> str:
        """Get API token from environment"""
        return os.getenv('COURTLISTENER_API_TOKEN', '')
    
    @property
    def base_url(self) -> str:
        """Get API base URL"""
        return os.getenv('COURTLISTENER_BASE_URL', 'https://www.courtlistener.com/api/rest/v4')
    
    @property
    def timeout(self) -> int:
        """Get request timeout in seconds"""
        return int(os.getenv('COURTLISTENER_TIMEOUT', '30'))
    
    @property
    def log_level(self) -> str:
        """Get log level"""
        return os.getenv('LOG_LEVEL', 'DEBUG')
    
    @property
    def log_to_file(self) -> bool:
        """Check if logging to file"""
        return os.getenv('LOG_TO_FILE', 'false').lower() == 'true'
    
    @property
    def output_format(self) -> str:
        """Get default output format"""
        return os.getenv('OUTPUT_FORMAT', 'xlsx')
    
    @property
    def include_timestamp(self) -> bool:
        """Check if timestamps should be included"""
        return os.getenv('INCLUDE_TIMESTAMP', 'true').lower() == 'true'


# Global config instance
config = Config()
