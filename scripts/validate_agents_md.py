#!/usr/bin/env python3
"""Validate all AGENTS.md files are present and up-to-date (Rule 017 + Rule 058)"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def get_required_directories() -> list[str]:
    """Get directories that require AGENTS.md files (dynamic discovery, matches create_agents_md.py)."""
    # Directories to exclude from AGENTS.md requirement
    EXCLUDED_DIRS = {
        "__pycache__",  # Python bytecode cache
        ".git",  # Git metadata
        "node_modules",  # Node.js dependencies
        ".venv",  # Python virtual environment
        "venv",  # Python virtual environment (alternate)
        ".pytest_cache",  # Pytest cache
        ".mypy_cache",  # Mypy cache
        ".ruff_cache",  # Ruff cache
        "__pypackages__",  # PDM packages
        "public",  # Static/generated web assets
        "dist",  # Build output
        "build",  # Build output
        ".egg-info",  # Python package metadata
    }

    required = [".", "scripts", "migrations", "tests", "tools"]  # Root + tool directories

    # Add all src subdirectories (excluding cache/generated dirs)
    src_dir = ROOT / "src"
    if src_dir.exists():
        required.append("src")
        for subdir in src_dir.iterdir():
            if (
                subdir.is_dir()
                and not subdir.name.startswith(".")
                and subdir.name not in EXCLUDED_DIRS
                and not subdir.name.endswith(".egg-info")
            ):
                required.append(f"src/{subdir.name}")

    # Add all agentpm subdirectories (excluding cache/generated dirs)
    agentpm_dir = ROOT / "agentpm"
    if agentpm_dir.exists():
        for subdir in agentpm_dir.iterdir():
            if (
                subdir.is_dir()
                and not subdir.name.startswith(".")
                and subdir.name not in EXCLUDED_DIRS
            ):
                required.append(f"agentpm/{subdir.name}")

    # Add all docs subdirectories (excluding cache/generated dirs)
    docs_dir = ROOT / "docs"
    if docs_dir.exists():
        required.append("docs")
        for subdir in docs_dir.iterdir():
            if (
                subdir.is_dir()
                and not subdir.name.startswith(".")
                and subdir.name not in EXCLUDED_DIRS
            ):
                required.append(f"docs/{subdir.name}")

    # Add webui subdirectories (excluding generated/static dirs)
    webui_dir = ROOT / "webui"
    if webui_dir.exists():
        for subdir in webui_dir.iterdir():
            if (
                subdir.is_dir()
                and not subdir.name.startswith(".")
                and subdir.name not in EXCLUDED_DIRS
                and subdir.name not in {"public", "dist", "build"}
            ):
                required.append(f"webui/{subdir.name}")

    return sorted(set(required))  # Remove duplicates and sort


def check_agents_files():
    """Check that all required AGENTS.md files exist"""
    required_dirs = get_required_directories()
    missing = []
    for dir_path in required_dirs:
        agents_path = ROOT / dir_path / "AGENTS.md"
        if not agents_path.exists():
            missing.append(dir_path)

    if missing:
        print(f"[validate_agents_md] FAIL: Missing {len(missing)} AGENTS.md files:")
        for path in missing:
            print(f"  - {path}/AGENTS.md")
        return False

    print(f"[validate_agents_md] PASS: All {len(required_dirs)} required AGENTS.md files present")
    return True


def check_agents_content():
    """Check that AGENTS.md files have basic required structure"""
    required_dirs = get_required_directories()
    issues = []
    for dir_path in required_dirs:
        agents_path = ROOT / dir_path / "AGENTS.md"
        if not agents_path.exists():
            continue

        content = agents_path.read_text()
        if len(content.strip()) < 50:
            issues.append(f"{agents_path}: Content too short (< 50 chars)")
        if not content.startswith("# AGENTS.md"):
            issues.append(f"{agents_path}: Missing '# AGENTS.md' header")
        if "## Directory Purpose" not in content:
            issues.append(f"{agents_path}: Missing '## Directory Purpose' section")

    if issues:
        print(f"[validate_agents_md] WARN: {len(issues)} content issues:")
        for issue in issues:
            print(f"  - {issue}")
        # Non-fatal - just warnings
        return True

    print("[validate_agents_md] PASS: All AGENTS.md files have valid structure")
    return True


def main():
    """Run all validation checks"""
    presence_ok = check_agents_files()
    content_ok = check_agents_content()

    if not presence_ok:
        sys.exit(1)

    # Content warnings are non-fatal
    sys.exit(0)


if __name__ == "__main__":
    main()
