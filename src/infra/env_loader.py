#!/usr/bin/env python3
"""Environment variable loader with validation."""

import os
import sys
from pathlib import Path


def ensure_env_loaded():
    """Ensure environment variables are loaded from .env files."""
    # Load .env if it exists
    env_file = Path(".env")
    if env_file.exists():
        print(f"📄 Loading environment from {env_file}", file=sys.stderr)
        load_dotenv(env_file)

    # Load .env.local if it exists (overrides .env)
    env_local = Path(".env.local")
    if env_local.exists():
        print(f"📄 Loading local environment from {env_local}", file=sys.stderr)
        load_dotenv(env_local)


def load_dotenv(filepath):
    """Simple dotenv loader."""
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or (
                        value.startswith("'") and value.endswith("'")
                    ):
                        value = value[1:-1]

                    os.environ[key] = value
    except Exception as e:
        print(f"⚠️  Error loading {filepath}: {e}", file=sys.stderr)


def validate_required_env_vars():
    """Validate that required environment variables are set."""
    required = ["GEMATRIA_DSN", "BIBLE_DB_DSN"]

    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"❌ Missing required environment variables: {missing}", file=sys.stderr)
        sys.exit(1)

    print("✅ Required environment variables present", file=sys.stderr)


def get_env_var(name, default=None, required=False):
    """Get environment variable with optional default."""
    value = os.getenv(name, default)
    if required and value is None:
        print(f"❌ Required environment variable {name} not set", file=sys.stderr)
        sys.exit(1)
    return value
