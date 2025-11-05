#!/bin/bash
# Verification commands to run after enrichment completes
# Run this script once enrichment reaches 100%

set -e

echo "=== Checking enrichment completion ==="
python3 scripts/monitor_pipeline.py --json | jq '.stage_status.stages.enrichment | {count, total, progress: (.count / .total * 100 | floor), completed: (.count == .total)}'

echo ""
echo "=== Running exports smoke ==="
make ci.exports.smoke 2>&1 | tail -30

echo ""
echo "=== Checking graph exports ==="
ls -lh share/exports/ 2>/dev/null || echo "No exports found"

echo ""
echo "=== Diff vs golden (if exists) ==="
diff -u share/exports/graph.json golden/graph.json 2>&1 || echo "No golden/graph.json found"

echo ""
echo "=== Testing agent imports ==="
python3 -c "from src.services.planner_agent import plan_processing; from src.services.math_model_client import verify_gematria_calculation; from src.services.semantic_agent import extract_semantic_features; from src.services.expert_agent import analyze_theological; print('✅ All agents import successfully')" 2>&1

echo ""
echo "=== Testing graph creation (default) ==="
python3 -c "from src.graph.graph import create_graph; g = create_graph(); print('✅ Graph created (default enrichment flow)')" 2>&1

echo ""
echo "=== Testing graph creation (with agents) ==="
USE_AGENTS=true python3 -c "from src.graph.graph import create_graph; import os; print(f'USE_AGENTS={os.getenv(\"USE_AGENTS\")}'); g = create_graph(); print('✅ Graph created with agents enabled')" 2>&1

echo ""
echo "=== Verifying agent wiring ==="
USE_AGENTS=true python3 -c "from src.graph.graph import create_graph; g = create_graph(); edges = [(e.source, e.target) for e in g.edges]; agent_edges = [e for e in edges if any(x in ['planner', 'math_agent', 'semantic_agent', 'expert_agent'] for x in e)]; print(f'Agent edges: {agent_edges}'); print('✅ Agents wired' if agent_edges else '❌ Agents not wired')" 2>&1

echo ""
echo "=== Git status ==="
git add . && git status -sb

echo ""
echo "=== Ruff check ==="
ruff format --check . && ruff check . 2>&1 | grep -v "~/mcp" | tail -10

