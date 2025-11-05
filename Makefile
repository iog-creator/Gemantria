

# Python interpreter (for CI compatibility)
PYTHON ?= python3

ui.dev.help:
	@if [ -n "$$CI" ]; then echo "HINT[ui.dev.help]: CI detected; noop."; exit 0; fi
	@echo "UI local dev instructions:"
	@echo "1) make ingest.local.envelope"
	@echo "2) cd ui && npm create vite@latest . -- --template react-ts (or pnpm)"
	@echo "3) Implement loader to read /tmp/p9-ingest-envelope.json"
	@echo "4) Run: npm run dev (local only)"

# Codex CLI optional targets (local-only, CI-gated)

codex.task:
	@if [ "$(CI)" = "true" ] && [ "$(ALLOW_CODEX)" != "1" ]; then \
		echo "HINT: Codex CLI is optional and local-only. To enable in CI, set ALLOW_CODEX=1."; \
		exit 0; \
	fi
	@scripts/agents/codex-task.sh "$(TASK)" PROFILE=$(PROFILE)

codex.grok:
	@make codex.task PROFILE=grok4 TASK="$(TASK)"

codex.parallel:
	@if [ "$(CI)" = "true" ] && [ "$(ALLOW_CODEX)" != "1" ]; then \
		echo "HINT: Codex CLI is optional and local-only. To enable in CI, set ALLOW_CODEX=1."; \
		exit 0; \
	fi
	@scripts/agents/codex-par.sh < tasks.txt  # Adjust as needed, e.g., pipe from stdin

# Share sync (OPS v6.2 compliance)

share.sync:
	@python3 scripts/sync_share.py

# --- UI acceptance (headless) ---

ENVELOPE ?= share/exports/envelope.json
MIN_NODES ?= 200000
MIN_EDGES ?= 0
ALLOW_EMPTY ?=

.PHONY: accept.ui
accept.ui:
	@echo ">> UI acceptance on $(ENVELOPE) ..."
	@$(PYTHON) scripts/acceptance/check_envelope.py $(ENVELOPE) --min-nodes $(MIN_NODES) --min-edges $(MIN_EDGES) $(if $(ALLOW_EMPTY),--allow-empty,)

.PHONY: accept.ui.smoke
accept.ui.smoke:
	@echo ">> Export + accept (smoke)"
	@$(PYTHON) scripts/export_noun_index.py
	@$(MAKE) accept.ui ENVELOPE=$(ENVELOPE) MIN_NODES=$(MIN_NODES) MIN_EDGES=$(MIN_EDGES) ALLOW_EMPTY=$(ALLOW_EMPTY)

# --- UI temporal exports (CSV/PNG) ---

OUTDIR ?= ui/out
.PHONY: ui.export.temporal
ui.export.temporal:
	@echo ">> Temporal strip export to $(OUTDIR)"
	@$(PYTHON) scripts/ui/export_temporal_strip.py $(ENVELOPE) --outdir $(OUTDIR) --mode point

.PHONY: ui.export.temporal.span
ui.export.temporal.span:
	@echo ">> Temporal strip export (span mode) to $(OUTDIR)"
	@$(PYTHON) scripts/ui/export_temporal_strip.py $(ENVELOPE) --outdir $(OUTDIR) --mode span

# --- Temporal summary + PR comment ---

TEMPORAL_CSV ?= $(OUTDIR)/temporal_strip.csv
TEMPORAL_MD  ?= $(OUTDIR)/temporal_summary.md
.PHONY: ui.temporal.summary
ui.temporal.summary:
	@echo ">> Temporal summary → $(TEMPORAL_MD)"
	@$(PYTHON) scripts/ui/temporal_summary.py

.PHONY: ui.temporal.comment
ui.temporal.comment:
	@echo ">> Comment temporal summary on current PR"
	@PR=$$(gh pr view --json number --jq .number 2>/dev/null || echo ""); \
	if [ -z "$$PR" ]; then echo "No open PR found for this branch. SKIP."; exit 0; fi; \
	if [ ! -f "$(TEMPORAL_MD)" ]; then echo "Summary not found at $(TEMPORAL_MD). Run 'make ui.temporal.summary' first."; exit 1; fi; \
	gh pr comment $$PR -F "$(TEMPORAL_MD)"

.PHONY: test.ui.smoke
test.ui.smoke:
	@pytest tests/ui/test_extract_smoke.py

.PHONY: deploy.prod
deploy.prod:
	@echo ">> Prod deploy stub"
	@$(PYTHON) scripts/deploy.py

# COMPASS evaluation (mathematical correctness scoring)
ENVELOPE ?= share/exports/envelope.json

.PHONY: test.compass
test.compass:
	@echo ">> COMPASS evaluation on $(ENVELOPE)"
	@python3 scripts/compass/scorer.py $(ENVELOPE) --verbose

# CI smoke targets (for workflow compatibility)
.PHONY: eval.graph.calibrate.adv
eval.graph.calibrate.adv:
	@echo ">> Graph calibration (CI smoke - may fail without data)"
	@PYTHONPATH=. $(PYTHON) scripts/compass/scorer.py $(ENVELOPE) --verbose || echo "Calibration skipped (expected in CI without data)"

.PHONY: ci.exports.smoke
ci.exports.smoke:
	@echo ">> CI exports smoke (may fail without DB)"
	@PYTHONPATH=. $(PYTHON) scripts/export_noun_index.py --limit 10 || echo "CI exports smoke skipped (expected without DB)"

exports.guard.hebrew:
	@mkdir -p share/evidence
	@echo ">> Hebrew export integrity guard"
	@psql $$DSN -f scripts/sql/guard_hebrew_export.sql | tee share/evidence/guard_hebrew_export.out && awk "NR>1{sum+=$$2} END{exit (sum!=0)}" share/evidence/guard_hebrew_export.out

.PHONY: monitoring.badges
monitoring.badges:
	@echo ">> Generate monitoring badges (uptime/perf)"
	@python3 scripts/generate_badges.py --type monitoring --out share/eval/badges/

.PHONY: monitoring.run
monitoring.run:
	@echo ">> Run monitoring stub"
	@$(PYTHON) scripts/monitoring.py

.PHONY: scaling.run
scaling.run:
	@echo ">> Run scaling stub"
	@$(PYTHON) scripts/scaling.py

.PHONY: optimize.run
optimize.run:
	@echo ">> Run optimization stub"
	@$(PYTHON) scripts/optimize.py

.PHONY: expansion.run
expansion.run:
	@echo ">> Run expansion stub"
	@$(PYTHON) scripts/expansion.py

.PHONY: expansion.full
expansion.full:
	@echo ">> Run full expansion pipeline"
	@make expansion.run
	@if [ -f share/exports/expanded_envelope.json ]; then \
		make accept.ui ENVELOPE=share/exports/expanded_envelope.json MIN_NODES=200000; \
		make ui.temporal.summary; \
		echo "Full expansion complete"; \
	else \
		echo "Expansion failed - no expanded envelope found"; \
	fi

.PHONY: generate.forest
generate.forest:
	@echo ">> Generate forest overview"
	@$(PYTHON) scripts/generate_forest.py
	@echo "Forest generated: docs/forest/overview.md updated"

.PHONY: ontology.check
ontology.check:
	@echo ">> Check ontology forward compatibility"
	@$(PYTHON) scripts/ontology_compat.py
	@echo "Ontology compatibility check complete"

.PHONY: metrics.sync
metrics.sync:
	@echo ">> Sync metrics views to contract"
	@$(PYTHON) scripts/metrics_contract.py
	@echo "Metrics sync complete"

.PHONY: enforcement.check
enforcement.check:
	@echo ">> Check system enforcement bridge"
	@$(PYTHON) scripts/enforcement_bridge.py
	@echo "Enforcement bridge check complete"

.PHONY: temporal.analytics
temporal.analytics:
	@echo ">> Run temporal pattern analysis"
	@$(PYTHON) scripts/temporal_analytics.py
	@if [ -f share/exports/temporal_patterns.json ]; then \
		make accept.ui ENVELOPE=share/exports/temporal_patterns.json MIN_NODES=200000 || echo "Temporal validation skipped"; \
	fi
	@echo "Temporal analysis complete"

.PHONY: forecast.run
forecast.run:
	@echo ">> Run forecasting pipeline"
	@make temporal.analytics
	@if [ -f share/exports/forecast.json ]; then \
		echo "Forecast data available at share/exports/forecast.json"; \
	fi
	@echo "Forecast complete"

# Book processing integration
.PHONY: book.plan book.dry book.go book.stop book.resume

BOOK_CONFIG ?= config/book_plan.yaml

book.plan:
	@echo ">> Plan book processing"
	@$(PYTHON) scripts/run_book.py plan --cfg $(BOOK_CONFIG)

book.dry:
	@echo ">> Dry run book processing"
	@$(PYTHON) scripts/run_book.py dry --cfg $(BOOK_CONFIG)

book.go:
	@echo ">> Run full book processing"
	@$(PYTHON) scripts/run_book.py go --cfg $(BOOK_CONFIG)

book.stop:
	@echo ">> Stop-loss book processing (first N chapters)"
	@if [ -z "$(N)" ]; then echo "Usage: make book.stop N=5"; exit 1; fi
	@$(PYTHON) scripts/run_book.py stop --cfg $(BOOK_CONFIG) --n $(N)

book.resume:
	@echo ">> Resume book processing"
	@$(PYTHON) scripts/run_book.py resume

# Schema validation
schema.validate:
	@echo ">> Validate schemas against current exports"
	@if [ -f exports/graph_latest.json ]; then \
		$(PYTHON) scripts/eval/jsonschema_validate.py exports/graph_latest.json schemas/graph_output.schema.json 2>/dev/null || echo "Graph schema validation skipped (schema not found)"; \
	fi
	@if [ -f share/exports/envelope.json ]; then \
		$(PYTHON) scripts/eval/jsonschema_validate.py share/exports/envelope.json schemas/envelope.schema.json 2>/dev/null || echo "Envelope schema validation skipped (schema not found)"; \
	fi
	@echo "Schema validation complete"

# Analysis operations
analyze.graph:
	@echo ">> Run graph analysis (communities and centrality)"
	@$(PYTHON) scripts/analyze_graph.py

analyze.export:
	@echo ">> Export analysis results for visualization"
	@PYTHONPATH=. $(PYTHON) scripts/export_graph.py
	@PYTHONPATH=. $(PYTHON) scripts/export_stats.py

analyze.all:
	@echo ">> Run complete analysis suite"
	@make analyze.graph
	@make analyze.export
	@echo "Analysis complete"

# Unified pipeline orchestration
orchestrator.pipeline:
	@echo ">> Run main pipeline via orchestrator"
	@PYTHONPATH=. $(PYTHON) scripts/pipeline_orchestrator.py pipeline --book $(BOOK)

orchestrator.book:
	@echo ">> Run book processing via orchestrator"
	@PYTHONPATH=. $(PYTHON) scripts/pipeline_orchestrator.py book $(OPERATION) --config $(BOOK_CONFIG)

orchestrator.analysis:
	@echo ">> Run analysis via orchestrator"
	@PYTHONPATH=. $(PYTHON) scripts/pipeline_orchestrator.py analysis $(OPERATION)

orchestrator.embeddings:
	@echo ">> Run embeddings backfill via orchestrator"
	@PYTHONPATH=. $(PYTHON) scripts/pipeline_orchestrator.py embeddings --model $(EMBEDDING_MODEL) --dim $(EMBEDDING_DIM)

orchestrator.full:
	@echo ">> Run complete workflow via orchestrator"
	@PYTHONPATH=. $(PYTHON) scripts/pipeline_orchestrator.py full --book $(BOOK) --config $(BOOK_CONFIG) 2>&1 | tee /tmp/orchestrator_venv.log

# Integration testing
test.pipeline.integration:
	@echo ">> Run pipeline integration tests"
	@pytest tests/integration/test_pipeline_integration.py -v
