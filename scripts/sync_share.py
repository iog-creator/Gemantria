# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
sync_share.py — standard share sync entrypoint.

DMS-only sync: syncs share/ from control.doc_registry only.

- Requires DMS doc registry to be populated with share_path-enabled docs.
- Fail-closed: exits with error if registry is unavailable or has no share_path-enabled docs.
- No manifest fallback: registry is the single source of truth for share/ sync.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import List

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from sqlalchemy import text

    from pmagent.db.loader import get_control_engine

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


REPO_ROOT = ROOT
SHARE_ROOT = REPO_ROOT / "share"


def _sync_from_registry() -> bool:
    """
    Attempt to sync share/ from the control.doc_registry.

    Returns True if registry-based sync was performed.
    Raises SystemExit(1) if registry is unavailable or has no share_path-enabled docs.

    This function is fail-closed: it never falls back to manifest-based behavior.

    **Contract (DMS SSOT Enforcement):**

    1. **DMS as Single Source of Truth**
       - Query `control.doc_registry` for all rows where:
         - `share_path IS NOT NULL`
         - `enabled = TRUE`
       - Build set of expected share paths from registry (no filesystem discovery).

    2. **Populate share/ from DMS**
       - For each enabled doc with a `share_path`:
         - Copy source file from `repo_path` to `share_path`.
         - Create parent directories if needed.
         - Log each copy operation.

    3. **Delete Stale Files (Enforce Registry-Only)**
       - For any `.md` file in `share/` root NOT in expected set:
         - Delete it immediately (stale/obsolete file).
       - This prevents drift: files not in registry are removed.

    4. **Delete Stale Subdirectories (Enforce Flat Structure)**
       - For any subdirectory in `share/`:
         - Recursively remove it (enforce flat structure per SHARE_FOLDER_STRUCTURE.md).
       - Prevents legacy subdirs (e.g., `atlas/`, `exports/`, `runtime/`) from persisting.

    5. **Fail-Closed on DB Unavailability**
       - If Postgres/control schema unreachable:
         - Exit non-zero (SystemExit(1)).
         - Print error to stderr.
         - Do NOT proceed with filesystem-only sync.
       - Principle: If SSOT is unreachable, we do not trust the filesystem view.

    **Why This Matters:**
    - Prevents "zombie files" (41 stale files when registry says 17).
    - Prevents subdirectory drift (old `atlas/`, `exports/` persisting).
    - Ensures `make housekeeping` can self-heal share/ folder.
    - Aligns share/ with DMS registry on every sync (no manual cleanup needed).
    """
    if not DB_AVAILABLE:
        print(
            "[sync_share] ERROR: Database not available for registry sync. DMS doc registry is required.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None

    try:
        engine = get_control_engine()
    except Exception as exc:  # pragma: no cover - defensive
        print(
            f"[sync_share] ERROR: Unable to get control-plane engine: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT logical_name, repo_path, share_path, enabled
                    FROM control.doc_registry
                    WHERE share_path IS NOT NULL
                      AND enabled = TRUE
                    ORDER BY logical_name
                    """
                )
            ).fetchall()

            if not rows:
                print(
                    "[sync_share] ERROR: DMS doc registry has no share_path-enabled docs. "
                    "Manifest fallback is forbidden. Run: make governance.ingest.docs",
                    file=sys.stderr,
                )
                raise SystemExit(1)

            SHARE_ROOT.mkdir(parents=True, exist_ok=True)

            # Step 1: Collect all expected share paths from registry (SSOT)
            expected_share_paths = set()
            for logical_name, repo_rel, share_rel, enabled in rows:
                repo_path = REPO_ROOT / repo_rel
                # Handle both relative and absolute share paths
                if str(share_rel).startswith("share/"):
                    share_path = REPO_ROOT / share_rel
                else:
                    share_path = SHARE_ROOT / share_rel

                if not repo_path.is_file():
                    print(
                        f"[sync_share] WARN: registry repo_path missing for {logical_name}: {repo_path}",
                        file=sys.stderr,
                    )
                    continue

                expected_share_paths.add(share_path)
                share_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(repo_path, share_path)
                print(f"[sync_share] registry copy: {logical_name}: {repo_path} -> {share_path}")

            # Step 2: Clean up files in share/ that are NOT in the registry
            # Only clean up .md files in the root of share/ (enforce registry-only)
            if SHARE_ROOT.is_dir():
                for share_file in SHARE_ROOT.iterdir():
                    if share_file.is_file() and share_file.suffix == ".md":
                        if share_file not in expected_share_paths:
                            print(
                                f"[sync_share] cleanup: removing stale file not in registry: {share_file.name}",
                                file=sys.stderr,
                            )
                            share_file.unlink()
                    elif share_file.is_dir():
                        # Step 3: Remove all subdirectories to enforce flat structure
                        # (per SHARE_FOLDER_STRUCTURE.md: "Flat directory structure - no subdirectories")
                        print(
                            f"[sync_share] cleanup: removing subdirectory: {share_file.name}",
                            file=sys.stderr,
                        )
                        shutil.rmtree(share_file)

        return True
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        print(
            f"[sync_share] ERROR: Registry sync failed: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


def main(argv: List[str] | None = None) -> int:
    """
    Main entrypoint: sync share/ from DMS doc registry only.

    This function is fail-closed: it requires the registry to be populated with
    share_path-enabled docs. No manifest fallback is performed.
    """
    # Sync from the doc registry. This will raise SystemExit(1) if:
    # - Database is unavailable
    # - Registry has no share_path-enabled docs
    # - Any other error occurs during sync
    _sync_from_registry()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
