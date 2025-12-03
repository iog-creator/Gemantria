#!/usr/bin/env python3
"""
KB Registry Seeding Script (KB-Reg:M3a)

Seeds the KB document registry with core SSOT docs, runbooks, and AGENTS.md files.
Respects CI write guards (Rule-044) - only runs in local/dev environments.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pmagent.kb.registry import (
    KBDocument,
    load_registry,
    save_registry,
    validate_registry,
)

# CI guard: Do not write in CI
if os.getenv("CI") == "true":
    print("ERROR: KB registry seeding is disabled in CI (read-only per Rule-044)", file=sys.stderr)
    sys.exit(1)


def create_seed_documents(repo_root: Path) -> list[KBDocument]:
    """Create seed documents for KB registry.

    Args:
        repo_root: Repository root path

    Returns:
        List of KBDocument instances
    """
    documents = []

    # SSOT Documents
    documents.append(
        KBDocument(
            id="ssot-master-plan",
            title="Master Plan",
            path="docs/SSOT/MASTER_PLAN.md",
            type="ssot",
            tags=["governance", "planning", "ssot"],
            owning_subsystem="docs",
            provenance={"source": "seeded", "category": "core_ssot"},
        )
    )

    documents.append(
        KBDocument(
            id="ssot-pmagent-current-vs-intended",
            title="pmagent Current vs Intended State",
            path="docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md",
            type="ssot",
            tags=["governance", "pmagent", "ssot"],
            owning_subsystem="docs",
            provenance={"source": "seeded", "category": "core_ssot"},
        )
    )

    # Key ADRs (small starter set)
    documents.append(
        KBDocument(
            id="adr-065-postgres-ssot",
            title="Postgres SSOT",
            path="ADR-065-postgres-ssot.md",
            type="adr",
            tags=["architecture", "database", "ssot"],
            owning_subsystem="root",
            provenance={"source": "seeded", "category": "key_adr"},
        )
    )

    documents.append(
        KBDocument(
            id="adr-066-lm-studio-control-plane",
            title="LM Studio Control Plane Integration",
            path="ADR-066-lm-studio-control-plane-integration.md",
            type="adr",
            tags=["architecture", "lm", "control-plane"],
            owning_subsystem="root",
            provenance={"source": "seeded", "category": "key_adr"},
        )
    )

    documents.append(
        KBDocument(
            id="adr-032-bibledb-ssot",
            title="Bible DB as SSOT Roadmap",
            path="ADR-032-bibledb-as-SSOT-roadmap.md",
            type="adr",
            tags=["architecture", "database", "roadmap"],
            owning_subsystem="root",
            provenance={"source": "seeded", "category": "key_adr"},
        )
    )

    # Runbooks
    documents.append(
        KBDocument(
            id="runbook-pm-snapshot",
            title="PM Snapshot Current",
            path="docs/runbooks/PM_SNAPSHOT_CURRENT.md",
            type="runbook",
            tags=["ops", "pm", "snapshot"],
            owning_subsystem="docs",
            provenance={"source": "seeded", "category": "runbook"},
        )
    )

    # AGENTS.md files
    documents.append(
        KBDocument(
            id="agents-md-root",
            title="Root AGENTS.md",
            path="AGENTS.md",
            type="agents_md",
            tags=["governance", "root"],
            owning_subsystem="root",
            provenance={"source": "seeded", "category": "agents_md"},
        )
    )

    documents.append(
        KBDocument(
            id="agents-md-pmagent",
            title="pmagent Package AGENTS.md",
            path="pmagent/AGENTS.md",
            type="agents_md",
            tags=["governance", "pmagent"],
            owning_subsystem="pmagent",
            provenance={"source": "seeded", "category": "agents_md"},
        )
    )

    documents.append(
        KBDocument(
            id="agents-md-webui-graph",
            title="webui/graph AGENTS.md",
            path="webui/graph/AGENTS.md",
            type="agents_md",
            tags=["governance", "webui"],
            owning_subsystem="webui",
            provenance={"source": "seeded", "category": "agents_md"},
        )
    )

    return documents


def main() -> None:
    """Main seeding function."""
    repo_root = ROOT

    # Load existing registry (or create empty)
    registry = load_registry()

    # Create seed documents
    seed_docs = create_seed_documents(repo_root)

    # Add documents to registry (skip if already exists)
    added_count = 0
    skipped_count = 0
    for doc in seed_docs:
        if registry.get_by_id(doc.id):
            skipped_count += 1
            print(f"SKIP: Document already exists: {doc.id}", file=sys.stderr)
        else:
            if registry.add_document(doc):
                added_count += 1
                print(f"ADDED: {doc.id} -> {doc.path}", file=sys.stderr)
            else:
                skipped_count += 1
                print(f"SKIP: Failed to add (duplicate?): {doc.id}", file=sys.stderr)

    # Validate registry
    validation = validate_registry(registry, repo_root=repo_root)

    # Save registry
    try:
        save_registry(registry, allow_ci_write=False)
        print(f"\nSUCCESS: Registry seeded with {added_count} new document(s)", file=sys.stderr)
        if skipped_count > 0:
            print(f"SKIPPED: {skipped_count} document(s) already existed", file=sys.stderr)
        print(f"TOTAL: {len(registry.documents)} document(s) in registry", file=sys.stderr)

        # Print validation summary
        if validation["valid"]:
            print("VALIDATION: ✓ Registry is valid", file=sys.stderr)
        else:
            print(f"VALIDATION: ✗ Registry has {len(validation['errors'])} error(s)", file=sys.stderr)
            for error in validation["errors"][:5]:  # First 5 errors
                print(f"  - {error}", file=sys.stderr)
            if len(validation["errors"]) > 5:
                print(f"  ... and {len(validation['errors']) - 5} more", file=sys.stderr)

        if validation["warnings"]:
            print(f"WARNINGS: {len(validation['warnings'])} warning(s)", file=sys.stderr)
            for warning in validation["warnings"][:3]:  # First 3 warnings
                print(f"  - {warning}", file=sys.stderr)

    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to save registry: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
