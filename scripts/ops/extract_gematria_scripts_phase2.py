#!/usr/bin/env python3
"""
Extraction Script: Gematria Scripts Phase 2
===========================================
Moves Gematria-related scripts from scripts/ to agentpm/modules/gematria/scripts/.

Phase 2 targets:
- scripts/ai_noun_discovery.py
- scripts/math_verifier.py
- scripts/extract_nouns_from_bible_db.py
- scripts/gematria_verify.py (if exists)

This script:
1. Creates agentpm/modules/gematria/scripts/ directory
2. Moves scripts to new location
3. Updates imports if needed
4. Creates __init__.py in scripts directory
"""

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TARGET_DIR = REPO_ROOT / "agentpm" / "modules" / "gematria" / "scripts"

# Scripts to move (source -> target name)
SCRIPTS_TO_MOVE = [
    ("scripts/ai_noun_discovery.py", "ai_noun_discovery.py"),
    ("scripts/math_verifier.py", "math_verifier.py"),
    ("scripts/extract_nouns_from_bible_db.py", "extract_nouns_from_bible_db.py"),
    ("scripts/gematria_verify.py", "gematria_verify.py"),  # May not exist
]


def move_script(source_path: Path, target_name: str) -> bool:
    """Move a script file to the target directory."""
    if not source_path.exists():
        print(f"⚠️  {source_path.relative_to(REPO_ROOT)}: Not found (skipping)")
        return False

    target_path = TARGET_DIR / target_name

    try:
        # Copy file
        shutil.copy2(source_path, target_path)
        print(f"✅ Moved: {source_path.relative_to(REPO_ROOT)} -> {target_path.relative_to(REPO_ROOT)}")
        return True
    except Exception as e:
        print(f"❌ Error moving {source_path}: {e}")
        return False


def create_init_file():
    """Create __init__.py in scripts directory."""
    init_file = TARGET_DIR / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Gematria module scripts."""\n')
        print(f"✅ Created: {init_file.relative_to(REPO_ROOT)}")


def main():
    """Main extraction function."""
    print("🔍 Gematria Scripts Phase 2 Extraction")
    print("=" * 60)
    print()

    # Create target directory
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Target directory: {TARGET_DIR.relative_to(REPO_ROOT)}")
    print()

    # Create __init__.py
    create_init_file()
    print()

    # Move scripts
    moved_count = 0
    for source_rel, target_name in SCRIPTS_TO_MOVE:
        source_path = REPO_ROOT / source_rel
        if move_script(source_path, target_name):
            moved_count += 1
        print()

    print("=" * 60)
    print(f"✅ Phase 2 extraction complete: {moved_count} scripts moved")
    print()
    print("📝 Next steps:")
    print("   1. Update Makefile targets to reference new script locations")
    print("   2. Update any other references to moved scripts")
    print("   3. Run 'make book.smoke' to verify pipeline still works")
    print()
    print("⚠️  Note: Original scripts in scripts/ are preserved as copies.")
    print("   Remove them after verifying Makefile targets work correctly.")

    return 0 if moved_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
