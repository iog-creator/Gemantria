#!/usr/bin/env python3
"""
Envelope Error System - Critical enforcement of imperative commands.

This system ensures that hints envelopes with imperative commands are processed
and their commands executed. Agents cannot ignore these commands.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Set

ROOT = Path(__file__).resolve().parent.parent.parent


class EnvelopeErrorSystem:
    """Critical envelope error system that agents cannot ignore."""

    IMPERATIVE_COMMANDS = {
        "AGENT_STOP_AND_PAY_ATTENTION",
        "PROCESS_HINTS_ENVELOPE_IMMEDIATELY",
        "CHECK_METADATA_REQUIREMENTS",
        "VALIDATE_ENVELOPE_CONTENTS",
        "ENFORCE_PROJECT_GOVERNANCE",
        "ABORT_IF_CRITICAL_ISSUES",
    }

    def __init__(self):
        self.processed_envelopes: Set[str] = set()
        self.errors: List[str] = []

    def load_envelope(self, envelope_path: Path) -> Dict[str, Any]:
        """Load and validate envelope structure."""
        try:
            with open(envelope_path, encoding="utf-8") as f:
                envelope = json.load(f)

            # Validate envelope structure
            if not self._validate_envelope(envelope):
                self.errors.append(f"Invalid envelope structure: {envelope_path}")
                return {}

            return envelope

        except Exception as e:
            self.errors.append(f"Failed to load envelope {envelope_path}: {e}")
            return {}

    def _validate_envelope(self, envelope: Dict[str, Any]) -> bool:
        """Validate envelope has required structure."""
        required_fields = ["type", "version", "items", "count"]
        for field in required_fields:
            if field not in envelope:
                return False

        if envelope.get("type") != "hints_envelope":
            return False

        if envelope.get("version") != "1.0":
            return False

        return True

    def has_imperative_commands(self, envelope: Dict[str, Any]) -> bool:
        """Check if envelope contains imperative commands."""
        commands = envelope.get("imperative_commands", [])
        return bool(commands and any(cmd in self.IMPERATIVE_COMMANDS for cmd in commands))

    def execute_imperative_commands(self, envelope: Dict[str, Any], envelope_path: Path) -> bool:
        """Execute all imperative commands in the envelope."""
        commands = envelope.get("imperative_commands", [])
        success = True

        for command in commands:
            if command in self.IMPERATIVE_COMMANDS:
                print(f"🔴 EXECUTING IMPERATIVE COMMAND: {command}")
                success &= self._execute_command(command, envelope, envelope_path)
            else:
                print(f"⚠️  Unknown imperative command: {command}")

        return success

    def _execute_command(self, command: str, envelope: Dict[str, Any], envelope_path: Path) -> bool:
        """Execute a specific imperative command."""
        try:
            if command == "AGENT_STOP_AND_PAY_ATTENTION":
                print("🛑 AGENT STOPPING FOR CRITICAL ENVELOPE PROCESSING")
                return True

            elif command == "PROCESS_HINTS_ENVELOPE_IMMEDIATELY":
                print("⚡ PROCESSING HINTS ENVELOPE IMMEDIATELY")
                return self._process_hints(envelope)

            elif command == "CHECK_METADATA_REQUIREMENTS":
                print("📋 CHECKING METADATA REQUIREMENTS")
                return self._check_metadata_requirements()

            elif command == "VALIDATE_ENVELOPE_CONTENTS":
                print("🔍 VALIDATING ENVELOPE CONTENTS")
                return self._validate_envelope_contents(envelope)

            elif command == "ENFORCE_PROJECT_GOVERNANCE":
                print("🏛️ ENFORCING PROJECT GOVERNANCE")
                return self._enforce_governance()

            elif command == "ABORT_IF_CRITICAL_ISSUES":
                print("💀 CHECKING FOR CRITICAL ISSUES")
                return self._abort_if_critical_issues()

        except Exception as e:
            print(f"❌ Error executing command {command}: {e}")
            return False

        return True

    def _process_hints(self, envelope: Dict[str, Any]) -> bool:
        """Process all hints in the envelope."""
        hints = envelope.get("items", [])
        for hint in hints:
            print(f"💡 Processing hint: {hint}")
        return True

    def _check_metadata_requirements(self) -> bool:
        """Check that all files have required metadata."""
        try:
            result = subprocess.run(
                [sys.executable, "pms/scripts/enforce_metadata.py", "--staged"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"❌ Metadata check failed: {result.stderr}")
                return False

            print("✅ Metadata requirements satisfied")
            return True

        except Exception as e:
            print(f"❌ Metadata check error: {e}")
            return False

    def _validate_envelope_contents(self, envelope: Dict[str, Any]) -> bool:
        """Validate envelope contents are properly formed."""
        # Check for required fields
        required = ["type", "version", "items", "count"]
        for field in required:
            if field not in envelope:
                print(f"❌ Missing required field: {field}")
                return False

        # Check count matches items length
        if len(envelope.get("items", [])) != envelope.get("count", 0):
            print("❌ Item count mismatch")
            return False

        print("✅ Envelope contents valid")
        return True

    def _enforce_governance(self) -> bool:
        """Enforce project governance rules."""
        try:
            # Run rules audit
            result1 = subprocess.run(
                [sys.executable, "scripts/rules_audit.py"], cwd=ROOT, capture_output=True, text=True
            )

            # Run housekeeping
            result2 = subprocess.run(["make", "housekeeping"], cwd=ROOT, capture_output=True, text=True)

            success = result1.returncode == 0 and result2.returncode == 0
            if success:
                print("✅ Governance enforced")
            else:
                print("❌ Governance enforcement failed")
            return success

        except Exception as e:
            print(f"❌ Governance enforcement error: {e}")
            return False

    def _abort_if_critical_issues(self) -> bool:
        """Abort pipeline if critical issues found."""
        if self.errors:
            print("💀 CRITICAL ISSUES DETECTED - ABORTING:")
            for error in self.errors:
                print(f"  ❌ {error}")
            return False

        print("✅ No critical issues detected")
        return True

    def process_envelope_file(self, envelope_path: Path) -> bool:
        """Process a single envelope file."""
        envelope_id = str(envelope_path.relative_to(ROOT))

        if envelope_id in self.processed_envelopes:
            print(f"⏭️  Envelope already processed: {envelope_id}")
            return True

        print(f"📬 Processing envelope: {envelope_id}")

        envelope = self.load_envelope(envelope_path)
        if not envelope:
            return False

        if not self.has_imperative_commands(envelope):
            print("ℹ️  No imperative commands in envelope")
            return True

        success = self.execute_imperative_commands(envelope, envelope_path)
        if success:
            self.processed_envelopes.add(envelope_id)
            print(f"✅ Envelope processed successfully: {envelope_id}")

        return success


def main():
    """Main entry point for envelope error system."""
    system = EnvelopeErrorSystem()

    # Find and process all envelope files
    envelope_dir = ROOT / "exports"
    if envelope_dir.exists():
        for envelope_file in envelope_dir.glob("*hints_envelope*.json"):
            system.process_envelope_file(envelope_file)

    # Check for errors
    if system.errors:
        print("\n💀 ENVELOPE PROCESSING ERRORS:")
        for error in system.errors:
            print(f"  ❌ {error}")
        sys.exit(1)

    print("\n✅ All envelopes processed successfully")


if __name__ == "__main__":
    main()
