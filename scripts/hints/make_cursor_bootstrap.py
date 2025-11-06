#!/usr/bin/env python3

import json, time, os

envelope = {
    "type": "hints_envelope",
    "version": 1,
    "commands": ["AGENT_STOP_AND_PAY_ATTENTION", "PROCESS_HINTS_ENVELOPE_IMMEDIATELY", "ENFORCE_PROJECT_GOVERNANCE"],
    "read_these_first": [
        ".cursor/rules/000-ssot-index.mdc",
        "RULES_INDEX.md",
        "AGENTS.md",
        "src/graph/AGENTS.md",
        "src/nodes/AGENTS.md",
        ".cursor/rules/050-ops-contract.mdc",
        ".cursor/rules/051-cursor-insight.mdc",
        ".cursor/rules/052-tool-priority.mdc",
        ".cursor/rules/060-pipeline-sequence.mdc",
    ],
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}

os.makedirs("exports", exist_ok=True)
with open("exports/hints_envelope.cursor.json", "w", encoding="utf-8") as f:
    json.dump(envelope, f, indent=2)

print("Wrote exports/hints_envelope.cursor.json")
