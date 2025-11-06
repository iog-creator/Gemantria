"""
Configuration management for the Gematria pipeline.

This is a placeholder module. The original EnvManager class
has been replaced with direct calls to ensure_env_loaded().
"""

from src.infra.env_loader import ensure_env_loaded


class EnvManager:
    """
    Placeholder EnvManager class for backward compatibility.
    This just calls ensure_env_loaded() to maintain the same behavior.
    """

    def __init__(self):
        ensure_env_loaded()
