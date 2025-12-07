#!/usr/bin/env python3
"""
AGENTS/KB Registry Remediation (Phase 27.L Batch 2)

Remediates pmagent control-plane DMS (control.doc_registry) based on AGENTS/KB forensics.

Reads forensics JSON and:
- Disables agentpm/ ghosts (missing on disk)
- Updates agentpm → pmagent path renames where files exist
- Disables orphan entries (missing on disk, no canonical surface)
- Preserves canonical AGENTS surfaces

Uses control.doc_registry.enabled for soft-disable (no hard deletes).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Pre-flight DB check (mandatory - Rule 050 evidence-first)
preflight_script = ROOT / "scripts" / "ops" / "preflight_db_check.py"
result = subprocess.run([sys.executable, str(preflight_script), "--mode", "hint"], capture_output=True)
if result.returncode != 0:
    print(f"[HINT] DB preflight failed (may be DB-off mode): {result.stderr.decode()}", file=sys.stderr)
    # Continue in read-only mode (will handle DB unavailable gracefully)

from pmagent.db.loader import get_control_engine
from sqlalchemy import text

FORensics_PATH = ROOT / "docs" / "analysis" / "AGENTS_KB_FORensics.json"

# Canonical AGENTS surfaces (protected from remediation)
CANONICAL_SURFACES = {
    "AGENTS.md",
    "pmagent/AGENTS.md",
    "scripts/AGENTS.md",
}


def check_file_exists(repo_path: str, repo_root: Path = ROOT) -> bool:
    """Check if a file exists in the repository."""
    if not repo_path:
        return False
    file_path = repo_root / repo_path
    return file_path.exists() and file_path.is_file()


def compute_pmagent_candidate(agentpm_path: str) -> str | None:
    """Compute pmagent/ candidate path from agentpm/ path."""
    if not agentpm_path.startswith("agentpm/"):
        return None
    return "pmagent/" + agentpm_path[len("agentpm/") :]


def load_forensics() -> dict:
    """Load forensics JSON data."""
    if not FORensics_PATH.exists():
        raise FileNotFoundError(f"Forensics file not found: {FORensics_PATH}")
    with open(FORensics_PATH) as f:
        return json.load(f)


def plan_remediation(forensics_data: dict) -> dict:
    """
    Plan remediation actions based on forensics data.

    Returns:
        Dictionary with action counts and detailed action list.
    """
    entries = forensics_data["entries"]
    actions = {
        "disable_agentpm_ghosts": [],
        "disable_orphans": [],
        "update_agentpm_to_pmagent": [],
        "keep_canonical": [],
        "keep_existing": [],
    }

    # Track which pmagent/ paths already exist in DMS
    existing_pmagent_paths = set()
    for entry in entries:
        repo_path = entry.get("repo_path") or ""
        if repo_path.startswith("pmagent/") and entry.get("exists_on_disk"):
            existing_pmagent_paths.add(repo_path)

    for entry in entries:
        doc_id = entry["doc_id"]
        repo_path = entry.get("repo_path") or ""
        exists_on_disk = entry.get("exists_on_disk", False)
        canonical_surface = entry.get("canonical_surface")
        prefix_category = entry.get("prefix_category", "")

        # Case 1: Canonical surfaces - always keep
        if repo_path in CANONICAL_SURFACES or canonical_surface in CANONICAL_SURFACES:
            actions["keep_canonical"].append(
                {
                    "doc_id": doc_id,
                    "repo_path": repo_path,
                    "reason": "canonical_surface",
                }
            )
            continue

        # Case 2: agentpm/ ghosts (missing on disk)
        if prefix_category == "agentpm/" and not exists_on_disk:
            pmagent_candidate = compute_pmagent_candidate(repo_path)
            if pmagent_candidate and pmagent_candidate in existing_pmagent_paths:
                # There's already a pmagent/ entry for this, disable the agentpm/ ghost
                actions["disable_agentpm_ghosts"].append(
                    {
                        "doc_id": doc_id,
                        "repo_path": repo_path,
                        "reason": "agentpm_ghost_duplicate",
                        "pmagent_candidate": pmagent_candidate,
                    }
                )
            elif pmagent_candidate and check_file_exists(pmagent_candidate):
                # File exists at pmagent/ location, update path
                actions["update_agentpm_to_pmagent"].append(
                    {
                        "doc_id": doc_id,
                        "old_repo_path": repo_path,
                        "new_repo_path": pmagent_candidate,
                        "reason": "agentpm_to_pmagent_rename",
                    }
                )
            else:
                # Pure ghost, no replacement
                actions["disable_agentpm_ghosts"].append(
                    {
                        "doc_id": doc_id,
                        "repo_path": repo_path,
                        "reason": "agentpm_ghost_no_replacement",
                    }
                )
            continue

        # Case 3: General missing-on-disk orphans
        if not exists_on_disk and (canonical_surface is None or canonical_surface == "orphan"):
            actions["disable_orphans"].append(
                {
                    "doc_id": doc_id,
                    "repo_path": repo_path,
                    "reason": "missing_orphan",
                }
            )
            continue

        # Case 4: Everything else that exists - keep
        if exists_on_disk:
            actions["keep_existing"].append(
                {
                    "doc_id": doc_id,
                    "repo_path": repo_path,
                    "reason": "exists_on_disk",
                }
            )

    return actions


def apply_remediation(actions: dict, dry_run: bool = False) -> dict:
    """
    Apply remediation actions to control.doc_registry.

    Returns:
        Dictionary with counts of applied actions.
    """
    if dry_run:
        return {
            "disabled_agentpm_ghosts": len(actions["disable_agentpm_ghosts"]),
            "disabled_orphans": len(actions["disable_orphans"]),
            "updated_paths": len(actions["update_agentpm_to_pmagent"]),
            "kept_canonical": len(actions["keep_canonical"]),
            "kept_existing": len(actions["keep_existing"]),
        }

    try:
        engine = get_control_engine()
    except Exception as e:
        raise RuntimeError(f"Failed to connect to control-plane DB: {e}") from e

    stats = {
        "disabled_agentpm_ghosts": 0,
        "disabled_orphans": 0,
        "updated_paths": 0,
        "kept_canonical": len(actions["keep_canonical"]),
        "kept_existing": len(actions["keep_existing"]),
    }

    with engine.begin() as conn:  # Transaction context
        # Disable agentpm/ ghosts
        for action in actions["disable_agentpm_ghosts"]:
            conn.execute(
                text(
                    """
                    UPDATE control.doc_registry
                    SET enabled = FALSE,
                        updated_at = NOW()
                    WHERE doc_id = :doc_id
                    """
                ),
                {"doc_id": action["doc_id"]},
            )
            stats["disabled_agentpm_ghosts"] += 1

        # Disable orphans
        for action in actions["disable_orphans"]:
            conn.execute(
                text(
                    """
                    UPDATE control.doc_registry
                    SET enabled = FALSE,
                        updated_at = NOW()
                    WHERE doc_id = :doc_id
                    """
                ),
                {"doc_id": action["doc_id"]},
            )
            stats["disabled_orphans"] += 1

        # Update agentpm → pmagent paths
        for action in actions["update_agentpm_to_pmagent"]:
            # Also update logical_name if it contains agentpm/
            old_logical = None
            result = conn.execute(
                text("SELECT logical_name FROM control.doc_registry WHERE doc_id = :doc_id"),
                {"doc_id": action["doc_id"]},
            ).fetchone()
            if result:
                old_logical = result[0]
                new_logical = old_logical.replace("agentpm/", "pmagent/") if "agentpm/" in old_logical else old_logical
            else:
                new_logical = None

            update_params = {
                "doc_id": action["doc_id"],
                "new_repo_path": action["new_repo_path"],
            }
            update_sql = """
                UPDATE control.doc_registry
                SET repo_path = :new_repo_path,
                    updated_at = NOW()
            """
            if new_logical and new_logical != old_logical:
                update_sql += ", logical_name = :new_logical_name"
                update_params["new_logical_name"] = new_logical
            update_sql += " WHERE doc_id = :doc_id"

            conn.execute(text(update_sql), update_params)
            stats["updated_paths"] += 1

    return stats


def print_summary(actions: dict, stats: dict | None = None, dry_run: bool = False) -> None:
    """Print remediation summary."""
    mode = "DRY-RUN" if dry_run else "APPLIED"
    print(f"\n📊 Remediation Summary ({mode}):", file=sys.stderr)
    print(f"   Disable agentpm/ ghosts: {len(actions['disable_agentpm_ghosts'])}", file=sys.stderr)
    print(f"   Disable orphans: {len(actions['disable_orphans'])}", file=sys.stderr)
    print(f"   Update agentpm → pmagent: {len(actions['update_agentpm_to_pmagent'])}", file=sys.stderr)
    print(f"   Keep canonical: {len(actions['keep_canonical'])}", file=sys.stderr)
    print(f"   Keep existing: {len(actions['keep_existing'])}", file=sys.stderr)

    if stats:
        print("\n✅ Applied:", file=sys.stderr)
        print(f"   Disabled agentpm/ ghosts: {stats['disabled_agentpm_ghosts']}", file=sys.stderr)
        print(f"   Disabled orphans: {stats['disabled_orphans']}", file=sys.stderr)
        print(f"   Updated paths: {stats['updated_paths']}", file=sys.stderr)

    # Show sample actions
    if actions["disable_agentpm_ghosts"]:
        print("\n📋 Sample agentpm/ ghosts to disable (first 5):", file=sys.stderr)
        for action in actions["disable_agentpm_ghosts"][:5]:
            print(f"   - {action['repo_path']} ({action['reason']})", file=sys.stderr)

    if actions["update_agentpm_to_pmagent"]:
        print("\n📋 Sample path updates (first 5):", file=sys.stderr)
        for action in actions["update_agentpm_to_pmagent"][:5]:
            print(f"   - {action['old_repo_path']} → {action['new_repo_path']}", file=sys.stderr)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AGENTS/KB Registry Remediation")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply remediation (default: dry-run)",
    )
    parser.add_argument(
        "--forensics-path",
        type=Path,
        default=FORensics_PATH,
        help="Path to forensics JSON file",
    )
    args = parser.parse_args()

    dry_run = not args.apply

    try:
        # Load forensics data
        print(f"[INFO] Loading forensics from {args.forensics_path}...", file=sys.stderr)
        forensics_data = load_forensics()
        print(f"[INFO] Loaded {len(forensics_data['entries'])} entries", file=sys.stderr)

        # Plan remediation
        print("[INFO] Planning remediation actions...", file=sys.stderr)
        actions = plan_remediation(forensics_data)

        # Apply or dry-run
        if dry_run:
            print("[DRY-RUN] Computing planned actions (no DB writes)...", file=sys.stderr)
            stats = apply_remediation(actions, dry_run=True)
        else:
            print("[APPLY] Applying remediation to control.doc_registry...", file=sys.stderr)
            stats = apply_remediation(actions, dry_run=False)

        # Print summary
        print_summary(actions, stats, dry_run=dry_run)

        if dry_run:
            print("\n💡 To apply these changes, run with --apply", file=sys.stderr)

        sys.exit(0)
    except Exception as e:
        print(f"ERROR: Remediation failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
