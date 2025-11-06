#!/usr/bin/env python3
"""
Generate a runtime hints envelope for pipeline node sequence enforcement.

Related Rules: Rule-060 (Pipeline Node Sequence)
"""

import json
import time
from pathlib import Path

envelope = {
    "type": "hints_envelope",
    "version": 1,
    "commands": [
        "AGENT_STOP_AND_PAY_ATTENTION",
        "PROCESS_HINTS_ENVELOPE_IMMEDIATELY",
    ],
    "expected_node_sequence": [
        "collect_nouns",
        "validate_batch",
        "enrichment",
        "confidence_validator",
        "network_aggregator",
        "schema_validator",
        "analysis_runner",
        "wrap_hints",
    ],
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}

# Ensure exports directory exists
exports_dir = Path("exports")
exports_dir.mkdir(exist_ok=True)

output_file = exports_dir / "hints_envelope.pipeline.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(envelope, f, indent=2)

print(f"Wrote {output_file}")
