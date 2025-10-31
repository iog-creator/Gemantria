"""
Environment loading utility for consistent .env file handling across all scripts.

This module provides a standardized way to load environment variables from .env files,
preventing the persistent database connectivity issues caused by inconsistent loading.
"""

import os
from pathlib import Path


def load_env_file(env_path: Path = Path(".env")) -> None:
    """
    Load environment variables from .env file.

    Args:
        env_path: Path to the .env file (defaults to .env in current directory)
    """
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            # Remove surrounding quotes if present
            if value and len(value) >= 2 and value[0] == value[-1] and value[0] in ['"', "'"]:
                value = value[1:-1]
            os.environ[key] = value


def ensure_env_loaded() -> None:
    """
    Ensure environment variables are loaded from .env file.

    This should be called at the beginning of all scripts that need database access.
    """
    load_env_file()


__all__ = ["ensure_env_loaded", "load_env_file"]
