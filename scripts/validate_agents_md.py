#!/usr/bin/env python3
"""Validate all AGENTS.md files are present and up-to-date (Rule 017 + Rule 058)"""

import sys
from pathlib import Path

# Directories that MUST have AGENTS.md files
REQUIRED_AGENTS_DIRS = [
    ".",  # Root
    "src",
    "src/core",
    "src/graph",
    "src/nodes",
    "src/infra",
    "src/services",
    "src/rerank",
    "src/ssot",
    "src/persist",
    "src/obs",
    "src/utils",
    "scripts",
    "tests",
    "tools",
    "migrations",
    "docs",
    "docs/SSOT",
    "docs/ADRs",
    "docs/forest",
    "docs/phase9",
    "docs/phase10",
    "webui/dashboard",
    "webui/graph",
]


def check_agents_files():
    """Check that all required AGENTS.md files exist"""
    missing = []
    for dir_path in REQUIRED_AGENTS_DIRS:
        agents_path = Path(dir_path) / "AGENTS.md"
        if not agents_path.exists():
            missing.append(str(agents_path))

    if missing:
        print(f"[validate_agents_md] FAIL: Missing {len(missing)} AGENTS.md files:")
        for path in missing:
            print(f"  - {path}")
        return False

    print(f"[validate_agents_md] PASS: All {len(REQUIRED_AGENTS_DIRS)} required AGENTS.md files present")
    return True


def check_agents_content():
    """Check that AGENTS.md files have basic required structure"""
    issues = []
    for dir_path in REQUIRED_AGENTS_DIRS:
        agents_path = Path(dir_path) / "AGENTS.md"
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
