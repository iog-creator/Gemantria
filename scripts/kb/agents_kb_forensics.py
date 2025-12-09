#!/usr/bin/env python3
"""
AGENTS/KB Registry Forensics (Phase 27.L Batch 1)

Read-only introspection to map KB registry entries to canonical AGENTS surfaces.

Queries pmagent control-plane DMS (control.doc_registry) for AGENTS-related entries,
checks filesystem existence, and cross-references with canonical AGENTS surfaces.

Outputs:
- docs/analysis/AGENTS_KB_FORensics.json (detailed data)
- docs/analysis/AGENTS_KB_FORensics.md (human-readable summary)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, UTC
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Pre-flight DB check (mandatory - Rule 050 evidence-first)
preflight_script = ROOT / "scripts" / "ops" / "preflight_db_check.py"
result = subprocess.run([sys.executable, str(preflight_script), "--mode", "hint"], capture_output=True)
if result.returncode != 0:
    print(
        f"[HINT] DB preflight failed (may be DB-off mode): {result.stderr.decode()}",
        file=sys.stderr,
    )
    # Continue in read-only mode (will handle DB unavailable gracefully)

from pmagent.db.loader import get_control_engine
from pmagent.kb.registry import REGISTRY_PATH, load_registry
from sqlalchemy import text

# Canonical AGENTS surfaces (from AGENTS framework)
CANONICAL_AGENTS_SURFACES = [
    "AGENTS.md",  # Root
    "pmagent/AGENTS.md",  # pmagent package
    "scripts/AGENTS.md",  # Scripts (transitional, if still in SSOT)
]


def check_file_exists(repo_path: str, repo_root: Path = ROOT) -> bool:
    """Check if a file exists in the repository."""
    if not repo_path:
        return False
    file_path = repo_root / repo_path
    return file_path.exists() and file_path.is_file()


def query_dms_agents_entries() -> list[dict]:
    """
    Query pmagent control-plane DMS for AGENTS-related entries.

    Returns:
        List of dicts with doc_id, logical_name, repo_path, enabled, importance, tags, etc.
    """
    try:
        engine = get_control_engine()
    except Exception as e:
        print(f"[HINT] DB unavailable: {e}", file=sys.stderr)
        return []

    query = text("""
        SELECT
            d.doc_id,
            d.logical_name,
            d.role,
            d.repo_path,
            d.share_path,
            d.enabled,
            d.importance,
            d.tags,
            d.owner_component
        FROM control.doc_registry d
        WHERE
            -- AGENTS.md files
            d.repo_path LIKE '%AGENTS.md'
            OR d.repo_path LIKE '%/AGENTS.md'
            OR d.logical_name LIKE '%AGENTS%'
            -- Old agentpm/ paths
            OR d.repo_path LIKE 'agentpm/%'
            -- pmagent/ paths
            OR d.repo_path LIKE 'pmagent/%'
        ORDER BY d.repo_path, d.logical_name
    """)

    entries = []
    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()
        for row in rows:
            (
                doc_id,
                logical_name,
                role,
                repo_path,
                share_path,
                enabled,
                importance,
                tags,
                owner_component,
            ) = row
            entries.append(
                {
                    "doc_id": str(doc_id),
                    "logical_name": logical_name,
                    "role": role,
                    "repo_path": repo_path,
                    "share_path": share_path,
                    "enabled": enabled,
                    "importance": importance or "unknown",
                    "tags": tags or [],
                    "owner_component": owner_component or "unknown",
                }
            )

    return entries


def load_kb_registry_entries() -> list[dict]:
    """
    Load KB registry entries from share/kb_registry.json (if exists).

    Returns:
        List of dicts with id, path, type, owning_subsystem, etc.
    """
    if not REGISTRY_PATH.exists():
        return []

    try:
        registry = load_registry()
        entries = []
        for doc in registry.documents:
            # Filter for AGENTS-related entries
            if (
                "AGENTS" in doc.path.upper()
                or doc.path.startswith("agentpm/")
                or doc.path.startswith("pmagent/")
                or doc.type == "agents_md"
            ):
                entries.append(
                    {
                        "id": doc.id,
                        "path": doc.path,
                        "type": doc.type,
                        "owning_subsystem": doc.owning_subsystem,
                        "tags": doc.tags,
                        "provenance": doc.provenance,
                    }
                )
        return entries
    except Exception as e:
        print(f"[HINT] Failed to load KB registry: {e}", file=sys.stderr)
        return []


def map_to_canonical_surface(repo_path: str) -> str | None:
    """
    Map a repo_path to a canonical AGENTS surface.

    Returns:
        Canonical surface path (e.g., "AGENTS.md", "pmagent/AGENTS.md") or None if orphan.
    """
    if not repo_path:
        return None

    # Exact matches
    if repo_path in CANONICAL_AGENTS_SURFACES:
        return repo_path

    # Root AGENTS.md
    if repo_path == "AGENTS.md" or (repo_path.endswith("/AGENTS.md") and repo_path.count("/") == 0):
        return "AGENTS.md"

    # pmagent/AGENTS.md
    if repo_path == "pmagent/AGENTS.md":
        return "pmagent/AGENTS.md"

    # scripts/AGENTS.md (transitional)
    if repo_path == "scripts/AGENTS.md":
        return "scripts/AGENTS.md"

    # Old agentpm/ paths → should map to pmagent/AGENTS.md or be orphaned
    if repo_path.startswith("agentpm/"):
        # Check if it's a direct AGENTS.md under agentpm/
        if repo_path == "agentpm/AGENTS.md" or repo_path.endswith("/AGENTS.md"):
            # Could map to pmagent/AGENTS.md if it's the package-level one
            if repo_path.count("/") == 1:  # agentpm/AGENTS.md
                return "pmagent/AGENTS.md"
        return None  # Orphan (old agentpm/ structure)

    # Other pmagent/ paths with AGENTS.md
    if repo_path.startswith("pmagent/") and repo_path.endswith("/AGENTS.md"):
        # Subsystem AGENTS.md files (e.g., pmagent/kb/AGENTS.md)
        # These are valid but not "canonical" in the same sense
        return None  # Not a canonical surface, but valid

    return None  # Orphan


def run_forensics() -> dict:
    """
    Run AGENTS/KB forensics analysis.

    Returns:
        Dictionary with summary and detailed entries.
    """
    print("[INFO] Querying pmagent control-plane DMS for AGENTS entries...", file=sys.stderr)
    dms_entries = query_dms_agents_entries()
    print(f"[INFO] Found {len(dms_entries)} DMS entries", file=sys.stderr)

    print("[INFO] Loading KB registry entries...", file=sys.stderr)
    kb_entries = load_kb_registry_entries()
    print(f"[INFO] Found {len(kb_entries)} KB registry entries", file=sys.stderr)

    # Process DMS entries
    processed_entries = []
    by_prefix = defaultdict(lambda: {"total": 0, "missing": 0, "exists": 0})
    by_canonical = defaultdict(list)

    for entry in dms_entries:
        repo_path = entry["repo_path"] or ""
        exists_on_disk = check_file_exists(repo_path)

        # Determine prefix category
        if repo_path.startswith("agentpm/"):
            prefix = "agentpm/"
        elif repo_path.startswith("pmagent/"):
            prefix = "pmagent/"
        elif repo_path == "AGENTS.md" or repo_path.endswith("/AGENTS.md"):
            prefix = "root/AGENTS.md" if repo_path == "AGENTS.md" else "other/AGENTS.md"
        else:
            prefix = "other"

        by_prefix[prefix]["total"] += 1
        if exists_on_disk:
            by_prefix[prefix]["exists"] += 1
        else:
            by_prefix[prefix]["missing"] += 1

        # Map to canonical surface
        canonical_surface = map_to_canonical_surface(repo_path)
        if canonical_surface:
            by_canonical[canonical_surface].append(entry)
        else:
            by_canonical["orphan"].append(entry)

        processed_entry = {
            **entry,
            "exists_on_disk": exists_on_disk,
            "canonical_surface": canonical_surface,
            "prefix_category": prefix,
        }
        processed_entries.append(processed_entry)

    # Summary statistics
    total_entries = len(processed_entries)
    exists_count = sum(1 for e in processed_entries if e["exists_on_disk"])
    missing_count = total_entries - exists_count

    # Count agentpm/ ghosts
    agentpm_ghosts = sum(1 for e in processed_entries if e["prefix_category"] == "agentpm/" and not e["exists_on_disk"])

    summary = {
        "total_agents_entries": total_entries,
        "exists_on_disk": exists_count,
        "missing_on_disk": missing_count,
        "agentpm_ghosts": agentpm_ghosts,
        "by_prefix": {k: dict(v) for k, v in by_prefix.items()},
        "by_canonical": {k: len(v) for k, v in by_canonical.items()},
    }

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": summary,
        "canonical_agents_surfaces": CANONICAL_AGENTS_SURFACES,
        "entries": processed_entries,
        "kb_registry_entries": kb_entries,
        "by_canonical_detail": {
            k: [
                {
                    "doc_id": e["doc_id"],
                    "logical_name": e["logical_name"],
                    "repo_path": e["repo_path"],
                    "exists_on_disk": e["exists_on_disk"],
                    "enabled": e["enabled"],
                    "importance": e["importance"],
                }
                for e in processed_entries
                if e["canonical_surface"] == (k if k != "orphan" else None)
            ]
            for k in by_canonical.keys()
        },
    }


def write_markdown_report(data: dict, output_path: Path) -> None:
    """Write human-readable Markdown report."""
    summary = data["summary"]
    entries = data["entries"]

    with open(output_path, "w") as f:
        f.write("# AGENTS/KB Registry Forensics Report\n\n")
        f.write(f"**Generated:** {data['generated_at']}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Total AGENTS entries:** {summary['total_agents_entries']}\n")
        f.write(f"- **Exists on disk:** {summary['exists_on_disk']}\n")
        f.write(f"- **Missing on disk:** {summary['missing_on_disk']}\n")
        f.write(f"- **agentpm/ ghosts:** {summary['agentpm_ghosts']}\n\n")

        f.write("### By Prefix\n\n")
        for prefix, stats in sorted(summary["by_prefix"].items()):
            f.write(f"- **{prefix}**: {stats['total']} total, {stats['exists']} exist, {stats['missing']} missing\n")

        f.write("\n### By Canonical Surface\n\n")
        for surface, count in sorted(data["by_canonical_detail"].items()):
            f.write(f"- **{surface}**: {count} entries\n")

        f.write("\n## Sample Missing Entries (agentpm/ ghosts)\n\n")
        missing_agentpm = [e for e in entries if e["prefix_category"] == "agentpm/" and not e["exists_on_disk"]]
        for entry in missing_agentpm[:20]:  # First 20
            f.write(f"- `{entry['repo_path']}` (enabled={entry['enabled']}, importance={entry['importance']})\n")
        if len(missing_agentpm) > 20:
            f.write(f"\n... and {len(missing_agentpm) - 20} more\n")

        f.write("\n## Sample Existing Entries\n\n")
        existing = [e for e in entries if e["exists_on_disk"]][:10]
        for entry in existing:
            f.write(f"- `{entry['repo_path']}` → canonical: {entry['canonical_surface'] or 'orphan'}\n")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AGENTS/KB Registry Forensics (read-only)")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "docs" / "analysis",
        help="Output directory for reports",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        data = run_forensics()

        # Write JSON
        json_path = output_dir / "AGENTS_KB_FORensics.json"
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ JSON report written: {json_path}", file=sys.stderr)

        # Write Markdown
        md_path = output_dir / "AGENTS_KB_FORensics.md"
        write_markdown_report(data, md_path)
        print(f"✅ Markdown report written: {md_path}", file=sys.stderr)

        # Print summary to stdout
        summary = data["summary"]
        print("\n📊 Summary:", file=sys.stderr)
        print(f"   Total AGENTS entries: {summary['total_agents_entries']}", file=sys.stderr)
        print(f"   Exists on disk: {summary['exists_on_disk']}", file=sys.stderr)
        print(f"   Missing on disk: {summary['missing_on_disk']}", file=sys.stderr)
        print(f"   agentpm/ ghosts: {summary['agentpm_ghosts']}", file=sys.stderr)

        sys.exit(0)
    except Exception as e:
        print(f"ERROR: Forensics failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
