#!/usr/bin/env python3
"""
sync_share.py — DMS-driven share sync (Phase 24.C).

- Fetches allowed paths from DMS.
- Populates share/ from repo (fixes missing_in_share).
- Audits share/ for unknown files (extra_in_share).
- STRICT mode: Aborts if unknown managed files exist.
- DEV mode: Warns if unknown managed files exist.
- NEVER DELETE files silently.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import json
from pathlib import Path
from typing import List

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Pre-flight DB check (mandatory - Rule 050 evidence-first)
preflight_script = ROOT / "scripts" / "ops" / "preflight_db_check.py"
result = subprocess.run([sys.executable, str(preflight_script), "--mode", "strict"], capture_output=True)
if result.returncode != 0:
    print(result.stderr.decode(), file=sys.stderr)
    sys.exit(result.returncode)

try:
    from sqlalchemy import text
    from pmagent.db.loader import get_control_engine

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

REPO_ROOT = ROOT
SHARE_ROOT = REPO_ROOT / "share"


def run_guard(mode: str) -> dict:
    """Run guard_share_sync_policy.py and return output."""
    guard_script = ROOT / "scripts" / "guards" / "guard_share_sync_policy.py"
    if not guard_script.exists():
        print(f"[sync_share] ERROR: Guard script missing at {guard_script}", file=sys.stderr)
        sys.exit(1)

    # We run the guard in HINT mode initially to get the data without exiting on failure
    # We will enforce policy locally
    res = subprocess.run([sys.executable, str(guard_script), "--mode", "HINT"], capture_output=True, text=True)
    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError:
        print(f"[sync_share] ERROR: Invalid JSON from guard:\n{res.stdout}", file=sys.stderr)
        return {"ok": False, "extra_in_share": [], "missing_in_share": []}


def _sync_from_registry(strict: bool = True) -> bool:
    if not DB_AVAILABLE:
        print("[sync_share] ERROR: Database not available.", file=sys.stderr)
        sys.exit(1)

    print("[sync_share] Running Share Sync Policy Guard...")
    report = run_guard("HINT")

    extra_in_share = report.get("extra_in_share", [])

    # Policy Enforcement: Extra Files
    if extra_in_share:
        msg = f"[sync_share] Found {len(extra_in_share)} unknown files in managed namespaces:\n" + "\n".join(
            f"  - {f}" for f in extra_in_share
        )

        if strict:
            print(
                f"{msg}\n[sync_share] STRICT MODE: Aborting sync. Register these files in DMS or move them to share/tmp/.",
                file=sys.stderr,
            )
            sys.exit(1)
        else:
            print(f"{msg}\n[sync_share] WARN: Skipping strictly managed check (DEV mode). Files will NOT be deleted.")

    # Proceed to Populate (Fix Missing)
    # We re-fetch allowlist to know source paths using same logic as guard/previous version
    # Actually guard logic doesn't give us source paths, only status.
    # So we need to query DB again to get (repo_path -> share_path) mapping.

    try:
        engine = get_control_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                SELECT logical_name, repo_path, share_path
                FROM control.doc_registry 
                WHERE enabled = TRUE
            """)
            ).fetchall()

            SHARE_ROOT.mkdir(parents=True, exist_ok=True)

            count = 0
            for row in rows:
                sp = row.share_path
                if not sp and row.repo_path and row.repo_path.startswith("share/"):
                    sp = row.repo_path

                if not sp:
                    continue

                repo_path = REPO_ROOT / row.repo_path
                share_path = REPO_ROOT / sp

                if not repo_path.exists():
                    print(f"[sync_share] WARN: Source missing for {row.logical_name}: {repo_path}")
                    continue

                # Check if update needed
                # For now, just copy (blind overwrite is safe as source is SSOT)
                # Optimization: check mtime or hash? sync_share usually forces copy.

                if not share_path.parent.exists():
                    share_path.parent.mkdir(parents=True, exist_ok=True)

                # Avoid copy if src and dst are the same file
                if repo_path.resolve() == share_path.resolve():
                    # print(f"[sync_share] skipping copy (same file): {row.logical_name}")
                    continue

                shutil.copy2(repo_path, share_path)
                count += 1

            print(f"[sync_share] Populated {count} files from DMS.")

    except Exception as e:
        print(f"[sync_share] ERROR: Sync failed: {e}", file=sys.stderr)
        sys.exit(1)

    return True


def main(argv: List[str] | None = None) -> int:
    # Determine mode. Default to STRICT in CI, but maybe we want a flag.
    # For now, assume STRICT by default unless --dev is passed?
    # Or rely on AGENTS/Tasks saying "STRICT in CI".
    # We'll default to STRICT.

    strict = True
    if len(sys.argv) > 1 and "--dev" in sys.argv:
        strict = False

    _sync_from_registry(strict=strict)
    return 0


if __name__ == "__main__":
    main()
