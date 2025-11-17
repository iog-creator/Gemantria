# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
sync_share.py — standard share sync entrypoint.

Phase-8B: Now supports doc registry-driven sync with manifest fallback.

- First attempts to sync from control.doc_registry (when DB is available).
- Falls back to update_share.py (manifest-based) if registry is unavailable or empty.
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

    from agentpm.db.loader import get_control_engine

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


REPO_ROOT = ROOT
SHARE_ROOT = REPO_ROOT / "share"


def _sync_from_registry() -> bool:
    """
    Attempt to sync share/ from the control.doc_registry.

    Returns True if registry-based sync was performed, False if the caller
    should fall back to manifest-based behavior.
    """
    if not DB_AVAILABLE:
        return False

    try:
        engine = get_control_engine()
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[sync_share] NOTE: DB not available for registry sync: {exc}", file=sys.stderr)
        return False

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
                    "[sync_share] Registry has no share_path-enabled docs; falling back to manifest.",
                    file=sys.stderr,
                )
                return False

            SHARE_ROOT.mkdir(parents=True, exist_ok=True)

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

                share_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(repo_path, share_path)
                print(f"[sync_share] registry copy: {logical_name}: {repo_path} -> {share_path}")

        return True
    except Exception as exc:  # pragma: no cover - defensive
        print(
            f"[sync_share] NOTE: Registry sync failed: {exc}; falling back to manifest.",
            file=sys.stderr,
        )
        return False


def main(argv: List[str] | None = None) -> int:
    """
    Main entrypoint: try registry sync first, fall back to manifest-based sync.
    """
    # First try to sync from the doc registry. If that fails or is empty, fall
    # back to manifest-based behavior so existing pipelines keep working.
    used_registry = _sync_from_registry()
    if not used_registry:
        # Fall back to existing update_share.py behavior
        from scripts.update_share import main as update_main  # noqa: PLC0415

        return update_main()  # update_share.main() doesn't take argv
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
