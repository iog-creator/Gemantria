#!/usr/bin/env python3
"""
Guard: OA Reasoning Bridge Coherence (Phase 27.F)

Ensures that:
1. docs/SSOT/oa/OA_REASONING_BRIDGE.md matches code in pmagent/oa/reasoning_bridge.py
2. OA State (share/orchestrator_assistant/STATE.json) correctly reflects the bridge scaffolding.

Usage:
    python scripts/guards/guard_oa_reasoning_bridge.py --mode [STRICT|HINT]
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    from pmagent.oa.reasoning_bridge import PROGRAM_IDS
except ImportError:
    PROGRAM_IDS = set()
    print("WARNING: Could not import pmagent.oa.reasoning_bridge", file=sys.stderr)


# Paths
DOC_PATH = ROOT / "docs" / "SSOT" / "oa" / "OA_REASONING_BRIDGE.md"
STATE_PATH = ROOT / "share" / "orchestrator_assistant" / "STATE.json"


def check_coherence(strict: bool = False) -> dict:
    issues = []

    # 1. Check Doc Existence
    if not DOC_PATH.exists():
        issues.append("Missing SSOT doc: docs/SSOT/oa/OA_REASONING_BRIDGE.md")

    # 2. Check Code vs Doc (Program IDs)
    # Simple grep-like check on doc content for program IDs
    if DOC_PATH.exists():
        doc_content = DOC_PATH.read_text()
        for pid in PROGRAM_IDS:
            if pid not in doc_content:
                issues.append(f"Program ID '{pid}' defined in code but missing from SSOT doc")

    # 3. Check OA State
    if not STATE_PATH.exists():
        issues.append("Missing OA State: share/orchestrator_assistant/STATE.json")
    else:
        try:
            state = json.loads(STATE_PATH.read_text())
            bridge_meta = state.get("reasoning_bridge", {})

            if not bridge_meta:
                issues.append("OA State missing 'reasoning_bridge' section")
            else:
                state_programs = set(bridge_meta.get("programs", []))

                # Check alignment: Code vs State
                missing_in_state = PROGRAM_IDS - state_programs
                extra_in_state = state_programs - PROGRAM_IDS

                if missing_in_state:
                    issues.append(f"OA State missing programs defined in code: {missing_in_state}")
                if extra_in_state:
                    issues.append(f"OA State has extra programs not in code: {extra_in_state}")

                if bridge_meta.get("implementation_status") != "DESIGN_ONLY":
                    issues.append("OA State implementation_status should be 'DESIGN_ONLY' for Phase 27.F")

        except json.JSONDecodeError:
            issues.append("Invalid JSON in OA State file")

    return {"ok": len(issues) == 0, "issues": issues, "mode": "STRICT" if strict else "HINT"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["STRICT", "HINT"], default="HINT")
    args = parser.parse_args()

    # Always HINT for this batch unless otherwise specified, but guard supports STRICT
    strict = args.mode == "STRICT"

    result = check_coherence(strict)

    print(json.dumps(result, indent=2))

    if not result["ok"] and strict:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
