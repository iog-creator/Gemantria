#!/usr/bin/env python3
"""
ingest_share_docs.py

Ingests documentation from share/ into control.doc_registry.
Ensures that files restored or created in share/ are tracked in DMS.

Scope:
- share/PHASE*.md files
- Logic:
  - If exists in registry: match/update path
  - If missing: INSERT
"""

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
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
except ImportError:
    print("DB libs not available", file=sys.stderr)
    sys.exit(1)

SHARE_ROOT = ROOT / "share"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ingest_share_docs(dry_run: bool = False):
    if not SHARE_ROOT.exists():
        print(f"Share root {SHARE_ROOT} does not exist.")
        return

    engine = get_control_engine()

    # Candidates: PHASE*.md
    candidates = list(SHARE_ROOT.glob("PHASE*.md"))

    count_new = 0
    count_updated = 0

    with engine.begin() as conn:
        for p in candidates:
            rel_path = p.relative_to(ROOT)  # Relative to repo root for share_path usually?
            # Or should share_path be relative to share/ or repo?
            # Existing specific: share/PHASE...
            share_rel = str(rel_path)
            # logical_name derivation: PHASE::{filename}
            logical_name = f"PHASE::{p.name}"

            # Check existence
            row = conn.execute(
                text("SELECT doc_id, repo_path FROM control.doc_registry WHERE logical_name = :n"), {"n": logical_name}
            ).fetchone()

            if row:
                # Update?
                # Ensure share_path is set
                if not dry_run:
                    conn.execute(
                        text("""
                        UPDATE control.doc_registry 
                        SET share_path = :sp, enabled = TRUE, updated_at = NOW()
                        WHERE doc_id = :id
                    """),
                        {"sp": share_rel, "id": row.doc_id},
                    )
                    count_updated += 1
                else:
                    print(f"[DRY] Would update {logical_name}")
            else:
                # Insert
                # Guess repo_path? If it's pure share restoration, maybe repo_path is same or null?
                # Rule: share/ files are generated or restored. If restored from reconstruction, they might not be in docs/SSOT
                # We can set repo_path = share_path for these "share-native" or "restored" docs if they don't exist elsewhere.
                # Or set repo_path to NULL?
                # ingest_docs_to_db uses repo_path as primary.
                # Let's set repo_path = share_rel as fallback.

                tags = ["phase:restored", "source:share"]

                if not dry_run:
                    conn.execute(
                        text("""
                        INSERT INTO control.doc_registry (logical_name, role, repo_path, share_path, enabled, is_ssot)
                        VALUES (:ln, 'phase_doc', :rp, :sp, TRUE, FALSE)
                    """),
                        {"ln": logical_name, "rp": share_rel, "sp": share_rel},
                    )
                    count_new += 1
                    print(f"Ingested {logical_name}")
                else:
                    print(f"[DRY] Would ingest {logical_name}")

    print(f"Ingestion complete. New: {count_new}, Updated: {count_updated}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ingest_share_docs(args.dry_run)


if __name__ == "__main__":
    main()
