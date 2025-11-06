#!/usr/bin/env python3
"""
Envelope processor for PMS - handles hints envelopes with imperative commands.

Processes hints envelopes and executes imperative commands that agents cannot ignore.
Called automatically from pipeline and manual enforcement.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parent.parent


def load_envelope(envelope_path: Path) -> Dict[str, Any]:
    """Load a hints envelope from file."""
    try:
        with open(envelope_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load envelope {envelope_path}: {e}")
        return {}


def find_envelope_files() -> List[Path]:
    """Find all hints envelope files in the project."""
    envelopes = []
    # Look in exports/ and any envelope directories
    for pattern in ["exports/graph_latest.json", "**/envelopes/*.json", "**/*envelope*.json"]:
        for path in ROOT.glob(pattern):
            if path.is_file():
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("type") == "hints_envelope":
                            envelopes.append(path)
                except:
                    pass
    return envelopes


def execute_imperative_command(command: str, envelope: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an imperative command from hints envelope."""

    if command == "AGENT_STOP_AND_PAY_ATTENTION":
        print("🚨 IMPERATIVE: Agent must stop and pay attention to this envelope")
        return {"status": "acknowledged", "command": command}

    elif command == "PROCESS_HINTS_ENVELOPE_IMMEDIATELY":
        print("⚡ IMPERATIVE: Processing hints envelope immediately")
        # Process all hints in envelope
        hints = envelope.get("items", [])
        for hint in hints:
            print(f"📝 Processing hint: {hint}")
        return {"status": "processed", "hints_processed": len(hints)}

    elif command == "CHECK_METADATA_REQUIREMENTS":
        print("🔍 IMPERATIVE: Checking metadata requirements")
        try:
            result = subprocess.run(
                [sys.executable, "scripts/enforce_metadata.py", "--staged", "--fix"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ Metadata requirements satisfied")
                return {"status": "success", "command": command}
            else:
                print("❌ Metadata requirements failed")
                return {
                    "status": "error",
                    "command": command,
                    "error": "METADATA_REQUIREMENTS_FAILED",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
        except Exception as e:
            return {"status": "error", "command": command, "error": str(e)}

    elif command == "VALIDATE_ENVELOPE_CONTENTS":
        print("✅ IMPERATIVE: Validating envelope contents")
        required_fields = ["type", "version", "items", "count", "imperative_commands"]
        missing = [field for field in required_fields if field not in envelope]

        if missing:
            return {"status": "error", "command": command, "error": "INVALID_ENVELOPE", "missing_fields": missing}

        # Validate counts match
        if len(envelope.get("items", [])) != envelope.get("count", 0):
            return {"status": "error", "command": command, "error": "ENVELOPE_COUNT_MISMATCH"}

        return {"status": "valid", "command": command}

    else:
        return {"status": "error", "command": command, "error": "UNKNOWN_COMMAND"}


def process_envelope(envelope: Dict[str, Any]) -> Dict[str, Any]:
    """Process a complete hints envelope."""
    print(f"🎯 Processing hints envelope v{envelope.get('version', 'unknown')}")

    results = []
    imperative_commands = envelope.get("imperative_commands", [])

    if not imperative_commands:
        return {"status": "warning", "message": "No imperative commands found in envelope"}

    # Execute each imperative command
    for command in imperative_commands:
        print(f"🔧 Executing imperative command: {command}")
        result = execute_imperative_command(command, envelope)
        results.append(result)

        # Check enforcement level
        enforcement_level = envelope.get("enforcement_level", "normal")
        ignore_risk = envelope.get("ignore_risk", "none")

        if enforcement_level == "CRITICAL" and result.get("status") == "error":
            print(f"🚨 CRITICAL ENFORCEMENT: {ignore_risk}")
            # In critical mode, errors should cause pipeline abort
            return {
                "status": "critical_failure",
                "message": f"Critical envelope command failed: {command}",
                "ignore_risk": ignore_risk,
                "command_results": results,
            }

    return {"status": "completed", "commands_executed": len(results), "results": results}


def main():
    parser = argparse.ArgumentParser(description="Process hints envelopes")
    parser.add_argument("--file", help="Specific envelope file to process")
    parser.add_argument("--process-pending", action="store_true", help="Process all pending envelopes")
    parser.add_argument("--create-test-envelope", action="store_true", help="Create a test envelope")

    args = parser.parse_args()

    if args.create_test_envelope:
        # Create a test envelope for demonstration
        test_envelope = {
            "type": "hints_envelope",
            "version": "1.0",
            "items": ["Pipeline completed successfully", "Metadata validation recommended"],
            "count": 2,
            "imperative_commands": [
                "AGENT_STOP_AND_PAY_ATTENTION",
                "PROCESS_HINTS_ENVELOPE_IMMEDIATELY",
                "CHECK_METADATA_REQUIREMENTS",
                "VALIDATE_ENVELOPE_CONTENTS",
            ],
            "enforcement_level": "CRITICAL",
            "ignore_risk": "PIPELINE_ABORT",
        }

        envelope_path = ROOT / "exports" / "test_envelope.json"
        envelope_path.parent.mkdir(exist_ok=True)
        with open(envelope_path, "w", encoding="utf-8") as f:
            json.dump(test_envelope, f, indent=2)

        print(f"✅ Created test envelope: {envelope_path}")
        return 0

    if args.file:
        # Process specific file
        envelope_path = Path(args.file)
        if not envelope_path.exists():
            envelope_path = ROOT / envelope_path

        envelope = load_envelope(envelope_path)
        if not envelope:
            print(f"❌ Failed to load envelope: {envelope_path}")
            return 1

        result = process_envelope(envelope)
        print(f"📊 Result: {result.get('status', 'unknown')}")

        if result.get("status") == "critical_failure":
            print("🚨 CRITICAL FAILURE - Pipeline should abort")
            return 1

        return 0

    elif args.process_pending:
        # Process all pending envelopes
        envelopes = find_envelope_files()
        if not envelopes:
            print("ℹ️ No pending envelopes found")
            return 0

        print(f"📋 Found {len(envelopes)} envelope(s) to process")

        critical_failures = 0
        for envelope_path in envelopes:
            print(f"\n🔄 Processing: {envelope_path}")
            envelope = load_envelope(envelope_path)
            if envelope:
                result = process_envelope(envelope)
                if result.get("status") == "critical_failure":
                    critical_failures += 1

        if critical_failures > 0:
            print(f"\n🚨 {critical_failures} critical failure(s) detected")
            return 1

        print("✅ All envelopes processed successfully")
        return 0

    else:
        print("Use --file, --process-pending, or --create-test-envelope")
        return 1


if __name__ == "__main__":
    exit(main())
