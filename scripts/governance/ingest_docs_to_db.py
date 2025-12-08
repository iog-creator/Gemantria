#!/usr/bin/env python

"""
Ingest documentation metadata into the pmagent control-plane DMS.

Purpose
-------
Populate the following tables from canonical docs in the repo:

- control.doc_registry (pmagent control-plane DMS)
- control.doc_version

The goals are:

- Populate the pmagent control-plane DMS as the structured SSOT for doc metadata (paths, roles, hashes).
- Track versions by content hash and optional git commit.
- Clearly distinguish SSOT docs (repo) from derived views (e.g. share/).
- Populate governance metadata (importance, tags, owner_component).

This script does NOT:

- Modify share/ contents.
- Store full file contents in the database.

Note: pmagent is the governance engine; Gemantria is the governed project.
The pmagent control-plane DMS records and enforces the semantics defined by AGENTS.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from pmagent.db.loader import get_control_engine


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class DocTarget:
    logical_name: str
    role: str
    repo_path: Path
    is_ssot: bool
    importance: str = "unknown"
    tags: List[str] = field(default_factory=list)
    owner_component: str | None = None


CANONICAL_DOCS: List[DocTarget] = [
    DocTarget(
        logical_name="AGENTS_ROOT",
        role="ssot",
        repo_path=REPO_ROOT / "AGENTS.md",
        is_ssot=True,
        importance="critical",
        tags=["ssot", "agent_framework", "agent_framework_index"],
    ),
    DocTarget(
        logical_name="MASTER_PLAN",
        role="ssot",
        repo_path=REPO_ROOT / "MASTER_PLAN.md",
        is_ssot=True,
        importance="critical",
        tags=["ssot"],
    ),
    DocTarget(
        logical_name="RULES_INDEX",
        role="ssot",
        repo_path=REPO_ROOT / "RULES_INDEX.md",
        is_ssot=True,
        importance="critical",
        tags=["ssot"],
    ),
]


def derive_owner_component(repo_path: Path) -> str:
    """
    Heuristic: owner_component is the top-level dir, or 'root' for root files.
    """
    try:
        rel = repo_path.relative_to(REPO_ROOT)
        path_str = str(rel)
    except ValueError:
        # Fallback if not relative to root (shouldn't happen given logic)
        return "unknown"

    if "/" not in path_str:
        return "root"
    return path_str.split("/", 1)[0]


def iter_agents_docs() -> Iterable[DocTarget]:
    """
    Discover all AGENTS*.md docs in the repo (excluding share/ and virtualenvs).

    Rules:

    - Root AGENTS.md is treated as the global agent framework index.

    - Any other *AGENTS*.md (e.g. scripts_AGENTS.md, pmagent/AGENTS.md) is treated

      as module- or directory-level agent framework documentation.
    """
    for path in REPO_ROOT.rglob("*AGENTS*.md"):
        # Skip derived or non-repo locations.
        try:
            rel = path.relative_to(REPO_ROOT)
        except ValueError:
            continue

        parts = rel.parts
        # Skip share/ and typical venv paths.
        if parts[0] in {"share", ".venv", "venv", ".git"}:
            continue

        logical_name: str
        role = "agent_framework"
        importance = "high"
        tags = ["ssot", "agent_framework"]

        if rel == Path("AGENTS.md"):
            logical_name = "AGENTS_ROOT"
            role = "agent_framework_index"
            importance = "critical"
            tags = ["ssot", "agent_framework", "agent_framework_index"]
        else:
            # Derive a stable logical name from the relative path.
            logical_name = f"AGENTS::{rel.as_posix()}"

        yield DocTarget(
            logical_name=logical_name,
            role=role,
            repo_path=path,
            is_ssot=True,
            importance=importance,
            tags=tags,
        )


def iter_additional_docs() -> Iterable[DocTarget]:
    """
    Discover additional docs under docs/SSOT and docs/runbooks.

    - docs/SSOT/** -> role="ssot", importance="critical"
    - docs/runbooks/** -> role="runbook", importance="high"
    """
    ssot_root = REPO_ROOT / "docs" / "SSOT"
    if ssot_root.is_dir():
        for path in ssot_root.rglob("*.md"):
            yield DocTarget(
                logical_name=f"SSOT::{path.relative_to(REPO_ROOT)}",
                role="ssot",
                repo_path=path,
                is_ssot=True,
                importance="critical",
                tags=["ssot"],
            )

    runbook_root = REPO_ROOT / "docs" / "runbooks"
    if runbook_root.is_dir():
        for path in runbook_root.rglob("*.md"):
            yield DocTarget(
                logical_name=f"RUNBOOK::{path.relative_to(REPO_ROOT)}",
                role="runbook",
                repo_path=path,
                is_ssot=True,
                importance="high",
                tags=["runbook"],
            )


def iter_pdf_docs() -> Iterable[DocTarget]:
    """
    Discover PDF documentation files in docs/ directory.

    Phase 1: PDF discovery only (no parsing yet).
    Assigns roles based on filename patterns:
    - "audit" -> role="audit"
    - "architecture" or "design" -> role="architecture"
    - "reference" -> role="reference"
    - default -> role="documentation"
    """
    docs_root = REPO_ROOT / "docs"
    if not docs_root.is_dir():
        return

    for path in docs_root.glob("*.pdf"):
        # Skip if not a file or outside docs root
        if not path.is_file():
            continue

        # Determine role based on filename patterns
        filename_lower = path.name.lower()
        if "audit" in filename_lower:
            role = "audit"
        elif "architecture" in filename_lower or "design" in filename_lower:
            role = "architecture"
        elif "reference" in filename_lower or "master" in filename_lower:
            role = "reference"
        else:
            role = "documentation"

        # Create logical name from relative path
        logical_name = f"PDF::{path.relative_to(REPO_ROOT)}"

        yield DocTarget(
            logical_name=logical_name,
            role=role,
            repo_path=path,
            is_ssot=True,
            importance="medium",
            tags=["documentation", "pdf"],
        )


def sha256_bytes(data: bytes) -> str:
    """Return hex-encoded SHA-256 hash for the given bytes."""
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def get_git_commit() -> str | None:
    """Return the current git HEAD commit SHA, or None on failure."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8").strip()
    except Exception:
        return None


def load_share_manifest_mapping() -> dict[str, str]:
    """
    Load SHARE_MANIFEST.json and create a mapping from repo_path (src) to share_path (dst).

    Returns a dict mapping repo-relative paths to share-relative paths.
    """
    manifest_path = REPO_ROOT / "docs" / "SSOT" / "SHARE_MANIFEST.json"
    if not manifest_path.exists():
        return {}

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        items = manifest.get("items", [])
        # Map src (repo path) -> dst (share path)
        return {item["src"]: item["dst"] for item in items if "src" in item and "dst" in item}
    except Exception:
        return {}


def ingest_docs(dry_run: bool = False) -> int:
    """
    Ingest documentation metadata into pmagent control-plane DMS (control.doc_registry / control.doc_version).

    Steps:
    1. Build the doc target list (canonical + discovered).
    2. Compute content hashes and sizes for existing files.
    3. Upsert registry rows and insert version rows in the pmagent control-plane DMS.
    """
    targets: List[DocTarget] = list(CANONICAL_DOCS)
    # Phase-8: treat all AGENTS*.md docs as SSOT for the agent framework.
    targets.extend(iter_agents_docs())
    targets.extend(iter_additional_docs())
    # Layer 3 Phase 1: PDF discovery (no parsing yet)
    targets.extend(iter_pdf_docs())

    existing_targets: List[DocTarget] = []
    for t in targets:
        if t.repo_path.is_file():
            # Apply owner_component heuristic if not explicitly set
            if t.owner_component is None:
                t.owner_component = derive_owner_component(t.repo_path)
            existing_targets.append(t)
        else:
            print(
                f"[WARN] Missing doc for logical_name={t.logical_name} path={t.repo_path}",
                file=sys.stderr,
            )

    if not existing_targets:
        print("ERROR: No documentation files found for ingestion.", file=sys.stderr)
        return 1

    git_commit = get_git_commit()
    if dry_run:
        print("Dry-run mode: will NOT write to the database.", file=sys.stderr)
        for target in existing_targets:
            contents = target.repo_path.read_bytes()
            content_hash = sha256_bytes(contents)
            size_bytes = target.repo_path.stat().st_size
            repo_rel = str(target.repo_path.relative_to(REPO_ROOT))
            print(
                f"[DRY-RUN] Would upsert doc logical_name={target.logical_name} "
                f"role={target.role} path={repo_rel} hash={content_hash} "
                f"importance={target.importance} tags={target.tags} "
                f"owner_component={target.owner_component}",
                file=sys.stderr,
            )
        return 0

    try:
        engine = get_control_engine()
    except Exception as exc:  # pragma: no cover - defensive
        print(f"ERROR: Unable to get control-plane engine: {exc}", file=sys.stderr)
        return 1

    # Load share manifest mapping for gap-filling share_path
    manifest_mapping = load_share_manifest_mapping()

    with engine.begin() as conn:
        for target in existing_targets:
            contents = target.repo_path.read_bytes()
            content_hash = sha256_bytes(contents)
            size_bytes = target.repo_path.stat().st_size
            repo_rel = str(target.repo_path.relative_to(REPO_ROOT))

            # Determine share_path: use manifest mapping if available, otherwise NULL
            # The ON CONFLICT clause will preserve existing non-NULL share_path values
            share_path_from_manifest = manifest_mapping.get(repo_rel)

            # Determine if this is an AGENTS doc
            is_agents = target.logical_name.startswith("AGENTS") or repo_rel.endswith("AGENTS.md")

            # For AGENTS docs, ensure minimum importance and required tags
            if is_agents:
                # Root AGENTS.md must be critical
                if repo_rel == "AGENTS.md":
                    target.importance = "critical"
                    # Ensure required tags are present
                    required_tags = {"ssot", "agent_framework", "agent_framework_index"}
                    target.tags = list(set(target.tags) | required_tags)
                else:
                    # Other AGENTS.md must be at least high
                    if target.importance not in ("critical", "high"):
                        target.importance = "high"
                    # Ensure required tags are present
                    required_tags = {"ssot", "agent_framework"}
                    target.tags = list(set(target.tags) | required_tags)

            # Check existing row to apply hybrid update logic
            existing_row = conn.execute(
                text(
                    """
                    SELECT importance, tags
                    FROM control.doc_registry
                    WHERE logical_name = :logical_name
                    """
                ),
                {"logical_name": target.logical_name},
            ).fetchone()

            # Compute final importance and tags based on hybrid logic
            final_importance = target.importance
            final_tags = target.tags

            if existing_row:
                existing_importance, existing_tags = existing_row
                existing_tags = existing_tags or []

                if is_agents:
                    # AGENTS: upgrade upward, never downgrade
                    importance_order = {"unknown": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
                    existing_level = importance_order.get(existing_importance, 0)
                    new_level = importance_order.get(target.importance, 0)
                    if new_level > existing_level:
                        final_importance = target.importance
                    else:
                        final_importance = existing_importance

                    # Merge tags: union of existing and new
                    final_tags = list(set(existing_tags) | set(target.tags))
                else:
                    # Non-AGENTS: only update if unknown/empty (preserves manual overrides)
                    if existing_importance == "unknown":
                        final_importance = target.importance
                    else:
                        final_importance = existing_importance

                    if not existing_tags:
                        final_tags = target.tags
                    else:
                        final_tags = existing_tags

            # Upsert registry row with computed final values
            row = conn.execute(
                text(
                    """
                    INSERT INTO control.doc_registry (
                        logical_name, role, repo_path, share_path, is_ssot, enabled,
                        importance, tags, owner_component
                    )
                    VALUES (
                        :logical_name, :role, :repo_path, :share_path, :is_ssot, TRUE,
                        :importance, :tags, :owner_component
                    )
                    ON CONFLICT (logical_name) DO UPDATE SET
                        role = EXCLUDED.role,
                        repo_path = EXCLUDED.repo_path,
                        share_path = COALESCE(control.doc_registry.share_path, EXCLUDED.share_path),
                        is_ssot = EXCLUDED.is_ssot,
                        enabled = EXCLUDED.enabled,
                        owner_component = EXCLUDED.owner_component,
                        importance = EXCLUDED.importance,
                        tags = EXCLUDED.tags,
                        updated_at = NOW()
                    RETURNING doc_id
                    """
                ),
                {
                    "logical_name": target.logical_name,
                    "role": target.role,
                    "repo_path": repo_rel,
                    "share_path": share_path_from_manifest,
                    "is_ssot": target.is_ssot,
                    "importance": final_importance,
                    "tags": final_tags,
                    "owner_component": target.owner_component,
                },
            ).one()
            doc_id = row[0]

            # Insert version row.
            conn.execute(
                text(
                    """
                    INSERT INTO control.doc_version (doc_id, git_commit, content_hash, size_bytes)
                    VALUES (:doc_id, :git_commit, :content_hash, :size_bytes)
                    """
                ),
                {
                    "doc_id": doc_id,
                    "git_commit": git_commit,
                    "content_hash": content_hash,
                    "size_bytes": size_bytes,
                },
            )

    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ingest documentation metadata into the pmagent control-plane DMS.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform discovery and logging only; do not write to the database.",
    )
    args = parser.parse_args(argv)
    return ingest_docs(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
