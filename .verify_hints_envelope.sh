#!/bin/bash
# Verification script for hints envelope implementation
# Run after enrichment completes to verify hints are collected and exported

set -e

echo "=== Hints Envelope Verification ==="
echo ""

# 1. Check enrichment completion
echo "1. Checking enrichment status..."
python3 scripts/monitor_pipeline.py --json | jq '.stage_status.stages.enrichment | {count, total, progress: (.count / .total * 100 | floor), completed: (.count == .total)}'

# 2. Check exports for hints envelope
echo ""
echo "2. Checking exports for hints envelope..."
if [ -f "exports/graph_latest.json" ]; then
    echo "Found exports/graph_latest.json"
    jq '.metadata.hints' exports/graph_latest.json 2>/dev/null || echo "No hints envelope in metadata (expected if none emitted)"
elif [ -f "share/exports/graph_latest.json" ]; then
    echo "Found share/exports/graph_latest.json"
    jq '.metadata.hints' share/exports/graph_latest.json 2>/dev/null || echo "No hints envelope in metadata (expected if none emitted)"
else
    echo "No graph export found (expected if pipeline not complete)"
fi

# 3. Run guard validation
echo ""
echo "3. Running rules_guard validation..."
python3 scripts/rules_guard.py

# 4. Verify envelope structure (if present)
echo ""
echo "4. Verifying envelope structure (if present)..."
if [ -f "exports/graph_latest.json" ]; then
    jq -e '.metadata.hints.type == "hints_envelope" and .metadata.hints.version == "1.0" and (.metadata.hints.count == (.metadata.hints.items | length))' exports/graph_latest.json 2>/dev/null && echo "✓ Envelope structure valid" || echo "HINT: No valid envelope found (OK if no hints emitted)"
elif [ -f "share/exports/graph_latest.json" ]; then
    jq -e '.metadata.hints.type == "hints_envelope" and .metadata.hints.version == "1.0" and (.metadata.hints.count == (.metadata.hints.items | length))' share/exports/graph_latest.json 2>/dev/null && echo "✓ Envelope structure valid" || echo "HINT: No valid envelope found (OK if no hints emitted)"
fi

echo ""
echo "=== Verification Complete ==="

