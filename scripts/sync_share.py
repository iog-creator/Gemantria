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

    from agentpm.db.loader import get_control_engine

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
