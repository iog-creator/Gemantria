# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Comprehensive Guard Orchestrator

Runs all SSOT guards and validates schema compliance, business rules,
and data integrity across the entire pipeline.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infra.evidence_logger import get_evidence_logger, finalize_all_evidence
from scripts.config.env import get_rw_dsn, get_bible_db_dsn


def run_guard_script(script_path: str, description: str) -> Dict[str, Any]:
    """
    Run a guard script and capture its results.

    Args:
        script_path: Path to the guard script
        description: Human-readable description of the guard

    Returns:
        Dict with success status and details
    """
    try:
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=30)

        success = result.returncode == 0
        output = result.stdout.strip()
        error = result.stderr.strip()

        if success:
            message = output or f"{description} passed"
        else:
            message = error or output or f"{description} failed"

        return {"success": success, "message": message, "script": script_path, "description": description}

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": f"{description} timed out after 30 seconds",
            "script": script_path,
            "description": description,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"{description} error: {e!s}",
            "script": script_path,
            "description": description,
        }


def main():
    """Run all comprehensive guards."""
    # Initialize evidence logger
    evidence = get_evidence_logger("guard_all")

    try:
        evidence.log_evidence("guards_start", {"agent": "guard_all", "purpose": "Comprehensive SSOT validation"})

        # Define all guards to run
        guards = [
            ("scripts/guard_ai_nouns.py", "AI Nouns SSOT Schema Validation"),
            ("scripts/guard_graph_schema.py", "Graph SSOT Schema Validation"),
        ]

        # Add Hebrew export guard (SQL-based)
        if Path("scripts/sql/guard_hebrew_export.sql").exists():
            guards.append(("scripts/sql/guard_hebrew_export.sql", "Hebrew Export Integrity (SQL)"))

        results = []
        passed = 0
        failed = 0

        print(">> Running Comprehensive Guards", file=sys.stderr)
        print("=" * 50, file=sys.stderr)

        for script_path, description in guards:
            print(f"Running: {description}", file=sys.stderr)

            if script_path.endswith(".sql"):
                # SQL-based guard - run via psql
                result = run_sql_guard(script_path, description)
            else:
                # Python script guard
                result = run_guard_script(script_path, description)

            results.append(result)

            if result["success"]:
                passed += 1
                print(f"✅ PASS: {result['message']}", file=sys.stderr)
                evidence.log_validation_result(description, True, {"message": result["message"]})
            else:
                failed += 1
                print(f"❌ FAIL: {result['message']}", file=sys.stderr)
                evidence.log_validation_result(description, False, {"message": result["message"]})

            print(file=sys.stderr)

        # Summary
        total = len(guards)
        success = failed == 0

        summary = {
            "total_guards": total,
            "passed": passed,
            "failed": failed,
            "success": success,
            "guard_results": results,
        }

        if success:
            print(f"GUARDS_ALL_OK: {passed}/{total} guards passed", file=sys.stderr)
            evidence.log_agent_result(True, summary)
            return 0
        else:
            print(f"GUARDS_ALL_FAILED: {failed}/{total} guards failed", file=sys.stderr)
            evidence.log_agent_result(False, summary, f"{failed} guards failed")
            return 1

    except Exception as e:
        error_msg = str(e)
        print(f"GUARDS_ALL_ERROR: {error_msg}", file=sys.stderr)
        evidence.log_agent_result(False, {}, error_msg)
        return 1
    finally:
        finalize_all_evidence()


def run_sql_guard(sql_path: str, description: str) -> Dict[str, Any]:
    """
    Run a SQL-based guard script.

    Args:
        sql_path: Path to SQL file
        description: Description of the guard

    Returns:
        Dict with success status and details
    """
    try:
        # Get DSN from environment
        dsn = get_rw_dsn()
        if not dsn:
            return {
                "success": False,
                "message": "GEMATRIA_DSN not set for SQL guard",
                "script": sql_path,
                "description": description,
            }

        # Run psql command
        result = subprocess.run(["psql", dsn, "-f", sql_path], capture_output=True, text=True, timeout=30)

        # Parse psql output - look for errors or empty_hebrew counts
        output_lines = result.stdout.strip().split("\n")
        error_lines = [line for line in output_lines if line.strip()]

        if result.returncode == 0:
            # Check if there are any error counts > 0
            has_errors = False
            for line in error_lines:
                if line.startswith("empty_hebrew"):
                    parts = line.split("|")
                    if len(parts) >= 3:
                        try:
                            count = int(parts[2].strip())
                            if count > 0:
                                has_errors = True
                                break
                        except ValueError:
                            pass

            if has_errors:
                return {
                    "success": False,
                    "message": f"SQL guard found integrity issues: {'; '.join(error_lines)}",
                    "script": sql_path,
                    "description": description,
                }
            else:
                return {
                    "success": True,
                    "message": f"SQL guard passed: {'; '.join(error_lines) if error_lines else 'no issues found'}",
                    "script": sql_path,
                    "description": description,
                }
        else:
            return {
                "success": False,
                "message": f"SQL guard failed: {result.stderr.strip()}",
                "script": sql_path,
                "description": description,
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "SQL guard timed out after 30 seconds",
            "script": sql_path,
            "description": description,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"SQL guard error: {e!s}",
            "script": sql_path,
            "description": description,
        }


if __name__ == "__main__":
    sys.exit(main())
