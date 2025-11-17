#!/usr/bin/env python

"""

Ingest Cursor rule metadata into the control-plane DB.

Purpose
-------

Populate the following tables from existing governance sources:

- control.rule_definition

- control.rule_source

Sources of truth:

- .cursor/rules/*.mdc

- RULES_INDEX.md

- AGENTS.md (for cross-checks / additional metadata)

Notes
-----

- This script must use centralized DSN / engine loaders (no direct os.getenv).

- It should be safe in DB-off environments (emit a clear error and non-zero exit).

- Implementation is intentionally conservative; it can be extended in a follow-up PR.

"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Iterable, List, Mapping, Tuple

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from agentpm.db.loader import get_control_engine

REPO_ROOT = Path(__file__).resolve().parents[2]
CURSOR_RULES_DIR = REPO_ROOT / ".cursor" / "rules"
RULES_INDEX_PATH = REPO_ROOT / "RULES_INDEX.md"


def sha256_bytes(data: bytes) -> str:
    """Return a hex-encoded SHA-256 hash for the given bytes."""
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def iter_rule_files() -> Iterable[Path]:
    """Yield all .mdc rule files from .cursor/rules."""
    if not CURSOR_RULES_DIR.is_dir():
        return []
    return sorted(CURSOR_RULES_DIR.glob("*.mdc"))


def parse_rule_id_and_name_from_filename(path: Path) -> Tuple[str, str]:
    """
    Extract rule_id and a default name from a rule filename.
    Example: 050-ops-contract.mdc -> ("050", "ops-contract")
    """
    stem = path.stem
    parts = stem.split("-", 1)
    if len(parts) == 1:
        return parts[0], parts[0]
    return parts[0], parts[1]


def load_rule_index() -> Mapping[str, Mapping[str, str]]:
    """
    Parse RULES_INDEX.md to get rule metadata.
    """
    index: dict[str, dict[str, str]] = {}
    if not RULES_INDEX_PATH.is_file():
        return index
    for line in RULES_INDEX_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("- Rule "):
            continue
        try:
            rest = line[len("- Rule ") :]
            num, _rest_name = rest.split(":", 1)
            rule_id = num.split("-", 1)[0].strip()
            name = num.split("-", 1)[1].strip() if "-" in num else rule_id
            index[rule_id] = {"name": name, "raw": line}
        except Exception:
            continue
    return index


def ingest_rules(dry_run: bool = False) -> int:
    """
    Ingest rule definitions and sources into the control schema.
    """
    rule_index = load_rule_index()
    rule_files = list(iter_rule_files())
    if not rule_files:
        print("ERROR: No rule files found in .cursor/rules", file=sys.stderr)
        return 1

    if dry_run:
        print("Dry-run mode: will NOT write to the database.", file=sys.stderr)
        for path in rule_files:
            contents = path.read_bytes()
            content_hash = sha256_bytes(contents)
            rule_id, default_name = parse_rule_id_and_name_from_filename(path)
            from_index = rule_index.get(rule_id, {})
            name = from_index.get("name", default_name)
            status = "active"
            severity = "HINT"
            docs_path = str(path.relative_to(REPO_ROOT))
            print(
                f"[DRY-RUN] Would upsert rule {rule_id} "
                f"(name={name}, status={status}, severity={severity}, path={docs_path})",
                file=sys.stderr,
            )
        return 0

    try:
        engine = get_control_engine()
    except Exception as exc:
        print(f"ERROR: Unable to get control-plane engine: {exc}", file=sys.stderr)
        return 1

    with engine.begin() as conn:
        for path in rule_files:
            contents = path.read_bytes()
            content_hash = sha256_bytes(contents)
            rule_id, default_name = parse_rule_id_and_name_from_filename(path)
            from_index = rule_index.get(rule_id, {})
            name = from_index.get("name", default_name)
            status = "active"
            severity = "HINT"
            docs_path = str(path.relative_to(REPO_ROOT))
            conn.execute(
                text("""
                INSERT INTO control.rule_definition (rule_id, name, status, description, severity, docs_path)
                VALUES (:rule_id, :name, :status, NULL, :severity, :docs_path)
                ON CONFLICT (rule_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    status = EXCLUDED.status,
                    severity = EXCLUDED.severity,
                    docs_path = EXCLUDED.docs_path,
                    updated_at = NOW()
                """),
                {
                    "rule_id": rule_id,
                    "name": name,
                    "status": status,
                    "severity": severity,
                    "docs_path": docs_path,
                },
            )
            conn.execute(
                text("""
                INSERT INTO control.rule_source (rule_id, source_type, path, content_hash)
                VALUES (:rule_id, :source_type, :path, :content_hash)
                """),
                {
                    "rule_id": rule_id,
                    "source_type": "cursor_rules",
                    "path": docs_path,
                    "content_hash": content_hash,
                },
            )
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ingest Cursor rule metadata into the control-plane DB.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform discovery and logging only; do not write to the database.",
    )
    args = parser.parse_args(argv)
    return ingest_rules(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
