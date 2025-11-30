#!/usr/bin/env python3
"""
Export All AGENTS.md Files to Share Folder

Finds all AGENTS.md files in the repository and exports them to share/agents_md/
as full files (not head exports). This ensures the PM has complete context
from all AGENTS.md files.

Usage:
    python scripts/util/export_all_agents_md.py [--output-dir <path>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

OUT_DIR = REPO / "share" / "agents_md"
MANIFEST_FILE = OUT_DIR / "manifest.json"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file content."""
    content = file_path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def export_agents_md_files(repo_root: Path, out_dir: Path) -> dict[str, Any]:
    """Find and export all AGENTS.md files to share/agents_md/."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # Find all AGENTS.md files
    agents_files = list(repo_root.rglob("AGENTS.md"))
    agents_files = [f for f in agents_files if f.is_file()]

    exported_files = []
    manifest = {
        "schema": "agents_md_export.v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "repo_root": str(repo_root),
        "total_files": len(agents_files),
        "files": [],
    }

    for agents_file in sorted(agents_files):
        # Compute relative path from repo root
        rel_path = agents_file.relative_to(repo_root)
        rel_path_str = str(rel_path)

        # Create safe filename for share folder (replace / with _)
        safe_name = rel_path_str.replace("/", "_").replace("\\", "_")
        out_file = out_dir / safe_name

        try:
            # Read file content
            content = agents_file.read_text(encoding="utf-8")
            file_hash = compute_file_hash(agents_file)
            mtime = agents_file.stat().st_mtime

            # Write to share folder
            out_file.write_text(content, encoding="utf-8")

            # Add to manifest
            file_entry = {
                "source_path": rel_path_str,
                "export_path": f"share/agents_md/{safe_name}",
                "safe_name": safe_name,
                "file_hash": file_hash,
                "mtime": mtime,
                "line_count": len(content.splitlines()),
                "size_bytes": len(content.encode("utf-8")),
            }
            manifest["files"].append(file_entry)
            exported_files.append(rel_path_str)

        except Exception as exc:
            print(f"⚠️  Error exporting {rel_path_str}: {exc}", file=sys.stderr)
            manifest["files"].append(
                {
                    "source_path": rel_path_str,
                    "export_path": None,
                    "error": str(exc),
                }
            )

    # Write manifest
    manifest_file = out_dir / "manifest.json"
    manifest_file.write_text(
        json.dumps(manifest, indent=2, default=str),
        encoding="utf-8",
    )

    return {
        "total": len(agents_files),
        "exported": len(exported_files),
        "manifest_path": str(manifest_file.relative_to(repo_root)),
        "files": exported_files,
    }


def main() -> int:
    """Main entrypoint."""
    parser = argparse.ArgumentParser(description="Export all AGENTS.md files to share folder")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (default: share/agents_md)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO,
        help="Repository root directory (default: detected)",
    )

    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    out_dir = args.output_dir.resolve() if args.output_dir else OUT_DIR

    result = export_agents_md_files(repo_root, out_dir)

    print(f"✅ Exported {result['exported']}/{result['total']} AGENTS.md files")
    print(f"📄 Manifest: {result['manifest_path']}")
    if result["files"]:
        print("📋 Files exported:")
        for file_path in result["files"][:10]:  # Show first 10
            print(f"   - {file_path}")
        if len(result["files"]) > 10:
            print(f"   ... and {len(result['files']) - 10} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
