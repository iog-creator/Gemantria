#!/usr/bin/env python3
"""
Master Reference tracker runner (OPS v6.2).

- Loads env via centralized loader.
- DSN policy:
    * Tag/STRICT mode: require RO DSN (GEMATRIA_RO_DSN or ATLAS_DSN_RO). Fail closed if absent.
    * Dev/non-tag: prefer RO; fall back to RW (GEMATRIA_DSN) for read-only queries performed by the tracker.
- Calls scripts.populate_document_sections --all (import or subprocess).
- HINT mode (STRICT_MASTER_REF!=1) will skip gracefully if prerequisites are missing.
"""

from __future__ import annotations

import os
import sys
import importlib
import subprocess
import traceback
from pathlib import Path

# Add project root to path for imports
REPO = Path(__file__).resolve().parents[2]  # scripts/ops/master_ref_populate.py -> repo root
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

# Import centralized env loader at module level
from scripts.config.env import env, get_ro_dsn, get_rw_dsn


def echo(msg: str, err: bool = False):
    (sys.stderr if err else sys.stdout).write(msg + "\n")
    (sys.stderr if err else sys.stdout).flush()


def fail(msg: str, code: int = 2):
    echo(f"[masterref] {msg}", err=True)
    sys.exit(code)


def load_env():
    try:
        # scripts.config.env auto-loads .env via _ensure_loaded() when env() is called
        from scripts.config.env import env

        # Trigger env loading by calling env() once
        env("PATH")  # Non-fatal call to trigger _ensure_loaded()
        return True
    except Exception as e:
        echo(f"[masterref] env loader not available: {e}")
        if os.getenv("GITHUB_REF_TYPE") == "tag" or os.getenv("STRICT_MASTER_REF") == "1":
            fail("missing env loader in STRICT/tag mode", 5)
        return False


def resolve_dsn() -> str | None:
    ro = env("GEMATRIA_RO_DSN") or env("ATLAS_DSN_RO")
    try:
        ro = ro or get_ro_dsn()
    except Exception:
        pass
    if os.getenv("GITHUB_REF_TYPE") == "tag" or os.getenv("STRICT_MASTER_REF") == "1":
        return ro
    # dev: prefer RO, fallback to RW
    if ro:
        return ro
    try:
        return get_rw_dsn()
    except Exception:
        return None


def run_populate() -> int:
    # Try module form first
    try:
        mod = importlib.import_module("scripts.populate_document_sections")
        if hasattr(mod, "main"):
            # Call main with --all argument
            # Temporarily replace sys.argv
            old_argv = sys.argv
            sys.argv = ["populate_document_sections.py", "--all"]
            try:
                result = mod.main()
                return int(result or 0)
            finally:
                sys.argv = old_argv
    except Exception as e:
        echo(f"[masterref] module import failed: {e}")

    # Fallback: file runner
    cmd = [sys.executable, "scripts/populate_document_sections.py", "--all"]
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        echo("[masterref] populate_document_sections.py not found")
        return 127


def main() -> int:
    strict = os.getenv("STRICT_MASTER_REF") == "1" or os.getenv("GITHUB_REF_TYPE") == "tag"
    load_env()
    dsn = resolve_dsn()
    if not dsn:
        if strict:
            fail(
                "no DSN (need GEMATRIA_RO_DSN/ATLAS_DSN_RO in tag/STRICT, or GEMATRIA_DSN in dev)",
                2,
            )
        echo("[masterref] no DSN; skipping in HINT mode")
        return 0

    # Set DSN in environment for populate script
    os.environ["GEMATRIA_DSN"] = dsn

    try:
        rc = run_populate()
        if rc != 0 and strict:
            fail(f"populate script exited {rc}", rc)
        echo(f"[masterref] populate exited {rc}")
        return 0 if not strict else rc
    except Exception as e:
        echo("[masterref] exception:\n" + "".join(traceback.format_exc()), err=True)
        if strict:
            fail("exception during populate", 4)
        return 0


if __name__ == "__main__":
    sys.exit(main())
