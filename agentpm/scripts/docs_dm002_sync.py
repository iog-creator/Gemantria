"""
DM-002 sync: write canonical/archive_candidate decisions into control.kb_document.

- Reads DOC_DM002_CANONICAL_PREVIEW.md.
- For each canonical file:
    is_canonical = TRUE, status = 'canonical'
- For each archive candidate:
    is_canonical = FALSE, status = 'archive_candidate'

Notes:
- No file moves or deletions.
- Existing rows that do not appear in the preview are left unchanged.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import psycopg

from scripts.config.env import get_rw_dsn

PREVIEW_PATH = REPO_ROOT / "docs" / "analysis" / "DOC_DM002_CANONICAL_PREVIEW.md"


@dataclass
class GroupDecision:
    canonical: str
    archive_candidates: List[str]


def parse_preview(path: Path) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Parse DOC_DM002_CANONICAL_PREVIEW.md.

    Returns:
      canonical_map: path -> 'canonical'
      archive_map: path -> 'archive_candidate'

    If a path appears more than once, 'canonical' wins over 'archive_candidate'.
    """
    if not path.exists():
        raise SystemExit(f"preview file not found: {path}")

    canonical_map: Dict[str, str] = {}
    archive_map: Dict[str, str] = {}

    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            # Group header
            if line.startswith("## "):
                continue

            # Canonical line: **Canonical:** `path`
            if line.startswith("**Canonical:**"):
                # Extract between backticks
                start = line.find("`")
                end = line.rfind("`")
                if start != -1 and end != -1 and end > start:
                    p = line[start + 1 : end].strip()
                    if p:
                        canonical_map[p] = "canonical"
                        # canonical wins over prior archive assignment if any
                        archive_map.pop(p, None)
                continue

            # Archive candidate bullet: - `path`
            if line.startswith("- "):
                # Extract between backticks if present
                start = line.find("`")
                end = line.rfind("`")
                if start != -1 and end != -1 and end > start:
                    p = line[start + 1 : end].strip()
                else:
                    p = line[2:].strip()
                if p:
                    # Only record as archive_candidate if not canonical
                    if p not in canonical_map and p not in archive_map:
                        archive_map[p] = "archive_candidate"

    return canonical_map, archive_map


def sync_db(canonical_map: Dict[str, str], archive_map: Dict[str, str]) -> Tuple[int, int, int]:
    """
    Apply decisions to control.kb_document.

    Returns:
      updated_canonical_count
      updated_archive_count
      missing_count (paths not found in DB)
    """
    dsn = get_rw_dsn()
    updated_canonical = 0
    updated_archive = 0
    missing = 0

    with psycopg.connect(dsn) as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            # Canonical updates
            for path, _ in canonical_map.items():
                cur.execute(
                    """
                    UPDATE control.kb_document
                    SET is_canonical = TRUE, status = 'canonical'
                    WHERE path = %s
                    """,
                    (path,),
                )
                if cur.rowcount == 0:
                    missing += 1
                else:
                    updated_canonical += cur.rowcount

            # Archive candidate updates
            for path, _ in archive_map.items():
                cur.execute(
                    """
                    UPDATE control.kb_document
                    SET is_canonical = FALSE, status = 'archive_candidate'
                    WHERE path = %s
                    """,
                    (path,),
                )
                if cur.rowcount == 0:
                    missing += 1
                else:
                    updated_archive += cur.rowcount

        conn.commit()

    return updated_canonical, updated_archive, missing


def main() -> None:
    if not PREVIEW_PATH.exists():
        raise SystemExit(f"preview file not found: {PREVIEW_PATH}")

    canonical_map, archive_map = parse_preview(PREVIEW_PATH)
    print(
        f"Parsed preview: {len(canonical_map)} canonical, {len(archive_map)} archive_candidate paths"
    )

    updated_canonical, updated_archive, missing = sync_db(canonical_map, archive_map)

    print("DM-002 sync complete:")
    print(f"  Updated canonical rows       : {updated_canonical}")
    print(f"  Updated archive_candidate rows: {updated_archive}")
    print(f"  Missing paths (not in DB)    : {missing}")


if __name__ == "__main__":
    main()
