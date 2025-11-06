#!/usr/bin/env python3
"""
enforce_metadata.py — Automated metadata enforcement for touched files.

This script checks files for required metadata and adds it when missing.
Called automatically from hints envelopes when metadata requirements are detected.

Usage:
    python scripts/enforce_metadata.py --files file1.py file2.py
    python scripts/enforce_metadata.py --staged  # Check git staged files
"""

import argparse
from pathlib import Path
from typing import List, Set

ROOT = Path(__file__).resolve().parent.parent

# Files that require metadata (Python files in src/, scripts/)
METADATA_REQUIRED_PATTERNS = [
    "src/**/*.py",
    "scripts/*.py",
]

# Standard metadata template
METADATA_TEMPLATE = '''"""
{description}

Related Rules: Rule-039 (Execution Contract), Rule-050 (OPS Contract), Rule-058 (Auto-Housekeeping)
Related ADRs: ADR-032 (Organic AI Discovery), ADR-019 (Data Contracts)
"""
'''


def extract_description_from_filename(filepath: Path) -> str:
    """Extract a reasonable description from the file path and name."""
    if "graph" in str(filepath):
        return "LangGraph pipeline orchestration and execution engine"
    elif "enrichment" in str(filepath):
        return "AI enrichment node for theological context generation"
    elif "network_aggregator" in str(filepath):
        return "Network aggregator node for semantic graph building"
    elif "analysis_runner" in str(filepath):
        return "Analysis runner node for graph analysis and export"
    elif "create_agents_md" in str(filepath):
        return "Automated AGENTS.md file creation script"
    else:
        # Generic description based on filename
        name = filepath.stem.replace("_", " ").title()
        return f"{name} implementation"


def has_metadata(filepath: Path) -> bool:
    """Check if file has proper metadata (docstring with Related Rules)."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Look for docstring with Related Rules
        return "Related Rules:" in content and "Related ADRs:" in content
    except Exception:
        return False


def add_metadata(filepath: Path) -> bool:
    """Add metadata to file if missing."""
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()

        # Skip if already has metadata
        content = "".join(lines)
        if "Related Rules:" in content:
            return False

        # Find the first import or code line (after shebang if present)
        insert_index = 0

        # Skip shebang if present
        if lines and lines[0].startswith("#!"):
            insert_index = 1
            # Skip blank lines after shebang
            while insert_index < len(lines) and lines[insert_index].strip() == "":
                insert_index += 1

        # Extract description and create metadata
        description = extract_description_from_filename(filepath)
        metadata = METADATA_TEMPLATE.format(description=description)

        # Insert metadata
        lines.insert(insert_index, metadata + "\n")

        # Write back
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ Added metadata to {filepath}")
        return True

    except Exception as e:
        print(f"❌ Failed to add metadata to {filepath}: {e}")
        return False


def get_files_to_check(patterns: List[str]) -> Set[Path]:
    """Get all files matching the patterns."""
    files = set()
    for pattern in patterns:
        for filepath in ROOT.glob(pattern):
            if filepath.is_file():
                files.add(filepath)
    return files


def get_staged_files() -> Set[Path]:
    """Get files that are staged in git."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], cwd=ROOT, capture_output=True, text=True, check=True
        )
        files = set()
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                filepath = ROOT / line.strip()
                if filepath.exists() and filepath.suffix == ".py":
                    files.add(filepath)
        return files
    except Exception:
        return set()


def main():
    parser = argparse.ArgumentParser(description="Enforce metadata requirements")
    parser.add_argument("--files", nargs="*", help="Specific files to check")
    parser.add_argument("--staged", action="store_true", help="Check git staged files")
    parser.add_argument("--fix", action="store_true", help="Automatically fix missing metadata")

    args = parser.parse_args()

    if args.files:
        files_to_check = {ROOT / f for f in args.files}
    elif args.staged:
        files_to_check = get_staged_files()
    else:
        files_to_check = get_files_to_check(METADATA_REQUIRED_PATTERNS)

    print(f"🔍 Checking {len(files_to_check)} files for metadata...")

    missing_metadata = []
    for filepath in sorted(files_to_check):
        if not has_metadata(filepath):
            missing_metadata.append(filepath)

    if missing_metadata:
        print(f"❌ Found {len(missing_metadata)} files missing metadata:")
        for filepath in missing_metadata:
            print(f"  - {filepath.relative_to(ROOT)}")

        if args.fix:
            print("\n🔧 Adding metadata...")
            fixed = 0
            for filepath in missing_metadata:
                if add_metadata(filepath):
                    fixed += 1

            print(f"✅ Fixed {fixed}/{len(missing_metadata)} files")
            return 0 if fixed == len(missing_metadata) else 1
        else:
            print("\n💡 Run with --fix to automatically add metadata")
            return 1
    else:
        print("✅ All files have proper metadata")
        return 0


if __name__ == "__main__":
    exit(main())
