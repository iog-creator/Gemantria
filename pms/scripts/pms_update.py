#!/usr/bin/env python3
"""
PMS Update System - Safely update PMS to latest version.

Checks for updates, validates compatibility, and applies changes.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


class PMSUpdater:
    """Handles PMS system updates."""

    PMS_VERSION_FILE = ROOT / "pms" / "VERSION"
    BACKUP_DIR = ROOT / "backups" / "pms_updates"

    def __init__(self):
        self.current_version = self._get_current_version()
        self.backup_dir = None

    def _get_current_version(self) -> str:
        """Get current PMS version."""
        if self.PMS_VERSION_FILE.exists():
            return self.PMS_VERSION_FILE.read_text().strip()
        return "unknown"

    def check_for_updates(self) -> str | None:
        """Check if updates are available."""
        # For now, just check if we're running the latest known version
        # In production, this would check a remote repository
        latest_version = "2.0.0"  # Current version
        if self.current_version != latest_version:
            return latest_version
        return None

    def create_backup(self) -> Path:
        """Create backup of current PMS system."""
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = subprocess.run(["date", "+%Y%m%d_%H%M%S"], capture_output=True, text=True).stdout.strip()

        backup_path = self.BACKUP_DIR / f"pms_backup_{timestamp}"
        backup_path.mkdir()

        # Backup PMS directory
        if (ROOT / "pms").exists():
            shutil.copytree(ROOT / "pms", backup_path / "pms")

        # Backup configuration files
        config_files = ["PROJECT_MASTER_PLAN.md", "AGENTS.md", ".cursor/rules/", "Makefile"]

        for config in config_files:
            src = ROOT / config
            if src.exists():
                dst = backup_path / config
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.is_file():
                    shutil.copy2(src, dst)
                else:
                    shutil.copytree(src, dst, dirs_exist_ok=True)

        self.backup_dir = backup_path
        print(f"✅ Backup created: {backup_path}")
        return backup_path

    def validate_system_health(self) -> bool:
        """Validate that PMS system is healthy before update."""
        try:
            result = subprocess.run(
                [sys.executable, "pms/scripts/validate_pms.py"], cwd=ROOT, capture_output=True, text=True
            )

            return result.returncode == 0
        except Exception as e:
            print(f"❌ System validation failed: {e}")
            return False

    def apply_update(self, new_version: str) -> bool:
        """Apply PMS update."""
        print(f"⬆️ Updating PMS from {self.current_version} to {new_version}")

        # For now, this is a placeholder for actual update logic
        # In production, this would download and apply updates from a repository

        # Update version file
        self.PMS_VERSION_FILE.write_text(new_version)

        print(f"✅ PMS updated to version {new_version}")
        return True

    def rollback(self) -> bool:
        """Rollback to previous version using backup."""
        if not self.backup_dir or not self.backup_dir.exists():
            print("❌ No backup available for rollback")
            return False

        print(f"🔄 Rolling back using backup: {self.backup_dir}")

        try:
            # Restore PMS directory
            pms_backup = self.backup_dir / "pms"
            if pms_backup.exists():
                pms_target = ROOT / "pms"
                if pms_target.exists():
                    shutil.rmtree(pms_target)
                shutil.copytree(pms_backup, pms_target)

            # Restore configuration files
            config_files = ["PROJECT_MASTER_PLAN.md", "AGENTS.md", ".cursor/rules/", "Makefile"]

            for config in config_files:
                backup_src = self.backup_dir / config
                target = ROOT / config
                if backup_src.exists():
                    if target.exists():
                        if target.is_file():
                            os.remove(target)
                        else:
                            shutil.rmtree(target)
                    if backup_src.is_file():
                        shutil.copy2(backup_src, target)
                    else:
                        shutil.copytree(backup_src, target, dirs_exist_ok=True)

            print("✅ Rollback completed successfully")
            return True

        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

    def run_post_update_checks(self) -> bool:
        """Run checks after update to ensure everything works."""
        print("🔍 Running post-update checks...")

        # Validate system
        if not self.validate_system_health():
            print("❌ Post-update validation failed")
            return False

        # Test housekeeping
        try:
            result = subprocess.run(["make", "housekeeping"], cwd=ROOT, capture_output=True, text=True)

            if result.returncode != 0:
                print("❌ Housekeeping test failed")
                return False

        except Exception as e:
            print(f"❌ Housekeeping test error: {e}")
            return False

        print("✅ Post-update checks passed")
        return True

    def update(self) -> bool:
        """Perform complete PMS update."""
        print("🚀 Starting PMS Update Process")
        print("=" * 40)

        # Check for updates
        new_version = self.check_for_updates()
        if not new_version:
            print("✅ PMS is already up to date")
            return True

        print(f"📦 Update available: {self.current_version} → {new_version}")

        # Validate system health
        if not self.validate_system_health():
            print("❌ System health check failed - aborting update")
            return False

        # Create backup
        try:
            self.create_backup()
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return False

        # Apply update
        try:
            if not self.apply_update(new_version):
                print("❌ Update application failed")
                print("🔄 Attempting rollback...")
                self.rollback()
                return False
        except Exception as e:
            print(f"❌ Update failed: {e}")
            print("🔄 Attempting rollback...")
            self.rollback()
            return False

        # Run post-update checks
        if not self.run_post_update_checks():
            print("❌ Post-update checks failed")
            print("🔄 Attempting rollback...")
            self.rollback()
            return False

        print("🎉 PMS update completed successfully!")
        print(f"📋 Backup available at: {self.backup_dir}")
        return True


def main():
    """Main entry point."""
    updater = PMSUpdater()
    success = updater.update()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
