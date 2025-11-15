#!/usr/bin/env python3
"""
Reality Check #1: Automated Bring-Up Script

E2E Pipeline (Reality Check #1): Automated bring-up for SSOT Docs → Postgres → LM Studio Q&A.

This script:
1. Starts/verifies Postgres (using DB_START_CMD if set)
2. Starts/verifies LM Studio server + loads model using `lms` CLI
3. Runs `ingest_docs` and `pmagent ask docs "What does Phase-6P deliver?"`
4. Emits machine-readable result (success/failure + reasons)

Usage:
    python -m agentpm.scripts.reality_check_1
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.config.env import get_rw_dsn  # noqa: E402
from scripts.guards.guard_db_health import check_db_health  # noqa: E402
from scripts.guards.guard_lm_health import check_lm_health  # noqa: E402


def run_command(cmd: list[str] | str, timeout: int = 30, check: bool = False) -> tuple[int, str, str]:
    """
    Run a shell command and return (returncode, stdout, stderr).

    Args:
        cmd: Command to run (list of strings or string)
        timeout: Timeout in seconds
        check: If True, raise CalledProcessError on non-zero exit

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    if isinstance(cmd, str):
        cmd = ["sh", "-c", cmd]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return 1, "", str(e)


def check_postgres_running() -> tuple[bool, str]:
    """
    Check if Postgres is running and accessible.

    Returns:
        Tuple of (is_running, reason)
    """
    # Check via pg_isready if available
    code, _stdout, _stderr = run_command(["pg_isready"], timeout=5, check=False)
    if code == 0:
        return True, "pg_isready reports ready"

    # Check via DSN connection
    dsn = get_rw_dsn()
    if not dsn:
        return False, "GEMATRIA_DSN not set"

    try:
        import psycopg

        with psycopg.connect(dsn, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True, "Database connection successful"
    except ImportError:
        return False, "psycopg not installed"
    except Exception as e:
        return False, f"Database connection failed: {e}"


def start_postgres() -> tuple[bool, str]:
    """
    Start Postgres using DB_START_CMD if set.

    Returns:
        Tuple of (success, reason)
    """
    db_start_cmd = os.getenv("DB_START_CMD", "").strip()
    if not db_start_cmd:
        return False, "DB_START_CMD not set (skipping auto-start)"

    code, stdout, stderr = run_command(db_start_cmd, timeout=30, check=False)
    if code == 0:
        # Wait a moment for Postgres to start
        time.sleep(2)
        is_running, reason = check_postgres_running()
        if is_running:
            return True, f"Postgres started via DB_START_CMD: {reason}"
        else:
            return False, f"DB_START_CMD succeeded but Postgres not accessible: {reason}"
    else:
        return False, f"DB_START_CMD failed: {stderr or stdout}"


def ensure_postgres() -> tuple[bool, str]:
    """
    Ensure Postgres is running (check first, start if needed).

    Returns:
        Tuple of (success, reason)
    """
    is_running, reason = check_postgres_running()
    if is_running:
        return True, reason

    # Try to start Postgres
    success, start_reason = start_postgres()
    if success:
        return True, start_reason

    return False, f"Postgres not running ({reason}) and auto-start failed ({start_reason})"


def check_lm_studio_running() -> tuple[bool, str]:
    """
    Check if LM Studio server is running.

    Returns:
        Tuple of (is_running, reason)
    """
    # Check via health check
    health = check_lm_health()
    if health.get("ok") and health.get("mode") == "lm_ready":
        return True, "LM Studio health check passed"

    # Check if port is listening
    port = os.getenv("LM_STUDIO_SERVER_PORT", "1234").strip() or "1234"
    code, stdout, _stderr = run_command(["lsof", "-i", f":{port}"], timeout=5, check=False)
    if code == 0 and stdout:
        return True, f"LM Studio server listening on port {port}"

    return False, f"LM Studio server not running on port {port}"


def start_lm_studio_server() -> tuple[bool, str]:
    """
    Start LM Studio server using `lms server start`.

    Returns:
        Tuple of (success, reason)
    """
    port = os.getenv("LM_STUDIO_SERVER_PORT", "1234").strip() or "1234"

    # Check if lms CLI is available
    code, _, _ = run_command(["lms", "--version"], timeout=5, check=False)
    if code != 0:
        return False, "lms CLI not found (install LM Studio CLI)"

    # Start server
    code, stdout, stderr = run_command(["lms", "server", "start", "--port", port, "--gpu=1.0"], timeout=10, check=False)
    if code == 0:
        # Wait a moment for server to start
        time.sleep(3)
        is_running, reason = check_lm_studio_running()
        if is_running:
            return True, f"LM Studio server started on port {port}: {reason}"
        else:
            return False, f"lms server start succeeded but server not accessible: {reason}"
    else:
        # Server might already be running
        is_running, reason = check_lm_studio_running()
        if is_running:
            return True, f"LM Studio server already running: {reason}"
        return False, f"lms server start failed: {stderr or stdout}"


def load_lm_studio_model() -> tuple[bool, str]:
    """
    Load LM Studio model using `lms load` if LM_STUDIO_MODEL_ID is set.

    Returns:
        Tuple of (success, reason)
    """
    model_id = os.getenv("LM_STUDIO_MODEL_ID", "").strip()
    if not model_id:
        return True, "LM_STUDIO_MODEL_ID not set (skipping model load; models load on-demand)"

    # Check if lms CLI is available
    code, _, _ = run_command(["lms", "--version"], timeout=5, check=False)
    if code != 0:
        return False, "lms CLI not found (install LM Studio CLI)"

    # Load model
    code, stdout, stderr = run_command(["lms", "load", model_id], timeout=60, check=False)
    if code == 0:
        return True, f"Model {model_id} loaded successfully"
    else:
        return False, f"lms load failed: {stderr or stdout}"


def ensure_lm_studio() -> tuple[bool, str]:
    """
    Ensure LM Studio is running and model is loaded.

    Returns:
        Tuple of (success, reason)
    """
    is_running, reason = check_lm_studio_running()
    if not is_running:
        success, start_reason = start_lm_studio_server()
        if not success:
            return False, f"LM Studio not running ({reason}) and auto-start failed ({start_reason})"
        reason = start_reason

    # Try to load model (non-fatal)
    load_success, load_reason = load_lm_studio_model()
    if not load_success:
        # Model loading is optional (models can load on-demand)
        reason += f" (model load skipped: {load_reason})"

    return True, reason


def run_ingest_docs() -> tuple[bool, str]:
    """
    Run the doc ingestion script.

    Returns:
        Tuple of (success, reason)
    """
    code, stdout, stderr = run_command([sys.executable, "-m", "agentpm.scripts.ingest_docs"], timeout=60, check=False)
    if code == 0:
        return True, "Doc ingestion completed successfully"
    else:
        return False, f"Doc ingestion failed: {stderr or stdout}"


def run_golden_question() -> tuple[bool, str, dict[str, Any] | None]:
    """
    Run the golden question via pmagent ask docs.

    Returns:
        Tuple of (success, reason, answer_json)
    """
    code, stdout, stderr = run_command(
        ["pmagent", "ask", "docs", "What does Phase-6P deliver?"], timeout=60, check=False
    )
    if code == 0:
        # Try to parse JSON from stdout
        try:
            answer_json = json.loads(stdout)
            return True, "Golden question answered successfully", answer_json
        except json.JSONDecodeError:
            return True, f"Golden question answered (non-JSON output): {stdout[:200]}", None
    else:
        return False, f"Golden question failed: {stderr or stdout}", None


def main() -> int:
    """Main entry point for Reality Check #1 bring-up."""
    result: dict[str, Any] = {
        "ok": False,
        "steps": {},
        "summary": "",
        "errors": [],
    }

    # Step 1: Ensure Postgres
    print("[1/4] Ensuring Postgres is running...", file=sys.stderr)
    db_ok, db_reason = ensure_postgres()
    result["steps"]["postgres"] = {"ok": db_ok, "reason": db_reason}
    if not db_ok:
        result["errors"].append(f"Postgres: {db_reason}")
        result["summary"] = "Postgres bring-up failed"
        print(json.dumps(result, indent=2))
        return 1

    # Verify DB health
    db_health = check_db_health()
    result["steps"]["postgres_health"] = db_health

    # Step 2: Ensure LM Studio
    print("[2/4] Ensuring LM Studio is running...", file=sys.stderr)
    lm_ok, lm_reason = ensure_lm_studio()
    result["steps"]["lm_studio"] = {"ok": lm_ok, "reason": lm_reason}
    if not lm_ok:
        result["errors"].append(f"LM Studio: {lm_reason}")
        result["summary"] = "LM Studio bring-up failed"
        print(json.dumps(result, indent=2))
        return 1

    # Verify LM health
    lm_health = check_lm_health()
    result["steps"]["lm_studio_health"] = lm_health

    # Step 3: Run doc ingestion
    print("[3/4] Running doc ingestion...", file=sys.stderr)
    ingest_ok, ingest_reason = run_ingest_docs()
    result["steps"]["ingest_docs"] = {"ok": ingest_ok, "reason": ingest_reason}
    if not ingest_ok:
        result["errors"].append(f"Ingest: {ingest_reason}")
        result["summary"] = "Doc ingestion failed"
        print(json.dumps(result, indent=2))
        return 1

    # Step 4: Run golden question
    print("[4/4] Running golden question...", file=sys.stderr)
    question_ok, question_reason, answer_json = run_golden_question()
    result["steps"]["golden_question"] = {"ok": question_ok, "reason": question_reason}
    if answer_json:
        result["steps"]["golden_question"]["answer"] = answer_json
    if not question_ok:
        result["errors"].append(f"Golden question: {question_reason}")
        result["summary"] = "Golden question failed"
        print(json.dumps(result, indent=2))
        return 1

    # All steps passed
    result["ok"] = True
    result["summary"] = "Reality Check #1 passed: All steps completed successfully"
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
