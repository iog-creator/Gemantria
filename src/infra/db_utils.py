# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""
Database connection utilities for Gemantria.

Provides centralized DB connection setup with fallback handling
and error management per governance requirements.
"""

import os
import psycopg


def get_connection_dsn(env_var: str = "GEMATRIA_DSN", fallback: str = "DB_DSN") -> str:
    """
    Get database DSN with fallback and validation.

    Args:
        env_var: Primary environment variable name (default: GEMATRIA_DSN)
        fallback: Fallback environment variable name (default: DB_DSN)

    Returns:
        Valid database DSN string

    Raises:
        ValueError: If neither environment variable is set
    """
    dsn = os.getenv(env_var) or os.getenv(fallback)
    if not dsn:
        raise ValueError(f"{env_var} environment variable required")
    return dsn


def get_db_connection(dsn: str | None = None) -> psycopg.Connection:
    """
    Get database connection with proper setup.

    Args:
        dsn: Optional DSN string (will use environment if not provided)

    Returns:
        Configured database connection

    Raises:
        ValueError: If DSN cannot be determined
    """
    if dsn is None:
        dsn = get_connection_dsn()
    return psycopg.connect(dsn)
