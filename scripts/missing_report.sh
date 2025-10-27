#!/usr/bin/env bash
set -euo pipefail

must_have=(
"README.md" "AGENTS.md" "SSOT_MASTER_PLAN.md" "Makefile" "ruff.toml" "pre-commit-config.yaml" "pull_request_template.md"
".cursor/rules"
".github/workflows"
"SHARE_MANIFEST.json"
"share/RULES_INDEX.md" "share/all_rules_compiled.md"
"share/eval/badges"
"share/eval/quality_history.jsonl" "share/eval/calibration_adv.json" "share/eval/edges/edge_class_counts.json"
"exports/graph_stats.json" "exports/graph_correlations.json" "exports/graph_patterns.json" "exports/temporal_patterns.json" "exports/pattern_forecast.json"
"api_server.py" "env_loader.py" "export_stats.py" "generate_report.py" "rules_guard.py" "rules_audit.py"
"scripts/doctor.py" "scripts/bootstrap_dev.sh" "scripts/mode_decider.py" "scripts/eval/calibrate_advanced.py" "scripts/eval/quality_trend.py"
"webui/graph/package.json" "webui/graph/vite.config.ts" "webui/graph/src/components/GraphView.tsx"
)

echo "=== Missing Items Report ==="
missing=0
for p in "${must_have[@]}"; do
  if [ -e "$p" ]; then
    echo "FOUND:   $p"
  else
    echo "MISSING: $p"
    missing=$((missing+1))
  fi
done

echo "=== Summary ==="
echo "Missing count: $missing"
exit 0
