#!/usr/bin/env python3
"""
Seed the hint_registry with initial hints.

Loads hints from discovery catalog and inserts them into control.hint_registry.
"""

from __future__ import annotations

import json
import subprocess
import sys
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

from sqlalchemy import text

from pmagent.db.loader import get_control_engine


# Initial seed hints (minimal set of REQUIRED hints)
INITIAL_HINTS = [
    {
        "logical_name": "docs.dms_only",
        "scope": "handoff",
        "applies_to": {"flow": "handoff.generate"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "DMS-only, no fallback. share/ is derived from control.doc_registry only.",
            "commands": [],
            "constraints": {"rule_ref": "050", "no_fallback": True},
            "metadata": {"source": "Rule-050", "agent_file": "AGENTS.md"},
        },
        "priority": 0,
    },
    {
        "logical_name": "status.local_gates_first",
        "scope": "status_api",
        "applies_to": {"flow": "status_snapshot"},
        "kind": "REQUIRED",
        "injection_mode": "META_ONLY",
        "payload": {
            "text": "Local gates are primary; CI is a mirror only. Never block on CI.",
            "commands": ["ruff format --check . && ruff check .", "make book.smoke"],
            "constraints": {"rule_ref": "050", "local_first": True},
            "metadata": {"source": "Rule-050", "section": "5.5"},
        },
        "priority": 0,
    },
    {
        "logical_name": "share.dms_only",
        "scope": "handoff",
        "applies_to": {"flow": "handoff.generate"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "share/ sync is DMS-only. No manifest fallback.",
            "commands": ["make share.sync"],
            "constraints": {"rule_ref": "030", "dms_only": True},
            "metadata": {"source": "Rule-030", "agent_file": "AGENTS.md"},
        },
        "priority": 1,
    },
    {
        "logical_name": "governance.fail_closed",
        "scope": "handoff",
        "applies_to": {"flow": "handoff.generate"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "Governance scripts must fail-closed on errors. No silent fallbacks.",
            "commands": [],
            "constraints": {"rule_ref": "039", "fail_closed": True},
            "metadata": {"source": "Rule-039", "agent_file": "AGENTS.md"},
        },
        "priority": 5,
    },
    {
        "logical_name": "reality.green.required_checks",
        "scope": "status_api",
        "applies_to": {"flow": "reality_check"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "reality.green STRICT must pass all required checks before declaring system ready.",
            "commands": ["make reality.green STRICT"],
            "constraints": {"rule_ref": "050", "required_before": "PR"},
            "metadata": {"source": "Rule-050", "section": "5"},
        },
        "priority": 10,
    },
    {
        "logical_name": "db.dsn_env_var_ignored",
        "scope": "infra",
        "applies_to": {"flow": "db_connection"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "get_connection_dsn() ignores 'env_var' arg. Use scripts.config.env for specific DBs (e.g. Bible DB).",
            "commands": [],
            "constraints": {"use_loader": True},
            "metadata": {"source": "Phase 8 Recovery"},
        },
        "priority": 20,
    },
    {
        "logical_name": "data.bible_lemma_english",
        "scope": "data",
        "applies_to": {"flow": "ingest_bible_nouns"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "Bible DB 'lemma' column contains English definitions. Use surface form for Hebrew text & Gematria.",
            "commands": [],
            "constraints": {"use_surface": True},
            "metadata": {"source": "Phase 8 Recovery"},
        },
        "priority": 20,
    },
    {
        "logical_name": "ops.regenerate_truncation",
        "scope": "ops",
        "applies_to": {"flow": "regenerate_network"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "Regeneration TRUNCATES concept_network. Ensure canonical data is backed up before running.",
            "commands": ["pmagent graph regenerate --force"],
            "constraints": {"backup_required": True},
            "metadata": {"source": "Phase 8 Recovery"},
        },
        "priority": 20,
    },
    {
        "logical_name": "governance.ghost_records",
        "scope": "governance",
        "applies_to": {"flow": "housekeeping"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "DMS ghost records (enabled in DB but missing on disk) block housekeeping. Run ingest_docs_to_db to self-heal.",
            "commands": ["python scripts/governance/ingest_docs_to_db.py"],
            "constraints": {"rule_ref": "058", "self_healing": True},
            "metadata": {"source": "Phase 28 Cleanup"},
        },
        "priority": 10,
    },
    {
        "logical_name": "governance.agents_md_requirements",
        "scope": "governance",
        "applies_to": {"flow": "archival"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "AGENTS.md is MANDATORY in every top-level directory (including docs/) even if content is archived.",
            "commands": ["touch docs/AGENTS.md"],
            "constraints": {"rule_ref": "006", "structure_enforcement": True},
            "metadata": {"source": "Phase 28 Cleanup"},
        },
        "priority": 10,
    },
    {
        "logical_name": "governance.manifest_cleanup",
        "scope": "governance",
        "applies_to": {"flow": "archival"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "Archiving files requires removing them from SHARE_MANIFEST.json to prevent sync failures.",
            "commands": [],
            "constraints": {"rule_ref": "030", "manifest_sync": True},
            "metadata": {"source": "Phase 28 Cleanup"},
        },
        "priority": 10,
    },
    {
        "logical_name": "governance.agents_md_sync",
        "scope": "governance",
        "applies_to": {"flow": "check_agents_md_sync"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "Sync check script must handle deleted directories gracefully. Do not flag missing AGENTS.md if parent dir is gone.",
            "commands": [],
            "constraints": {"rule_ref": "006", "graceful_fail": True},
            "metadata": {"source": "Phase 27.I Fix"},
        },
        "priority": 10,
    },
    {
        "logical_name": "ops.circular_boot",
        "scope": "ops",
        "applies_to": {"flow": "reality_check"},
        "kind": "SUGGESTED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "If OA State mismatch persists (Boot vs Reality), run 'make pm.boot' to refresh bootstrap state, then re-run reality.green.",
            "commands": ["make pm.boot", "make reality.green"],
            "constraints": {"circular_dependency": True},
            "metadata": {"source": "Phase 27.I Fix"},
        },
        "priority": 15,
    },
    {
        "logical_name": "governance.dms_stale",
        "scope": "governance",
        "applies_to": {"flow": "archival"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "When archiving AGENTS.md, you MUST disable the old entry in control.doc_registry to prevent 'ghost' contract violations.",
            "commands": [],
            "constraints": {"rule_ref": "058", "no_ghosts": True},
            "metadata": {"source": "Phase 27.I Fix"},
        },
        "priority": 10,
    },
    {
        "logical_name": "governance.dspy_examples_min",
        "scope": "governance",
        "applies_to": {"flow": "dspy_training"},
        "kind": "REQUIRED",
        "injection_mode": "PRE_PROMPT",
        "payload": {
            "text": "Rule 101: New DSPy training files MUST contain at least 10 examples covering edge cases.",
            "commands": [],
            "constraints": {"rule_ref": "101", "min_examples": 10},
            "metadata": {"source": "User Mandate"},
        },
        "priority": 0,
    },
]


def seed_hint_registry(discovery_catalog_path: Path | None = None) -> int:
    """
    Seed the hint_registry with initial hints.

    Args:
        discovery_catalog_path: Optional path to discovery catalog JSON.
                               If provided, will also seed hints from catalog.

    Returns:
        0 on success, 1 on error
    """
    try:
        engine = get_control_engine()
    except Exception as exc:
        print(f"ERROR: Unable to get control-plane engine: {exc}", file=sys.stderr)
        return 1

    with engine.begin() as conn:
        # Insert initial hints
        for hint in INITIAL_HINTS:
            try:
                conn.execute(
                    text(
                        """
                        INSERT INTO control.hint_registry
                        (logical_name, scope, applies_to, kind, injection_mode, payload, priority, enabled)
                        VALUES (:logical_name, :scope, :applies_to, :kind, :injection_mode, :payload, :priority, TRUE)
                        ON CONFLICT (logical_name) DO UPDATE SET
                            scope = EXCLUDED.scope,
                            applies_to = EXCLUDED.applies_to,
                            kind = EXCLUDED.kind,
                            injection_mode = EXCLUDED.injection_mode,
                            payload = EXCLUDED.payload,
                            priority = EXCLUDED.priority,
                            updated_at = NOW()
                        """,
                    ),
                    {
                        "logical_name": hint["logical_name"],
                        "scope": hint["scope"],
                        "applies_to": json.dumps(hint["applies_to"]),
                        "kind": hint["kind"],
                        "injection_mode": hint["injection_mode"],
                        "payload": json.dumps(hint["payload"]),
                        "priority": hint["priority"],
                    },
                )
                print(f"✅ Seeded hint: {hint['logical_name']}")
            except Exception as exc:
                print(
                    f"⚠️  Failed to seed hint {hint['logical_name']}: {exc}",
                    file=sys.stderr,
                )

        # Optionally load from discovery catalog
        if discovery_catalog_path and discovery_catalog_path.exists():
            catalog = json.loads(discovery_catalog_path.read_text(encoding="utf-8"))
            print(f"\nLoading {len(catalog.get('hints', []))} hints from discovery catalog...")

            for hint_data in catalog.get("hints", []):
                # Map discovery catalog to registry format
                logical_name = hint_data.get("logical_name") or hint_data.get("text", "").split(":")[0]
                if not logical_name:
                    continue

                # Determine scope and flow from source file
                source_file = hint_data.get("source_file", "")
                if "handoff" in source_file.lower():
                    scope = "handoff"
                    flow = "handoff.generate"
                elif "status" in source_file.lower() or "reality" in source_file.lower():
                    scope = "status_api"
                    flow = "status_snapshot"
                elif "pmagent" in source_file.lower() or "plan" in source_file.lower():
                    scope = "pmagent"
                    flow = "capability_session"
                else:
                    scope = "handoff"  # default
                    flow = "handoff.generate"

                kind = hint_data.get("suggested_kind", "SUGGESTED")

                try:
                    conn.execute(
                        text(
                            """
                            INSERT INTO control.hint_registry
                            (logical_name, scope, applies_to, kind, injection_mode, payload, priority, enabled)
                            VALUES (:logical_name, :scope, :applies_to, :kind, :injection_mode, :payload, :priority, TRUE)
                            ON CONFLICT (logical_name) DO UPDATE SET
                                scope = EXCLUDED.scope,
                                applies_to = EXCLUDED.applies_to,
                                kind = EXCLUDED.kind,
                                injection_mode = EXCLUDED.injection_mode,
                                payload = EXCLUDED.payload,
                                priority = EXCLUDED.priority,
                                updated_at = NOW()
                            """,
                        ),
                        {
                            "logical_name": logical_name,
                            "scope": scope,
                            "applies_to": json.dumps({"flow": flow}),
                            "kind": kind,
                            "injection_mode": "PRE_PROMPT",  # default
                            "payload": json.dumps({"text": hint_data.get("text", "")}),
                            "priority": 10,  # lower priority for discovered hints
                        },
                    )
                    print(f"✅ Seeded discovered hint: {logical_name}")
                except Exception as exc:
                    print(
                        f"⚠️  Failed to seed discovered hint {logical_name}: {exc}",
                        file=sys.stderr,
                    )

    print("\n✅ Hint registry seeding complete")
    return 0


def main() -> int:
    """Main entrypoint."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed hint_registry with initial hints")
    parser.add_argument(
        "--discovery-catalog",
        type=Path,
        help="Path to discovery catalog JSON (from discover_hints.py)",
    )

    args = parser.parse_args()

    return seed_hint_registry(args.discovery_catalog)


if __name__ == "__main__":
    sys.exit(main())
