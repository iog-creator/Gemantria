"""
Phase 27.J: DMS-driven archive cleanup.

Policy:
- Archive all docs with importance='low' AND enabled=true AND repo_path LIKE '%.md'
- Move them into archive/docs_legacy/{basename}
- Set enabled=false and update repo_path in control.doc_registry
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import os
import shutil

import psycopg

from scripts.config.env import get_rw_dsn

PLAN_PATH = Path("docs/analysis/DOC_HYGIENE_PHASE27J_MOVES.json")


def fetch_candidates() -> List[Dict[str, Any]]:
    dsn = get_rw_dsn()
    rows: List[Dict[str, Any]] = []
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT doc_id, repo_path, share_path, importance, enabled
            FROM control.doc_registry
            WHERE importance = 'low'
              AND enabled = true
              AND repo_path LIKE '%.md'
              AND (repo_path IS NOT NULL)
            ORDER BY repo_path
            """
        )
        cols = [c.name for c in cur.description]
        for rec in cur.fetchall():
            rows.append(dict(zip(cols, rec)))
    return rows


def ensure_archive_dir() -> Path:
    path = Path("archive/docs_legacy")
    path.mkdir(parents=True, exist_ok=True)
    return path


def main(apply: bool = False) -> None:
    candidates = fetch_candidates()
    print(f"[INFO] Found {len(candidates)} low-importance enabled markdown docs.")

    archive_dir = ensure_archive_dir()

    moves = []
    for row in candidates:
        repo_path = row["repo_path"]
        basename = os.path.basename(repo_path)
        new_repo_path = f"archive/docs_legacy/{basename}"
        moves.append(
            {
                "doc_id": str(row["doc_id"]),
                "old_repo_path": repo_path,
                "new_repo_path": new_repo_path,
            }
        )

    PLAN_PATH.write_text(json.dumps({"moves": moves}, indent=2), encoding="utf-8")
    print(f"[INFO] Wrote move plan to {PLAN_PATH}")

    if not apply:
        print("[DRY-RUN] Not applying moves. Inspect JSON plan and rerun with --apply.")
        return

    dsn = get_rw_dsn()
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        for m in moves:
            old = Path(m["old_repo_path"])
            new = Path(m["new_repo_path"])

            if not old.exists():
                print(f"[WARN] File missing on disk: {old}")
                continue

            new.parent.mkdir(parents=True, exist_ok=True)
            print(f"[APPLY] Moving {old} -> {new}")
            shutil.move(str(old), str(new))

            cur.execute(
                """
                UPDATE control.doc_registry
                SET repo_path = %s,
                    enabled = false
                WHERE doc_id = %s
                """,
                (m["new_repo_path"], m["doc_id"]),
            )

        conn.commit()
        print(f"[APPLIED] Updated {len(moves)} row(s) in control.doc_registry")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply moves.")
    args = parser.parse_args()
    main(apply=args.apply)
