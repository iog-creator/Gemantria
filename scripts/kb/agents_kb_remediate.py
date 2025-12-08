#!/usr/bin/env python3
"""
AGENTS/KB Registry Remediation (Phase 27.L Batch 2/3)

Remediates pmagent control-plane DMS (control.doc_registry) based on AGENTS/KB forensics.

Reads forensics JSON and:
- Disables or hard-deletes agentpm/ ghosts (missing on disk)
- Updates agentpm → pmagent path renames where files exist
- Disables or hard-deletes orphan entries (missing on disk, no canonical surface)
- Preserves canonical AGENTS surfaces
- Normalizes metadata (enabled, importance, tags) on remaining AGENTS rows

Batch 2: Soft-disable mode (default)
Batch 3: Hard-delete mode + metadata normalization
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


def normalize_agents_metadata(engine, dry_run: bool = False) -> dict:
    """
    Normalize metadata on all AGENTS.md rows that exist on disk.

    Sets:
    - enabled = TRUE
    - importance = 'critical' for root/pmagent/scripts, 'high' for others
    - tags: ensures 'ssot' and 'agent_framework' are present (adds if missing)

    Returns:
        Dictionary with counts of normalized rows.
    """
    if dry_run:
        # Count what would be normalized
        try:
            engine_check = get_control_engine()
            with engine_check.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM control.doc_registry
                        WHERE repo_path LIKE '%AGENTS.md'
                          AND repo_path NOT LIKE 'backup/%'
                          AND repo_path NOT LIKE 'archive/%'
                    """)
                )
                count = result.scalar() or 0
            return {"normalized": count}
        except Exception:
            return {"normalized": 0}

    stats = {"normalized": 0}

    with engine.begin() as conn:
        # Get all AGENTS rows that should exist
        result = conn.execute(
            text("""
                SELECT doc_id, repo_path, importance, enabled, tags
                FROM control.doc_registry
                WHERE repo_path LIKE '%AGENTS.md'
                  AND repo_path NOT LIKE 'backup/%'
                  AND repo_path NOT LIKE 'archive/%'
            """)
        )
        rows = result.fetchall()

        for doc_id, repo_path, importance, enabled, tags in rows:
            # Check if file exists
            file_path = ROOT / repo_path
            if not file_path.exists():
                continue  # Skip ghosts (they should be deleted separately)

            # Determine target importance
            is_root = repo_path == "AGENTS.md"
            is_pmagent_root = repo_path == "pmagent/AGENTS.md"
            is_scripts_root = repo_path == "scripts/AGENTS.md"
            target_importance = "critical" if (is_root or is_pmagent_root or is_scripts_root) else "high"

            # Build tags set
            tags_list = list(tags) if tags else []
            tags_set = set(tags_list)
            tags_set.add("ssot")
            tags_set.add("agent_framework")
            if is_root:
                tags_set.add("agent_framework_index")
            new_tags = sorted(list(tags_set))

            # Check if update needed
            needs_update = not enabled or importance != target_importance or set(tags_list) != tags_set

            if needs_update:
                conn.execute(
                    text("""
                        UPDATE control.doc_registry
                        SET enabled = TRUE,
                            importance = :importance,
                            tags = :tags,
                            updated_at = NOW()
                        WHERE doc_id = :doc_id
                    """),
                    {
                        "doc_id": doc_id,
                        "importance": target_importance,
                        "tags": new_tags,
                    },
                )
                stats["normalized"] += 1

    return stats


def apply_remediation(actions: dict, dry_run: bool = False, mode: str = "soft") -> dict:
    """
    Apply remediation actions to control.doc_registry.

    Returns:
        Dictionary with counts of applied actions.
    """
    if dry_run:
        if mode == "hard":
            return {
                "deleted_agentpm_ghosts": len(actions["disable_agentpm_ghosts"]),
                "deleted_orphans": len(actions["disable_orphans"]),
                "updated_paths": len(actions["update_agentpm_to_pmagent"]),
                "kept_canonical": len(actions["keep_canonical"]),
                "kept_existing": len(actions["keep_existing"]),
            }
        else:
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

    if mode == "hard":
        stats = {
            "deleted_agentpm_ghosts": 0,
            "deleted_orphans": 0,
            "updated_paths": 0,
            "kept_canonical": len(actions["keep_canonical"]),
            "kept_existing": len(actions["keep_existing"]),
        }
    else:
        stats = {
            "disabled_agentpm_ghosts": 0,
            "disabled_orphans": 0,
            "updated_paths": 0,
            "kept_canonical": len(actions["keep_canonical"]),
            "kept_existing": len(actions["keep_existing"]),
        }

    with engine.begin() as conn:  # Transaction context
        # Handle agentpm/ ghosts (disable or hard-delete)
        for action in actions["disable_agentpm_ghosts"]:
            if mode == "hard":
                conn.execute(
                    text("DELETE FROM control.doc_registry WHERE doc_id = :doc_id"),
                    {"doc_id": action["doc_id"]},
                )
                stats["deleted_agentpm_ghosts"] += 1
            else:
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

        # Handle orphans (disable or hard-delete)
        for action in actions["disable_orphans"]:
            if mode == "hard":
                conn.execute(
                    text("DELETE FROM control.doc_registry WHERE doc_id = :doc_id"),
                    {"doc_id": action["doc_id"]},
                )
                stats["deleted_orphans"] += 1
            else:
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


def print_summary(
    actions: dict,
    stats: dict | None = None,
    dry_run: bool = False,
    mode: str = "soft",
    metadata_stats: dict | None = None,
) -> None:
    """Print remediation summary."""
    run_mode = "DRY-RUN" if dry_run else "APPLIED"
    action_mode = "HARD-DELETE" if mode == "hard" else "SOFT-DISABLE"
    print(f"\n📊 Remediation Summary ({run_mode}, {action_mode}):", file=sys.stderr)

    if mode == "hard":
        print(f"   Delete agentpm/ ghosts: {len(actions['disable_agentpm_ghosts'])}", file=sys.stderr)
        print(f"   Delete orphans: {len(actions['disable_orphans'])}", file=sys.stderr)
    else:
        print(f"   Disable agentpm/ ghosts: {len(actions['disable_agentpm_ghosts'])}", file=sys.stderr)
        print(f"   Disable orphans: {len(actions['disable_orphans'])}", file=sys.stderr)

    print(f"   Update agentpm → pmagent: {len(actions['update_agentpm_to_pmagent'])}", file=sys.stderr)
    print(f"   Keep canonical: {len(actions['keep_canonical'])}", file=sys.stderr)
    print(f"   Keep existing: {len(actions['keep_existing'])}", file=sys.stderr)

    if stats:
        print("\n✅ Applied:", file=sys.stderr)
        if mode == "hard":
            print(f"   Deleted agentpm/ ghosts: {stats.get('deleted_agentpm_ghosts', 0)}", file=sys.stderr)
            print(f"   Deleted orphans: {stats.get('deleted_orphans', 0)}", file=sys.stderr)
        else:
            print(f"   Disabled agentpm/ ghosts: {stats.get('disabled_agentpm_ghosts', 0)}", file=sys.stderr)
            print(f"   Disabled orphans: {stats.get('disabled_orphans', 0)}", file=sys.stderr)
        print(f"   Updated paths: {stats.get('updated_paths', 0)}", file=sys.stderr)

    if metadata_stats:
        print("\n✅ Metadata Normalized:", file=sys.stderr)
        print(f"   AGENTS rows normalized: {metadata_stats.get('normalized', 0)}", file=sys.stderr)

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
    parser.add_argument(
        "--mode",
        choices=["soft", "hard"],
        default="soft",
        help="Remediation mode: 'soft' (disable) or 'hard' (delete) ghosts (default: soft)",
    )
    parser.add_argument(
        "--normalize-metadata",
        action="store_true",
        help="Normalize enabled/importance/tags on remaining AGENTS rows",
    )
    args = parser.parse_args()

    dry_run = not args.apply
    mode = args.mode

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
            print(f"[DRY-RUN] Computing planned actions (no DB writes, mode={mode})...", file=sys.stderr)
            stats = apply_remediation(actions, dry_run=True, mode=mode)
        else:
            print(f"[APPLY] Applying remediation to control.doc_registry (mode={mode})...", file=sys.stderr)
            stats = apply_remediation(actions, dry_run=False, mode=mode)

        # Normalize metadata if requested
        metadata_stats = None
        if args.normalize_metadata:
            try:
                engine = get_control_engine()
                if dry_run:
                    print("[DRY-RUN] Computing metadata normalization plan...", file=sys.stderr)
                    metadata_stats = normalize_agents_metadata(engine, dry_run=True)
                else:
                    print("[APPLY] Normalizing AGENTS metadata...", file=sys.stderr)
                    metadata_stats = normalize_agents_metadata(engine, dry_run=False)
            except Exception as e:
                print(f"[WARN] Metadata normalization failed: {e}", file=sys.stderr)
                metadata_stats = {"normalized": 0}

        # Print summary
        print_summary(actions, stats, dry_run=dry_run, mode=mode, metadata_stats=metadata_stats)

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
