"""
Logging setup utilities for generated CLI projects.
"""

import logging
import sys


def setup_logger(name: str = "{PROJECT_NAME_DASH}", verbose: bool = False) -> logging.Logger:
    """Configure and return a process-wide logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
