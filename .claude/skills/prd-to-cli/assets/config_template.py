"""
Configuration management for generated CLI projects.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from src.utils import parse_env_value


class Config:
    """Load and manage key/value configuration from a .env-style file."""

    def __init__(self, config_path: Optional[str] = None):
        project_root = Path(__file__).resolve().parent.parent
        self.config_path = Path(config_path).resolve() if config_path else project_root / ".env"
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration values from file."""
        self.config = {}
        load_dotenv(self.config_path, override=False)

        if not self.config_path.exists():
            return

        with open(self.config_path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                self.config[key.strip()] = parse_env_value(value.strip())

        for key in list(self.config.keys()):
            if key in os.environ:
                self.config[key] = parse_env_value(os.environ[key])

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value

    def save(self):
        """Persist configuration values to disk."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            for key, value in self.config.items():
                f.write(f"{key}={value}\n")
