#!/usr/bin/env python3
"""
doc_cleanup_phase27.py

Aggressively cleans up docs/ directory by moving files to archive/.
Based on Phase 27 cleanup plan.
"""

import shutil
import logging
import argparse
from pathlib import Path
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"
ARCHIVE_DIR = REPO_ROOT / "archive"

# Rules
PRESERVE_DIRS = {
    "SSOT",
    "ADRs",
    "analysis",
}

# Directories to archive completely
ARCHIVE_DIRS = {
    "audits": "audits",
    "ops": "ops",
    "atlas": "atlas",
    "forest": "forest",
    "handoff": "handoff",
    "hints": "hints",
    "ingestion": "ingestion",
    "kb": "kb",
    "lm": "lm",
    "mcp": "mcp",
    "mining": "mining",
    "observability": "observability",
    "phase9": "phases/early",
    "phase10": "phases/early",
    "plans": "plans",
    "projects": "projects",
    "quality": "quality",
    "research": "research",
    "rfcs": "rfcs",
    "runbooks": "runbooks",
    "schema": "schema",
    "schemas": "schemas",
    "smokes": "smokes",
    "sql": "sql",
    "status": "status",
    "system": "system",
    "temporal": "temporal",
    "tickets": "tickets",
    "tools": "tools",
    "ui": "ui",
    "util": "util",
    "vendor": "vendor",
    "webui": "webui",
}

# Root files to ALWAYS keep (Evergreen)
KEEP_ROOT_FILES = {
    "README.md",
    "INDEX.md",
}


def git_mv(src, dest, dry_run=False):
    """Moves a file or directory using git mv."""
    if dry_run:
        logger.info(f"[DRY RUN] git mv {src} {dest}")
        return True

    dest_parent = Path(dest).parent
    if not dest_parent.exists():
        dest_parent.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(["git", "mv", "-k", str(src), str(dest)], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        # Fallback to shutil move if git fails (e.g. untracked)
        logger.warning(f"git mv failed for {src}: {e.stderr.decode().strip()}. Trying shutil.move")
        try:
            shutil.move(str(src), str(dest))
            return True
        except Exception as e2:
            logger.error(f"Failed to move {src}: {e2}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Clean up docs/ directory")
    parser.add_argument("--dry-run", action="store_true", help="Simulate moves")
    args = parser.parse_args()

    if not DOCS_DIR.exists():
        logger.error(f"Docs directory not found: {DOCS_DIR}")
        return

    # 1. Archive Root Files
    logger.info("--- Processing Root Files ---")
    for item in DOCS_DIR.iterdir():
        if item.is_file():
            if item.name in KEEP_ROOT_FILES:
                logger.info(f"Keeping root file: {item.name}")
                continue

            # Special case: Phase docs in root
            if item.name.upper().startswith("PHASE"):
                dest = ARCHIVE_DIR / "phases" / "root" / item.name
            else:
                dest = ARCHIVE_DIR / "docs_root" / item.name

            git_mv(item, dest, args.dry_run)

    # 2. Archive Directories
    logger.info("--- Processing Directories ---")
    for item in DOCS_DIR.iterdir():
        if item.is_dir():
            if item.name in PRESERVE_DIRS:
                logger.info(f"Preserving directory: {item.name}")
                continue

            # Check explicit map first
            if item.name in ARCHIVE_DIRS:
                target_sub = ARCHIVE_DIRS[item.name]
                dest = ARCHIVE_DIR / target_sub / item.name
                git_mv(item, dest, args.dry_run)
                continue

            # Handle Phase directories dynamically
            if item.name.lower().startswith("phase"):
                # Check if it looks like an old phase (simple heuristic)
                # We want to keep 27/28 if they existed as dirs (they generally don't, mostly flat files or SSOT)
                # But actual phase dirs like phase9 start with phase
                dest = ARCHIVE_DIR / "phases" / item.name
                git_mv(item, dest, args.dry_run)
                continue

            # Fallback for unknown dirs
            logger.info(f"Found unclassified directory: {item.name} -> Archiving to archive/misc")
            dest = ARCHIVE_DIR / "misc" / item.name
            git_mv(item, dest, args.dry_run)

    logger.info("Cleanup complete.")


if __name__ == "__main__":
    main()
