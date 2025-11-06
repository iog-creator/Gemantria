#!/usr/bin/env python3
"""
PMS Recovery System - Diagnose and fix PMS installation issues.

Automatically detects problems and applies fixes.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent.parent


class PMSRecovery:
    """Handles PMS system recovery and repair."""

    def __init__(self):
        self.issues: List[str] = []
        self.fixes_applied: List[str] = []

    def diagnose(self) -> bool:
        """Diagnose PMS system for issues."""
        print("🔍 Diagnosing PMS system...")
        print("=" * 40)

        checks = [
            self.check_pms_directory,
            self.check_core_components,
            self.check_scripts_executable,
            self.check_templates_exist,
            self.check_agents_md_files,
            self.check_rules_directory,
            self.check_makefile_integration,
            self.check_python_dependencies,
        ]

        all_good = True
        for check in checks:
            try:
                if not check():
                    all_good = False
            except Exception as e:
                print(f"💥 Check failed with error: {e}")
                all_good = False

        print("\n📋 Diagnosis Summary:")
        if self.issues:
            print("❌ Issues found:")
            for issue in self.issues:
                print(f"  - {issue}")
        else:
            print("✅ No issues detected")

        return all_good

    def check_pms_directory(self) -> bool:
        """Check if PMS directory exists."""
        if not (ROOT / "pms").exists():
            self.issues.append("PMS directory not found")
            return False
        return True

    def check_core_components(self) -> bool:
        """Check core PMS components."""
        core_files = [
            "pms/core/envelope_error_system.py",
            "pms/scripts/validate_pms.py",
            "pms/docs/PROJECT_MANAGEMENT_SYSTEM_SPEC.md",
        ]

        missing = []
        for file_path in core_files:
            if not (ROOT / file_path).exists():
                missing.append(file_path)

        if missing:
            self.issues.append(f"Missing core components: {', '.join(missing)}")
            return False
        return True

    def check_scripts_executable(self) -> bool:
        """Check that PMS scripts are executable."""
        scripts = [
            "pms/scripts/validate_pms.py",
            "pms/scripts/envelope_processor.py",
            "pms/scripts/enforce_metadata.py",
        ]

        for script in scripts:
            script_path = ROOT / script
            if script_path.exists():
                # Check shebang
                with open(script_path) as f:
                    first_line = f.readline().strip()
                    if not first_line.startswith("#!/usr/bin/env python3"):
                        self.issues.append(f"{script}: missing or incorrect shebang")
                        return False
            else:
                self.issues.append(f"Script not found: {script}")
                return False
        return True

    def check_templates_exist(self) -> bool:
        """Check that templates exist."""
        templates = [
            "pms/templates/PROJECT_MASTER_PLAN.template.md",
            "pms/templates/Makefile.pms",
            "pms/templates/AGENTS.md.template",
        ]

        missing = []
        for template in templates:
            if not (ROOT / template).exists():
                missing.append(template)

        if missing:
            self.issues.append(f"Missing templates: {', '.join(missing)}")
            return False
        return True

    def check_agents_md_files(self) -> bool:
        """Check AGENTS.md files exist."""
        required_files = [ROOT / "AGENTS.md", ROOT / "docs" / "AGENTS.md", ROOT / "src" / "AGENTS.md"]

        missing = []
        for file_path in required_files:
            if not file_path.exists():
                missing.append(str(file_path))

        if missing:
            self.issues.append(f"Missing AGENTS.md files: {', '.join(missing)}")
            return False
        return True

    def check_rules_directory(self) -> bool:
        """Check Cursor rules directory."""
        rules_dir = ROOT / ".cursor" / "rules"
        if not rules_dir.exists():
            self.issues.append("Cursor rules directory not found")
            return False
        return True

    def check_makefile_integration(self) -> bool:
        """Check Makefile includes PMS targets."""
        makefile = ROOT / "Makefile"
        if not makefile.exists():
            self.issues.append("Makefile not found")
            return False

        with open(makefile) as f:
            content = f.read()

        if "include pms/templates/Makefile.pms" not in content:
            self.issues.append("Makefile does not include PMS targets")
            return False
        return True

    def check_python_dependencies(self) -> bool:
        """Check Python dependencies are available."""
        try:
            import json
            import os
            import subprocess
            import sys
            from pathlib import Path

            return True
        except ImportError as e:
            self.issues.append(f"Missing Python dependency: {e}")
            return False

    def apply_fixes(self) -> bool:
        """Apply fixes for detected issues."""
        print("\n🔧 Applying fixes...")
        print("=" * 40)

        fixes_applied = []

        # Fix 1: Create missing AGENTS.md files
        if any("AGENTS.md" in issue for issue in self.issues):
            self._fix_missing_agents_md()
            fixes_applied.append("Created missing AGENTS.md files")

        # Fix 2: Fix Makefile integration
        if any("Makefile" in issue for issue in self.issues):
            self._fix_makefile_integration()
            fixes_applied.append("Fixed Makefile integration")

        # Fix 3: Create missing directories
        self._fix_missing_directories()
        fixes_applied.append("Created missing directories")

        # Fix 4: Set script permissions
        self._fix_script_permissions()
        fixes_applied.append("Fixed script permissions")

        self.fixes_applied = fixes_applied

        if fixes_applied:
            print("✅ Fixes applied:")
            for fix in fixes_applied:
                print(f"  - {fix}")
        else:
            print("ℹ️  No fixes needed")

        return True

    def _fix_missing_agents_md(self):
        """Create missing AGENTS.md files."""
        template = ROOT / "pms" / "templates" / "AGENTS.md.template"
        if not template.exists():
            return

        required_files = [ROOT / "AGENTS.md", ROOT / "docs" / "AGENTS.md", ROOT / "src" / "AGENTS.md"]

        for file_path in required_files:
            if not file_path.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(template, file_path)
                print(f"  Created: {file_path}")

    def _fix_makefile_integration(self):
        """Fix Makefile to include PMS targets."""
        makefile = ROOT / "Makefile"
        if not makefile.exists():
            # Create basic Makefile
            with open(makefile, "w") as f:
                f.write("# Project Makefile\n\n")
                f.write("# Include PMS targets\n")
                f.write("include pms/templates/Makefile.pms\n\n")
                f.write("# Add your targets here\n")
            print(f"  Created: {makefile}")
        else:
            # Add include if not present
            with open(makefile) as f:
                content = f.read()

            if "include pms/templates/Makefile.pms" not in content:
                with open(makefile, "a") as f:
                    f.write("\n# Include PMS targets\n")
                    f.write("include pms/templates/Makefile.pms\n")
                print(f"  Updated: {makefile}")

    def _fix_missing_directories(self):
        """Create missing directories."""
        directories = [ROOT / "exports", ROOT / ".cursor" / "rules", ROOT / "docs" / "ADRs", ROOT / "src"]

        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                print(f"  Created: {directory}")

    def _fix_script_permissions(self):
        """Ensure scripts have execute permissions."""
        scripts = [
            "pms/scripts/validate_pms.py",
            "pms/scripts/envelope_processor.py",
            "pms/scripts/enforce_metadata.py",
            "pms/scripts/pms_init.py",
            "pms/scripts/pms_update.py",
            "pms/scripts/pms_recover.py",
        ]

        for script in scripts:
            script_path = ROOT / script
            if script_path.exists():
                os.chmod(script_path, 0o755)

    def validate_fixes(self) -> bool:
        """Validate that fixes resolved issues."""
        print("\n🔍 Validating fixes...")
        print("=" * 40)

        # Re-run diagnosis
        self.issues = []
        if not self.diagnose():
            print("❌ Some issues remain after fixes")
            return False

        print("✅ All fixes validated successfully")
        return True

    def recover(self) -> bool:
        """Perform complete PMS recovery."""
        print("🚑 Starting PMS Recovery Process")
        print("=" * 40)

        # Step 1: Diagnose
        if not self.diagnose():
            print("📋 Issues detected, attempting recovery...")
        else:
            print("✅ PMS system appears healthy")
            return True

        # Step 2: Apply fixes
        if not self.apply_fixes():
            print("❌ Failed to apply fixes")
            return False

        # Step 3: Validate fixes
        if not self.validate_fixes():
            print("❌ Fix validation failed")
            return False

        # Step 4: Run final validation
        try:
            result = subprocess.run(
                [sys.executable, "pms/scripts/validate_pms.py"], cwd=ROOT, capture_output=True, text=True
            )

            if result.returncode != 0:
                print("❌ Final PMS validation failed")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False

        except Exception as e:
            print(f"❌ Final validation error: {e}")
            return False

        print("🎉 PMS recovery completed successfully!")
        return True


def main():
    """Main entry point."""
    recovery = PMSRecovery()
    success = recovery.recover()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
