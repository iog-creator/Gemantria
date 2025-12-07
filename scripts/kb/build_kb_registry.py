#!/usr/bin/env python3
"""
KB Registry Builder from DMS (Layer 3 Phase 4)

Builds KB registry from control.doc_registry + control.doc_fragment.meta.
Reads documents with kb_candidate=true fragments and aggregates metadata.

SSOT: share/kb_registry.json (read-only in CI per Rule-044).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Pre-flight DB check (mandatory - Rule 050 evidence-first)
preflight_script = ROOT / "scripts" / "ops" / "preflight_db_check.py"
result = subprocess.run([sys.executable, str(preflight_script), "--mode", "strict"], capture_output=True)
if result.returncode != 0:
    print(result.stderr.decode(), file=sys.stderr)
    sys.exit(result.returncode)

from pmagent.db.loader import get_control_engine
from pmagent.kb.registry import (
    KBDocument,
    KBDocumentRegistry,
    REGISTRY_PATH,
    load_registry,
    save_registry,
)
from sqlalchemy import text

# CI guard: Do not write in CI
if os.getenv("CI") == "true":
    print("ERROR: KB registry building is disabled in CI (read-only per Rule-044)", file=sys.stderr)
    sys.exit(1)


def build_kb_registry_from_dms(dry_run: bool = False) -> KBDocumentRegistry:
    """
    Build KB registry from DMS (control.doc_registry).

    Curated subset for PM usability:
    - Documents with kb_candidate=true fragments (AI-classified)
    - Manually curated high-importance docs (SSOT, runbooks, root AGENTS.md)

    Target size: ~100-200 documents (not all 994 enabled docs)

    Args:
        dry_run: If True, print summary instead of writing to file

    Returns:
        KBDocumentRegistry instance
    """
    engine = get_control_engine()

    # Query curated subset: Most important documents only
    # Phase 17.4 update: Include ALL enabled SSOT docs (not just kb_candidate)
    # Target: All SSOT + select high-value code docs
    query = text("""
        -- All enabled SSOT docs (Phase 17.4: removed kb_candidate filter)
        SELECT DISTINCT
            d.doc_id,
            d.logical_name,
            d.role,
            d.repo_path,
            d.share_path,
            d.is_ssot,
            d.enabled
        FROM control.doc_registry d
        WHERE d.enabled = true
          AND d.is_ssot = true

        UNION

        -- Runbooks (always included)
        SELECT DISTINCT
            d.doc_id,
            d.logical_name,
            d.role,
            d.repo_path,
            d.share_path,
            d.is_ssot,
            d.enabled
        FROM control.doc_registry d
        WHERE d.enabled = true
          AND d.role = 'runbook'

        UNION

        -- Root AGENTS.md files (critical for PM)
        SELECT DISTINCT
            d.doc_id,
            d.logical_name,
            d.role,
            d.repo_path,
            d.share_path,
            d.is_ssot,
            d.enabled
        FROM control.doc_registry d
        WHERE d.enabled = true
          AND (
            d.repo_path = 'AGENTS.md'
            OR d.repo_path = 'pmagent/AGENTS.md'
          )

        UNION

        -- Top core-importance kb_candidate documents (select code docs, limited to 50)
        SELECT * FROM (
            SELECT DISTINCT
                d.doc_id,
                d.logical_name,
                d.role,
                d.repo_path,
                d.share_path,
                d.is_ssot,
                d.enabled
            FROM control.doc_registry d
            JOIN control.doc_fragment f ON f.doc_id = d.doc_id
            WHERE d.enabled = true
              AND f.meta @> '{"kb_candidate": true, "importance": "core"}'::jsonb
              AND d.is_ssot = false
              AND d.role != 'runbook'
            LIMIT 50
        ) AS top_code_docs

        ORDER BY logical_name
    """)

    documents = []
    with engine.connect() as conn:
        doc_rows = conn.execute(query).fetchall()
        print(f"[DEBUG] Query returned {len(doc_rows)} documents", file=sys.stderr)

        for doc_row in doc_rows:
            doc_id, logical_name, role, repo_path, share_path, is_ssot, enabled = doc_row

            # Get fragment metadata if available (optional - docs may not be fragmented yet)
            fragment_query = text("""
                SELECT
                    f.fragment_index,
                    f.meta
                FROM control.doc_fragment f
                WHERE f.doc_id = :doc_id
                  AND f.meta @> '{"kb_candidate": true}'::jsonb
                ORDER BY f.fragment_index
            """)

            fragment_rows = conn.execute(fragment_query, {"doc_id": doc_id}).fetchall()

            # Documents without fragments are still included (they just have no fragment metadata)

            # Aggregate metadata from fragments
            subsystems = []
            importances = []
            phase_relevances = []
            doc_roles = []

            fragments_meta = []
            for frag_idx, meta_json in fragment_rows:
                if not meta_json:
                    continue

                # Extract fragment-level metadata
                subsystem = meta_json.get("subsystem")
                importance = meta_json.get("importance")
                phase_relevance = meta_json.get("phase_relevance", [])
                doc_role = meta_json.get("doc_role")

                if subsystem:
                    subsystems.append(subsystem)
                if importance:
                    importances.append(importance)
                if phase_relevance:
                    if isinstance(phase_relevance, list):
                        phase_relevances.extend(phase_relevance)
                    else:
                        phase_relevances.append(phase_relevance)
                if doc_role:
                    doc_roles.append(doc_role)

            # Don't store fragment metadata in registry (reduces file size)
            # Full metadata is available in DMS; registry is lightweight index only
            # Just count fragments for provenance

            # Determine dominant values (most common)
            dominant_subsystem = Counter(subsystems).most_common(1)[0][0] if subsystems else None
            dominant_importance = Counter(importances).most_common(1)[0][0] if importances else None
            unique_phase_relevance = sorted(set(phase_relevances)) if phase_relevances else []

            # Map doc_registry.role to KB document type
            doc_type_map = {
                "ssot": "ssot",
                "runbook": "runbook",
                "analysis": "other",
                "derived": "other",
            }
            kb_type = doc_type_map.get(role, "other")

            # Determine owning subsystem from fragment metadata or logical_name
            owning_subsystem = dominant_subsystem
            if not owning_subsystem:
                # Fallback: extract from logical_name or repo_path
                if "pmagent" in logical_name.lower() or "pmagent" in (repo_path or "").lower():
                    owning_subsystem = "pmagent"
                elif "docs" in (repo_path or "").lower():
                    owning_subsystem = "docs"
                else:
                    owning_subsystem = "root"

            # Build tags from metadata
            tags = []
            if is_ssot:
                tags.append("ssot")
            if role:
                tags.append(role)
            if unique_phase_relevance:
                tags.extend([f"phase-{p}" for p in unique_phase_relevance if p])

            # Create KB document entry
            kb_doc = KBDocument(
                id=logical_name.lower().replace(" ", "-").replace("_", "-"),
                title=logical_name,
                path=repo_path or share_path or "",
                type=kb_type,
                tags=tags,
                owning_subsystem=owning_subsystem,
                provenance={
                    "doc_id": str(doc_id),
                    "is_ssot": is_ssot,
                    "enabled": enabled,
                    "dominant_subsystem": dominant_subsystem,
                    "dominant_importance": dominant_importance,
                    "phase_relevance": unique_phase_relevance,
                    "fragment_count": len(fragments_meta),
                },
            )

            # Store fragment count only (not full fragment metadata to reduce file size)
            # Full fragment metadata available in control.doc_fragment.meta
            kb_doc.provenance["fragment_count"] = len(fragment_rows)
            kb_doc.provenance["has_classified_fragments"] = len(fragment_rows) > 0

            documents.append(kb_doc)

    # Create registry
    registry = KBDocumentRegistry(
        version="1.0",
        generated_at=datetime.now(UTC).isoformat(),
        documents=documents,
    )

    if dry_run:
        print(f"[DRY-RUN] Would create KB registry with {len(documents)} documents", file=sys.stderr)
        print("\nDocuments:", file=sys.stderr)
        for doc in documents:
            print(f"  - {doc.id}: {doc.title} ({doc.owning_subsystem}, {doc.type})", file=sys.stderr)
            if doc.provenance.get("fragment_count"):
                print(f"    Fragments: {doc.provenance['fragment_count']}", file=sys.stderr)
    else:
        # Load existing registry and merge (preserve non-DMS entries if any)
        try:
            existing = load_registry()
            # For now, replace entirely with DMS-sourced entries
            # TODO: Merge strategy (keep non-DMS entries, update DMS entries)
            registry = registry
        except FileNotFoundError:
            # No existing registry, use new one
            pass

        save_registry(registry, allow_ci_write=False)

    return registry


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Build KB registry from DMS")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without writing")
    args = parser.parse_args()

    try:
        registry = build_kb_registry_from_dms(dry_run=args.dry_run)
        if not args.dry_run:
            print(f"✅ KB registry built: {len(registry.documents)} documents", file=sys.stderr)
            print(f"   Written to: {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: Failed to build KB registry: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
