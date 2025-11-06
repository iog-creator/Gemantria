#!/usr/bin/env python3
"""
PMS (Project Management System) Initialization Script.

Deploys the complete PMS system in any project based on PROJECT_MASTER_PLAN.md.
Creates all necessary directories, files, and configurations.
"""

import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parent.parent


def load_master_plan(plan_path: str) -> Dict[str, Any]:
    """Load and parse the project master plan."""
    plan_file = Path(plan_path)
    if not plan_file.exists():
        plan_file = ROOT / plan_path

    if not plan_file.exists():
        print(f"❌ Master plan not found: {plan_path}")
        return {}

    try:
        with open(plan_file, encoding="utf-8") as f:
            content = f.read()

        # Extract key sections from markdown
        plan = {"path": str(plan_file), "content": content, "sections": parse_markdown_sections(content)}
        return plan
    except Exception as e:
        print(f"❌ Failed to load master plan: {e}")
        return {}


def parse_markdown_sections(content: str) -> Dict[str, str]:
    """Parse markdown content into sections."""
    sections = {}
    current_section = None
    current_content = []

    for line in content.split("\n"):
        if line.startswith("#"):
            # Save previous section
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()

            # Start new section
            current_section = line.lstrip("#").strip()
            current_content = []
        elif current_section:
            current_content.append(line)

    # Save last section
    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def create_directory_structure():
    """Create the PMS directory structure."""
    directories = [".cursor/rules", "scripts", "src", "docs/ADRs", "docs/SSOT", "docs/forest", "share", "exports"]

    for dir_path in directories:
        full_path = ROOT / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")


def create_initial_files(plan: Dict[str, Any]):
    """Create initial PMS files."""

    # Create main AGENTS.md
    agents_md = f"""# {get_project_name(plan)} - Project Documentation

## Project Overview

{plan.get("sections", {}).get("Project Overview", "Project description goes here")}

## Key Components

<!-- Add key components and their purposes here -->

## Development Workflow

{plan.get("sections", {}).get("Development Workflow", "Development workflow goes here")}

## Related Rules

| Rule | Purpose |
|------|---------|
| Rule-039 | Execution Contract |
| Rule-050 | OPS Contract |
| Rule-058 | Auto-Housekeeping |

## Rules Inventory

<!-- RULES_INVENTORY_START -->
| # | Title |
|---|-------|
| 000 | # --- |
<!-- RULES_INVENTORY_END -->
"""

    with open(ROOT / "AGENTS.md", "w", encoding="utf-8") as f:
        f.write(agents_md)

    print("📄 Created: AGENTS.md")

    # Create basic Makefile with PMS targets
    makefile_content = """# Project Management System (PMS) Makefile
# Auto-generated - do not edit directly

.PHONY: help setup housekeeping gates

# Default target
help:
	@echo "Project Management System (PMS) Targets:"
	@echo "  make setup              - Initial project setup"
	@echo "  make housekeeping        - Run auto-housekeeping"
	@echo "  make gates               - Run quality gates"
	@echo "  make pms-init           - Initialize PMS"
	@echo "  make agentmd-sync       - Sync AGENTS.md to rules"
	@echo "  make metadata-check     - Check metadata requirements"
	@echo "  make envelope-process   - Process hints envelopes"

# PMS Core Targets
pms-init:
	@echo "Initializing Project Management System..."
	python3 scripts/pms_init.py --init

pms-health-check:
	@echo "Checking PMS health..."
	python3 scripts/enforce_metadata.py --staged
	python3 scripts/envelope_processor.py --process-pending

agentmd-sync:
	@echo "Syncing AGENTS.md to Cursor rules..."
	# TODO: Implement AGENTS.md → .cursor/rules sync

housekeeping:
	@echo "Running auto-housekeeping..."
	python3 scripts/rules_audit.py
	make share-sync
	python3 scripts/generate_forest.py

metadata-check:
	@echo "Checking metadata requirements..."
	python3 scripts/enforce_metadata.py --staged

envelope-process:
	@echo "Processing hints envelopes..."
	python3 scripts/envelope_processor.py --process-pending

# Placeholder targets (implement as needed)
setup:
	@echo "Setting up project..."
	# Add your setup commands here

gates:
	@echo "Running quality gates..."
	# Add your gate commands here

share-sync:
	@echo "Syncing share directory..."
	# Add share sync logic here
"""

    with open(ROOT / "Makefile", "w", encoding="utf-8") as f:
        f.write(makefile_content)

    print("📄 Created: Makefile")


def create_pms_scripts():
    """Create the core PMS scripts."""

    scripts_to_copy = ["enforce_metadata.py", "create_agents_md.py", "rules_audit.py", "envelope_processor.py"]

    scripts_dir = ROOT / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    # Copy scripts from current project (assuming we're running from a PMS-enabled project)
    for script in scripts_to_copy:
        src_path = ROOT / "scripts" / script
        dst_path = scripts_dir / script

        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"📄 Copied script: {script}")
        else:
            print(f"⚠️  Script not found: {script}")


def create_initial_rules():
    """Create initial .cursor/rules files."""

    rules_dir = ROOT / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    # Create basic rules
    rules = [
        (
            "000-ssot-index.mdc",
            """---
description: Single Source of Truth index and governance
globs: ["**/*.md"]
alwaysApply: true
---

# Rule 000 — Single Source of Truth Index

Maintains the master index of all documentation and ensures SSOT compliance.
All documentation must be listed and cross-referenced.""",
        ),
        (
            "039-execution-contract.mdc",
            """---
description: Execution contract for automated operations
globs: ["**/*.py", "**/*.sh"]
alwaysApply: true
---

# Rule 039 — Execution Contract

All automated operations must follow the execution contract:
- Use provided Makefile targets only
- Envelope errors block execution
- Master plan is law""",
        ),
        (
            "050-ops-contract.mdc",
            """---
description: OPS contract for development workflow
globs: ["**/*.py", "**/*.md"]
alwaysApply: true
---

# Rule 050 — OPS Contract

Development workflow must follow OPS contract:
- Run housekeeping after changes
- Process hints envelopes immediately
- Maintain metadata requirements""",
        ),
        (
            "058-auto-housekeeping.mdc",
            """---
description: Auto-housekeeping after changes
globs: ["**/*"]
alwaysApply: true
---

# Rule 058 — Auto-Housekeeping

Mandatory housekeeping after any change:
- rules_audit.py
- share-sync
- forest generation""",
        ),
    ]

    for filename, content in rules:
        rule_path = rules_dir / filename
        with open(rule_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 Created rule: {filename}")


def get_project_name(plan: Dict[str, Any]) -> str:
    """Extract project name from master plan."""
    content = plan.get("content", "")
    lines = content.split("\n")

    # Look for title in first few lines
    for line in lines[:5]:
        if line.startswith("#"):
            return line.lstrip("#").strip()

    return "Project"


def create_docs_structure():
    """Create initial documentation structure."""

    # Create docs/SSOT directories
    ssot_dirs = ["docs/SSOT/schemas", "docs/SSOT/contracts"]
    for dir_path in ssot_dirs:
        full_path = ROOT / dir_path
        full_path.mkdir(parents=True, exist_ok=True)

    # Create basic SSOT files
    share_manifest = {
        "version": "1.0",
        "description": "Share directory synchronization manifest",
        "items": [
            {"src": "AGENTS.md", "dst": "share/AGENTS.md"},
            {"src": "docs/SSOT/RULES_INDEX.md", "dst": "share/RULES_INDEX.md"},
        ],
    }

    with open(ROOT / "docs" / "SSOT" / "SHARE_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(share_manifest, f, indent=2)

    print("📄 Created: docs/SSOT/SHARE_MANIFEST.json")

    # Create initial forest overview
    forest_content = """# Documentation Forest

## Overview

This documentation forest provides a comprehensive view of the project's knowledge base.

## Structure

- **ADRs/**: Architecture Decision Records
- **SSOT/**: Single Source of Truth documents
- **Forest/**: This overview and navigation

## Maintenance

This file is automatically generated by `scripts/generate_forest.py`.
Run `make housekeeping` to update.
"""

    with open(ROOT / "docs" / "forest" / "overview.md", "w", encoding="utf-8") as f:
        f.write(forest_content)

    print("📄 Created: docs/forest/overview.md")


def main():
    parser = argparse.ArgumentParser(description="Initialize Project Management System")
    parser.add_argument("--init", action="store_true", help="Initialize PMS in current directory")
    parser.add_argument("--plan", default="PROJECT_MASTER_PLAN.md", help="Path to master plan")

    args = parser.parse_args()

    if not args.init:
        print("Use --init to initialize PMS")
        return 1

    print("🚀 Initializing Project Management System (PMS)...")

    # Load master plan
    plan = load_master_plan(args.plan)
    if not plan:
        print("❌ Failed to load master plan")
        return 1

    print(f"📋 Loaded master plan: {plan['path']}")

    # Create directory structure
    print("\n📁 Creating directory structure...")
    create_directory_structure()

    # Create initial files
    print("\n📄 Creating initial files...")
    create_initial_files(plan)

    # Create PMS scripts
    print("\n🔧 Setting up PMS scripts...")
    create_pms_scripts()

    # Create initial rules
    print("\n📏 Creating initial rules...")
    create_initial_rules()

    # Create docs structure
    print("\n📚 Setting up documentation...")
    create_docs_structure()

    print("\n✅ PMS initialization complete!")
    print("\n📋 Next steps:")
    print("  1. Review and customize PROJECT_MASTER_PLAN.md")
    print("  2. Run 'make agentmd-sync' to sync rules")
    print("  3. Run 'make housekeeping' after any changes")
    print("  4. Start development with PMS governance")

    return 0


if __name__ == "__main__":
    exit(main())
