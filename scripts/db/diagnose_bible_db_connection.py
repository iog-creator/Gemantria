#!/usr/bin/env python3
"""Diagnose Bible DB connection issues and provide solutions.

This script helps diagnose connection problems to bible_db and provides
guidance on fixing authentication issues.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.config.env import get_bible_db_dsn


def check_dsn_config() -> dict:
    """Check DSN configuration from environment."""
    dsn = get_bible_db_dsn()
    return {
        "dsn_configured": dsn is not None,
        "dsn_value": dsn if dsn else None,
        "env_vars": {
            "BIBLE_DB_DSN": os.getenv("BIBLE_DB_DSN"),
            "BIBLE_RO_DSN": os.getenv("BIBLE_RO_DSN"),
            "RO_DSN": os.getenv("RO_DSN"),
            "ATLAS_DSN_RO": os.getenv("ATLAS_DSN_RO"),
            "ATLAS_DSN": os.getenv("ATLAS_DSN"),
        },
    }


def test_connection_methods() -> dict:
    """Test different connection methods."""
    results = {}

    # Method 1: Unix socket (from .env)
    dsn = get_bible_db_dsn()
    if dsn:
        results["method_1_unix_socket"] = {
            "dsn": dsn,
            "description": "Unix socket connection (from .env)",
        }
        try:
            import psycopg

            conn = psycopg.connect(dsn)
            conn.close()
            results["method_1_unix_socket"]["status"] = "SUCCESS"
        except Exception as e:
            results["method_1_unix_socket"]["status"] = f"FAILED: {e}"

    # Method 2: TCP with postgres user
    for password in ["postgres", "password", ""]:
        test_dsn = f"postgresql://postgres:{password}@localhost:5432/bible_db"
        try:
            import psycopg

            conn = psycopg.connect(test_dsn)
            conn.close()
            results[f"method_2_tcp_postgres_{password or 'empty'}"] = {
                "dsn": test_dsn.replace(password, "***") if password else test_dsn,
                "status": "SUCCESS",
            }
            break
        except Exception as e:
            results[f"method_2_tcp_postgres_{password or 'empty'}"] = {
                "dsn": test_dsn.replace(password, "***") if password else test_dsn,
                "status": f"FAILED: {e}",
            }

    # Method 3: TCP with mccoy user
    test_dsn = "postgresql://mccoy@localhost:5432/bible_db"
    try:
        import psycopg

        conn = psycopg.connect(test_dsn)
        conn.close()
        results["method_3_tcp_mccoy"] = {
            "dsn": test_dsn,
            "status": "SUCCESS",
        }
    except Exception as e:
        results["method_3_tcp_mccoy"] = {
            "dsn": test_dsn,
            "status": f"FAILED: {e}",
        }

    return results


def check_postgres_service() -> dict:
    """Check if PostgreSQL service is running."""
    import subprocess

    results = {}

    # Check if postgres is running
    try:
        result = subprocess.run(
            ["pg_isready", "-h", "localhost", "-p", "5432"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        results["pg_isready"] = {
            "status": "RUNNING" if result.returncode == 0 else "NOT_RUNNING",
            "output": result.stdout.strip(),
        }
    except Exception as e:
        results["pg_isready"] = {
            "status": "ERROR",
            "error": str(e),
        }

    # Check Unix socket
    socket_path = Path("/var/run/postgresql")
    results["unix_socket"] = {
        "path": str(socket_path),
        "exists": socket_path.exists(),
        "readable": socket_path.is_dir() and os.access(socket_path, os.R_OK),
    }

    return results


def main() -> int:
    """Main diagnostic function."""
    print("=" * 80)
    print("Bible DB Connection Diagnostic")
    print("=" * 80)
    print()

    # Check DSN configuration
    print("1. DSN Configuration:")
    print("-" * 80)
    dsn_config = check_dsn_config()
    print(f"   DSN Configured: {dsn_config['dsn_configured']}")
    if dsn_config["dsn_value"]:
        # Redact password if present
        dsn_display = dsn_config["dsn_value"]
        if "@" in dsn_display and ":" in dsn_display.split("@")[0]:
            parts = dsn_display.split("@")
            user_pass = parts[0].split("://")[1]
            if ":" in user_pass:
                user, _ = user_pass.split(":", 1)
                dsn_display = dsn_display.replace(user_pass, f"{user}:***")
        print(f"   DSN Value: {dsn_display}")
    print("   Environment Variables:")
    for key, value in dsn_config["env_vars"].items():
        if value:
            # Redact password
            if "@" in value and ":" in value.split("@")[0]:
                parts = value.split("@")
                user_pass = parts[0].split("://")[1]
                if ":" in user_pass:
                    user, _ = user_pass.split(":", 1)
                    value = value.replace(user_pass, f"{user}:***")
            print(f"     {key}: {value}")
        else:
            print(f"     {key}: (not set)")
    print()

    # Check PostgreSQL service
    print("2. PostgreSQL Service Status:")
    print("-" * 80)
    service_status = check_postgres_service()
    for key, value in service_status.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"     {k}: {v}")
        else:
            print(f"   {key}: {value}")
    print()

    # Test connection methods
    print("3. Connection Method Tests:")
    print("-" * 80)
    connection_tests = test_connection_methods()
    for method, result in connection_tests.items():
        print(f"   {method}:")
        if isinstance(result, dict):
            for k, v in result.items():
                print(f"     {k}: {v}")
        else:
            print(f"     {result}")
    print()

    # Recommendations
    print("4. Recommendations:")
    print("-" * 80)

    working_methods = [k for k, v in connection_tests.items() if isinstance(v, dict) and v.get("status") == "SUCCESS"]

    if working_methods:
        print(f"   ✓ Found {len(working_methods)} working connection method(s):")
        for method in working_methods:
            print(f"     - {method}")
        print()
        print("   Next steps:")
        print("   1. Use the working DSN from above")
        print("   2. Update .env file if needed")
        print("   3. Run the data recovery script")
    else:
        print("   ✗ No working connection methods found.")
        print()
        print("   Troubleshooting steps:")
        print("   1. Check if PostgreSQL is running:")
        print("      sudo systemctl status postgresql")
        print("   2. Check PostgreSQL authentication configuration:")
        print("      cat /etc/postgresql/*/main/pg_hba.conf")
        print("   3. Try connecting manually:")
        print("      psql -U postgres -d bible_db")
        print("      # or")
        print("      psql -U mccoy -d bible_db -h /var/run/postgresql")
        print("   4. If using password auth, reset postgres password:")
        print("      sudo -u postgres psql")
        print("      ALTER USER postgres PASSWORD 'your_password';")

    print()
    print("=" * 80)

    return 0 if working_methods else 1


if __name__ == "__main__":
    sys.exit(main())
