# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""
Database connection utilities for Gemantria.

Provides centralized DB connection setup with fallback handling
and error management per governance requirements.

All DSN access must go through scripts.config.env (centralized loader).
"""

import sys
from pathlib import Path

# Add project root to path for imports
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn
import psycopg


def get_connection_dsn(env_var: str = "GEMATRIA_DSN", fallback: str = "DB_DSN") -> str:
    """
    Get database DSN with fallback and validation.

    Args:
        env_var: Primary environment variable name (default: GEMATRIA_DSN) - ignored, uses centralized loader
        fallback: Fallback environment variable name (default: DB_DSN) - ignored, uses centralized loader

    Returns:
        Valid database DSN string

    Raises:
        ValueError: If DSN cannot be determined
    """
    dsn = get_rw_dsn()
    if env_var != "GEMATRIA_DSN":
        print(
            f"🔥🔥🔥 LOUD HINT [db.dsn_env_var_ignored]: get_connection_dsn() ignores '{env_var}' arg. Use scripts.config.env for specific DBs (e.g. Bible DB). 🔥🔥🔥",
            file=sys.stderr,
        )
    if not dsn:
        raise ValueError("GEMATRIA_DSN environment variable required (via centralized loader)")
    return dsn


def get_db_connection(dsn: str | None = None) -> psycopg.Connection:
    """
    Get database connection with proper setup.

    Args:
        dsn: Optional DSN string (will use centralized loader if not provided)

    Returns:
        Configured database connection

    Raises:
        ValueError: If DSN cannot be determined
    """
    if dsn is None:
        dsn = get_connection_dsn()
    return psycopg.connect(dsn)
