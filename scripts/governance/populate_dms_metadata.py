"""
Phase 27.J: Populate control.doc_registry.importance/tags/owner_component
from DOC_HYGIENE_PHASE27I_CLASSIFICATION.json.

Mappings:
- core-ssot     -> importance='critical', tags += ['ssot']
- transitional  -> importance='high',    tags += ['transitional']
- helpful       -> importance='medium',  tags += ['documentation']
- unknown       -> importance='low',     tags += ['review_candidate']
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

import psycopg

from scripts.config.env import get_rw_dsn

CLASSIFICATION_PATH = Path("docs/analysis/DOC_HYGIENE_PHASE27I_CLASSIFICATION.json")


CLASS_IMPORTANCE = {
    "core-ssot": "critical",
    "transitional": "high",
    "helpful": "medium",
    "unknown": "low",
}


CLASS_TAGS = {
    "core-ssot": ["ssot"],
    "transitional": ["transitional"],
    "helpful": ["documentation"],
    "unknown": ["review_candidate"],
}


def derive_owner_component(repo_path: str) -> str:
    """
    Heuristic: owner_component is the top-level dir, or 'root' for root files.
    """
    if "/" not in repo_path:
        return "root"
    return repo_path.split("/", 1)[0]


def load_classification() -> List[Dict[str, Any]]:
    data = json.loads(CLASSIFICATION_PATH.read_text(encoding="utf-8"))
    return data.get("docs", [])


def main(dry_run: bool = True) -> None:
    rows = load_classification()
    dsn = get_rw_dsn()

    print(f"[INFO] Loaded {len(rows)} classified docs from {CLASSIFICATION_PATH}")
    updates: List[Tuple[Any, ...]] = []

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        for row in rows:
            repo_path = row.get("repo_path")
            classification = row.get("classification")
            if not repo_path or not classification:
                continue

            importance = CLASS_IMPORTANCE.get(classification, "unknown")
            new_tags = CLASS_TAGS.get(classification, [])

            owner_component = derive_owner_component(repo_path)

            cur.execute(
                """
                SELECT doc_id, importance, tags, owner_component
                FROM control.doc_registry
                WHERE repo_path = %s
                """,
                (repo_path,),
            )
            rec = cur.fetchone()
            if not rec:
                print(f"[WARN] No doc_registry row for repo_path={repo_path!r}")
                continue

            doc_id, current_importance, current_tags, current_owner = rec

            current_tags = current_tags or []
            merged_tags = list(dict.fromkeys(list(current_tags) + new_tags))

            updates.append(
                (doc_id, importance, merged_tags, owner_component, repo_path, classification)
            )

        print(f"[INFO] Prepared {len(updates)} updates.")

        if dry_run:
            print("[DRY-RUN] Sample updates:")
            for u in updates[:10]:
                doc_id, importance, tags, owner_component, repo_path, classification = u
                print(
                    f"- {repo_path} ({classification}) -> "
                    f"importance={importance}, tags={tags}, owner_component={owner_component}"
                )
            return

        for doc_id, importance, tags, owner_component, repo_path, classification in updates:
            cur.execute(
                """
                UPDATE control.doc_registry
                SET importance = %s,
                    tags = %s,
                    owner_component = %s
                WHERE doc_id = %s
                """,
                (importance, tags, owner_component, doc_id),
            )

        conn.commit()
        print(f"[APPLIED] Updated {len(updates)} rows.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply updates instead of dry-run.",
    )
    args = parser.parse_args()
    main(dry_run=not args.apply)
