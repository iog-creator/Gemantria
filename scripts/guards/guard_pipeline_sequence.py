#!/usr/bin/env python3
"""
Static guard to verify canonical node order in src/graph/graph.py.
Does NOT depend on a main() symbol; scans the file content only.
"""

import re, sys, pathlib

ORDER = [
    "collect_nouns_node",
    "validate_batch_node",
    "enrichment_node",
    "confidence_validator_node",
    "network_aggregator_node",
    "schema_validator_node",
    "analysis_runner_node",
    "wrap_hints_node",
]

p = pathlib.Path("src/graph/graph.py").read_text(encoding="utf-8")

# Find the run_pipeline function
run_pipeline_start = p.find("def run_pipeline(")
if run_pipeline_start == -1:
    print("ERROR: run_pipeline function not found", file=sys.stderr)
    sys.exit(2)

# Find the end of run_pipeline (next def or end of file)
run_pipeline_end = p.find("\ndef ", run_pipeline_start + 1)
if run_pipeline_end == -1:
    run_pipeline_end = len(p)

run_pipeline_content = p[run_pipeline_start:run_pipeline_end]

idxs = []
for name in ORDER:
    m = list(re.finditer(rf"\b{name}\b", run_pipeline_content))
    if not m:
        print(f"ERROR: missing node call: {name}", file=sys.stderr)
        sys.exit(2)
    idxs.append(m[0].start())

if idxs != sorted(idxs):
    print("ERROR: pipeline nodes out of order", file=sys.stderr)
    sys.exit(2)

print("OK: pipeline sequence present and ordered.")
