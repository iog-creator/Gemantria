#!/usr/bin/env python3
"""
PMS Validation Script - Comprehensive validation of PMS system health.

Validates all 3 critical information sources and reports compliance status.
Called by CI and manual verification.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parent.parent.parent


class PMSValidator:
    """Comprehensive PMS system validator."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.results: Dict[str, Any] = {}

    def validate_all(self) -> bool:
        """Run all PMS validations."""
        print("🔍 PMS SYSTEM VALIDATION")
        print("=" * 50)

        validations = [
            ("hints_envelopes", self.validate_hints_envelopes),
            ("agents_md_files", self.validate_agents_md_files),
            ("mdc_rules", self.validate_mdc_rules),
            ("metadata_enforcement", self.validate_metadata_enforcement),
            ("housekeeping_automation", self.validate_housekeeping_automation),
            ("envelope_error_system", self.validate_envelope_error_system),
        ]

        all_passed = True
        for name, validator in validations:
            print(f"\n📋 Validating {name.replace('_', ' ')}...")
            try:
                passed = validator()
                self.results[name] = passed
                if passed:
                    print(f"✅ {name.replace('_', ' ')}: PASS")
                else:
                    print(f"❌ {name.replace('_', ' ')}: FAIL")
                    all_passed = False
            except Exception as e:
                print(f"💥 {name.replace('_', ' ')}: ERROR - {e}")
                self.errors.append(f"{name}: {e}")
                all_passed = False

        self.print_summary(all_passed)
        return all_passed

    def validate_hints_envelopes(self) -> bool:
        """Validate hints envelopes exist and are properly formed."""
        envelope_dir = ROOT / "exports"
        if not envelope_dir.exists():
            self.errors.append("exports/ directory does not exist")
            return False

        envelope_files = list(envelope_dir.glob("*hints_envelope*.json"))
        if not envelope_files:
            self.warnings.append("No hints envelope files found")
            return True  # Not an error if none exist yet

        for envelope_file in envelope_files:
            try:
                with open(envelope_file, encoding="utf-8") as f:
                    envelope = json.load(f)

                # Validate structure
                required = ["type", "version", "items", "count"]
                for field in required:
                    if field not in envelope:
                        self.errors.append(f"Envelope {envelope_file.name}: missing {field}")
                        return False

                if envelope["type"] != "hints_envelope":
                    self.errors.append(f"Envelope {envelope_file.name}: wrong type")
                    return False

                if envelope["version"] != "1.0":
                    self.errors.append(f"Envelope {envelope_file.name}: wrong version")
                    return False

                if len(envelope["items"]) != envelope["count"]:
                    self.errors.append(f"Envelope {envelope_file.name}: count mismatch")
                    return False

            except Exception as e:
                self.errors.append(f"Envelope {envelope_file.name}: invalid JSON - {e}")
                return False

        return True

    def validate_agents_md_files(self) -> bool:
        """Validate AGENTS.md files exist and are properly structured."""
        required_files = [ROOT / "AGENTS.md", ROOT / "docs" / "AGENTS.md", ROOT / "src" / "AGENTS.md"]

        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(str(file_path))

        if missing_files:
            self.errors.append(f"Missing AGENTS.md files: {', '.join(missing_files)}")
            return False

        # Validate content structure
        for file_path in required_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                if "RULES_INVENTORY_START" not in content:
                    self.warnings.append(f"{file_path.name}: missing rules inventory")

                if "AGENTS.md" not in content:
                    self.warnings.append(f"{file_path.name}: missing AGENTS.md reference")

            except Exception as e:
                self.errors.append(f"Error reading {file_path}: {e}")
                return False

        return True

    def validate_mdc_rules(self) -> bool:
        """Validate .mdc rules exist and are properly formatted."""
        rules_dir = ROOT / ".cursor" / "rules"
        if not rules_dir.exists():
            self.errors.append(".cursor/rules directory does not exist")
            return False

        mdc_files = list(rules_dir.glob("*.mdc"))
        if not mdc_files:
            self.warnings.append("No .mdc rule files found")
            return True  # Not critical if none exist

        for mdc_file in mdc_files:
            try:
                with open(mdc_file, encoding="utf-8") as f:
                    content = f.read()

                # Basic validation - should have proper markdown structure
                if not content.strip().startswith("#"):
                    self.warnings.append(f"{mdc_file.name}: does not start with header")

                if "id:" not in content:
                    self.warnings.append(f"{mdc_file.name}: missing rule id")

            except Exception as e:
                self.errors.append(f"Error reading {mdc_file}: {e}")
                return False

        return True

    def validate_metadata_enforcement(self) -> bool:
        """Validate metadata enforcement system is working."""
        # Look for script in PMS directory first, then root
        metadata_script = ROOT / "pms" / "scripts" / "enforce_metadata.py"
        if not metadata_script.exists():
            metadata_script = ROOT / "scripts" / "enforce_metadata.py"
        if not metadata_script.exists():
            self.errors.append("Metadata enforcement script not found")
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(metadata_script), "--help"], capture_output=True, text=True, cwd=ROOT
            )

            if result.returncode != 0:
                self.errors.append("Metadata enforcement script failed to run")
                return False

        except Exception as e:
            self.errors.append(f"Metadata enforcement validation failed: {e}")
            return False

        return True

    def validate_housekeeping_automation(self) -> bool:
        """Validate housekeeping automation is working."""
        try:
            # Test rules audit
            result1 = subprocess.run(
                [sys.executable, "scripts/rules_audit.py"], capture_output=True, text=True, cwd=ROOT
            )

            # Test share sync
            result2 = subprocess.run(["make", "share.sync"], capture_output=True, text=True, cwd=ROOT)

            # Test forest generation
            result3 = subprocess.run(
                [sys.executable, "scripts/generate_forest.py"], capture_output=True, text=True, cwd=ROOT
            )

            if result1.returncode != 0:
                self.errors.append("Rules audit failed")
                return False

            if result2.returncode != 0:
                self.errors.append("Share sync failed")
                return False

            if result3.returncode != 0:
                self.errors.append("Forest generation failed")
                return False

        except Exception as e:
            self.errors.append(f"Housekeeping validation failed: {e}")
            return False

        return True

    def validate_envelope_error_system(self) -> bool:
        """Validate envelope error system is properly implemented."""
        error_system = ROOT / "pms" / "core" / "envelope_error_system.py"
        if not error_system.exists():
            self.errors.append("Envelope error system not found")
            return False

        try:
            # Import and test the system
            sys.path.insert(0, str(ROOT / "pms"))
            from core.envelope_error_system import EnvelopeErrorSystem

            system = EnvelopeErrorSystem()
            # Basic functionality test
            envelope = {"type": "hints_envelope", "version": "1.0", "items": ["test"], "count": 1}

            if not system._validate_envelope(envelope):
                self.errors.append("Envelope validation logic failed")
                return False

        except Exception as e:
            self.errors.append(f"Envelope error system validation failed: {e}")
            return False

        return True

    def print_summary(self, all_passed: bool):
        """Print validation summary."""
        print("\n" + "=" * 50)
        print("📊 PMS VALIDATION SUMMARY")
        print("=" * 50)

        if all_passed:
            print("🎉 ALL PMS VALIDATIONS PASSED!")
        else:
            print("❌ PMS VALIDATIONS FAILED!")

        print(f"\n✅ Passed: {sum(1 for v in self.results.values() if v)}")
        print(f"❌ Failed: {sum(1 for v in self.results.values() if not v)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"💥 Errors: {len(self.errors)}")

        if self.errors:
            print("\n💥 CRITICAL ERRORS:")
            for error in self.errors:
                print(f"  ❌ {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")

        print(f"\n🏁 PMS Status: {'HEALTHY' if all_passed else 'NEEDS ATTENTION'}")


def main():
    """Main entry point."""
    validator = PMSValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
