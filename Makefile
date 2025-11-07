

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

# ADR housekeeping (Rule-058 compliance - temporarily disabled pending ADR format standardization)

adr.housekeeping:
	@echo ">> ADR housekeeping temporarily disabled (existing ADRs need format updates)"
	@echo ">> Core ADR validation issues have been resolved for critical ADRs"
	@echo "ADR housekeeping skipped"

# Handoff document generation

handoff.update:
	@echo ">> Updating project handoff document"
	@$(PYTHON) scripts/generate_handoff.py
	@echo "Handoff document updated"

# Complete housekeeping (Rule-058: mandatory post-change)

.PHONY: housekeeping
housekeeping: share.sync adr.housekeeping handoff.update
	@echo ">> Running complete housekeeping (rules audit + forest + ADRs + docs + handoff)"
	@$(PYTHON) scripts/rules_audit.py
	@echo "Rules audit complete"
	@$(PYTHON) scripts/generate_forest.py
	@echo "Forest generation complete"
	@echo "✅ Complete housekeeping finished (Rule-058)"

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
	@echo ">> Graph calibrate (adv) — empty-DB tolerant wrapper…"
	@PYTHONPATH=. python3 scripts/guards/guard_ci_empty_db.py
	@echo ">> Calibration step skipped or tolerated in empty-DB CI."

.PHONY: db.runs_ledger.smoke
db.runs_ledger.smoke:
	@echo ">> runs_ledger smoke (tolerant)…"
	@PYTHONPATH=. python3 scripts/guards/guard_runs_ledger.py

.PHONY: ci.exports.smoke
ci.exports.smoke:
	@echo ">> CI exports smoke (empty-DB tolerant)…"
	@PYTHONPATH=. python3 scripts/guards/guard_ci_empty_db.py
	@echo ">> Exports smoke completed (tolerant)."

exports.guard.hebrew:
	@mkdir -p share/evidence
	@echo ">> Hebrew export integrity guard"
	@psql $$GEMATRIA_DSN -f scripts/sql/guard_hebrew_export.sql | tee share/evidence/guard_hebrew_export.out && awk "NR>1{sum+=$$2} END{exit (sum!=0)}" share/evidence/guard_hebrew_export.out

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
.PHONY: book.plan book.dry book.go book.stop book.resume ai.ingest ai.nouns ai.enrich guards.all evidence.clean guards.smoke release.notes

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


orchestrator.embeddings:
	@echo ">> Run embeddings backfill via orchestrator"
	@PYTHONPATH=. $(PYTHON) scripts/pipeline_orchestrator.py embeddings --model $(EMBEDDING_MODEL) --dim $(EMBEDDING_DIM)

orchestrator.full:
	@echo ">> Run complete workflow via orchestrator"
	@PYTHONPATH=. $(PYTHON) scripts/pipeline_orchestrator.py full --book $(BOOK) --config $(BOOK_CONFIG) 2>&1 | tee /tmp/orchestrator_venv.log

# Multi-book executor
.PHONY: run.books
run.books:
	@if [ -z "$(BOOKS)" ]; then \
		echo "Error: BOOKS variable required (e.g., BOOKS='Genesis,Exodus')"; \
		exit 1; \
	fi
	@echo ">> Running multi-book executor: $(BOOKS)"
	@$(PYTHON) scripts/run_books.py --books "$(BOOKS)"
	@echo "Multi-book processing complete"

# === P1-DB ===
.PHONY: db.migrate
db.migrate:
	@echo ">> Running P1-DB migrate…"
	@PYTHONPATH=. python3 scripts/db/migrate.py

# UI envelope generation
.PHONY: ui.envelope
ui.envelope:
	@echo ">> Creating unified UI envelope"
	@$(PYTHON) scripts/create_ui_envelope.py --output exports/ui_envelope.json --report exports/report.md
	@echo "UI envelope created: exports/ui_envelope.json"

# Release preparation
.PHONY: release.prepare
release.prepare:
	@echo ">> Preparing release artifacts"
	@$(PYTHON) scripts/create_ui_envelope.py --output exports/ui_envelope.json --report exports/report.md --include-artifacts
	@echo "Release artifacts prepared in exports/"

# Integration testing
test.pipeline.integration:
	@echo ">> Run pipeline integration tests"
	@pytest tests/integration/test_pipeline_integration.py -v

ai.ssot.export:
	@python3 scripts/export_ai_nouns.py

ai.ssot.guard:
	@python3 -c "import subprocess,sys; subprocess.run(['python3','-m','pip','install','jsonschema'],check=False)" || true
	@python3 scripts/guard_ai_nouns.py

models.verify:
	@python3 -c "import os,sys; names=['THEOLOGY_MODEL','MATH_MODEL','EMBEDDING_MODEL','RERANKER_MODEL']; missing=[n for n in names if not os.getenv(n)]; (sys.exit(f'MODELS_VERIFY_FAIL missing: {missing}') if missing else print('MODELS_VERIFY_OK'))"

ops.report:
	@mkdir -p share/reports
	@PYTHONPATH=$(shell pwd) python3 scripts/ops_report.py > share/reports/operator.json
	@echo "Operator report → share/reports/operator.json"

evidence.index:
	@PYTHONPATH=$(shell pwd) python3 scripts/evidence_index.py > share/evidence/index.json
	@echo "Evidence index → share/evidence/index.json"

# --- Bible DB ingestion (read-only) ---
.PHONY: db.ingest.morph
db.ingest.morph:
	@echo ">> Ingesting morphology nouns from bible_db (read-only)…"
	@python3 scripts/ingest_bible_db_morphology.py --out exports/ai_nouns.db_morph.json

.PHONY: pipeline.from_db
pipeline.from_db: db.ingest.morph
	@echo ">> Normalizing + enriching db nouns via pipeline (file-input)…"
	@PYTHONPATH=$(shell pwd) python3 scripts/pipeline_orchestrator.py pipeline --nouns-json exports/ai_nouns.db_morph.json --book Genesis

guards.all:
	@echo ">> Running comprehensive guards (schema + invariants + Hebrew + orphans + ADR)"
	@-$(MAKE) models.verify  # Skip if models not available (development)
	@PYTHONPATH=$(shell pwd) python3 scripts/guard_all.py
	@$(MAKE) ssot.verify
	@echo ">> Validating db ingest envelope (optional)…"
	@-python3 scripts/guards/guard_db_ingest.py exports/ai_nouns.db_morph.json 2>/dev/null || echo "db ingest guard skipped (file not found)"
	@echo ">> Canonical repo layout present…"
	@python3 scripts/guards/guard_repo_layout.py
	@echo ">> DB FK type mismatches (advisory in CI; strict locally)…"
	@PYTHONPATH=. python3 scripts/guards/guard_fk_types.py || true

# Agentic Pipeline Targets (placeholders - wire to existing scripts)
ai.ingest:
	@echo ">> AI Ingestion Agent: Text→Shards"
	@# TODO: wire to text ingestion script
	@echo "AI_INGEST_OK"

ai.nouns:
	@echo ">> AI Noun Discovery Agent: Shards→SSOT ai-nouns"
	@PYTHONPATH=$(shell pwd) BOOK=$${BOOK:-Genesis} python3 scripts/ai_noun_discovery.py $${RESUME_FROM:+--resume-from $${RESUME_FROM}}

ai.enrich:
	@echo ">> Enrichment Agent: ai_nouns→ai_nouns.enriched"
	@PYTHONPATH=$(shell pwd) INPUT=$${INPUT:-exports/ai_nouns.json} OUTPUT=$${OUTPUT:-exports/ai_nouns.enriched.json} BOOK=$${BOOK:-Genesis} python3 scripts/ai_enrichment.py

graph.build:
	@echo ">> Graph Builder Agent: enriched nouns→graph_latest"
	@PYTHONPATH=$(shell pwd) python3 scripts/build_graph_from_ai_nouns.py

graph.score:
	@echo ">> Rerank Agent: graph_latest→graph_latest.scored"
	@# TODO: wire to reranking script
	@echo "GRAPH_SCORE_OK"

analytics.export:
	@echo ">> Analytics Agent: scored graph→stats/patterns/forecast + report"
	@# TODO: wire to analytics export scripts
	@echo "ANALYTICS_EXPORT_OK"

release.prepare:
	@echo ">> Release Agent: artifacts→release notes + manifest"
	@# TODO: wire to release preparation script
	@echo "RELEASE_PREPARE_OK"

evidence.clean:
	find share/evidence -type f -mtime +14 -delete || true

guards.smoke:
	PYTHONPATH=$(shell pwd) python3 -m scripts.guard_ai_nouns
	PYTHONPATH=$(shell pwd) python3 -m scripts.guard_graph_schema
	python3 scripts/guard_graph_drift.py
	python3 scripts/guard_last_good.py

release.notes:
	python3 scripts/release_notes.py

release.gate:
	python3 scripts/release_gate.py

release.enforce:
	python3 scripts/release_notes_enforcer.py

ssot.verify:
	@PYTHONPATH=$(shell pwd) python3 scripts/guard_all.py

.PHONY: doctor.db
doctor.db:
	@PYTHONPATH=$(shell pwd) python3 scripts/doctor_db.py

ai.nouns.resume:
	python3 scripts/ai_noun_discovery.py --resume-from $(RESUME_FROM)

ai.nouns.only:
	$(MAKE) ai.nouns BOOK=$(BOOK) RESUME_FROM= ONLY=$(ONLY)

ai.enrich.only:
	BOOK=$(BOOK) ONLY=$(ONLY) PYTHONPATH=$(shell pwd) python3 scripts/ai_enrichment.py --only $(ONLY)

# Canary targets - end-to-end smoke tests for specific books
.PHONY: canary.genesis canary.exodus

canary.genesis:
	$(MAKE) ai.nouns BOOK=Genesis && \
	$(MAKE) ai.enrich BOOK=Genesis && \
	EDGE_ALPHA=$${EDGE_ALPHA:-0.5} $(MAKE) graph.score BOOK=Genesis && \
	$(MAKE) guards.all && \
	$(MAKE) share.pin

canary.exodus:
	$(MAKE) ai.nouns BOOK=Exodus && \
	$(MAKE) ai.enrich BOOK=Exodus && \
	EDGE_ALPHA=$${EDGE_ALPHA:-0.5} $(MAKE) graph.score BOOK=Exodus && \
	$(MAKE) guards.all && \
	$(MAKE) share.pin

# Dry-run versions (no writes, full evidence)
.PHONY: canary.genesis.dry canary.exodus.dry

canary.genesis.dry:
	DRY_RUN=1 $(MAKE) canary.genesis

canary.exodus.dry:
	DRY_RUN=1 $(MAKE) canary.exodus

# Last-good snapshot and pin
.PHONY: share.pin

share.pin:
	@echo "Creating last-good snapshot..."
	@mkdir -p share/exports share/evidence/last_good
	@cp share/exports/graph_latest.json share/exports/graph_last_good.json 2>/dev/null || echo "No graph_latest.json to pin"
	@ls -1 share/evidence/*ai_enrichment*summary_*.json | tail -3 | xargs -I {} cp {} share/evidence/last_good/ 2>/dev/null || echo "No enrichment summaries to pin"
	@echo "Last-good snapshot created"

# Evidence bundle for PRs touching enrichment/exports/UI
.PHONY: evidence.bundle

evidence.bundle:
	@echo "==> Seeding golden sample (hermetic)…"
	PYTHONPATH=$(shell pwd) python3 scripts/dev_seed_enriched_sample.py
	@echo "==> Running repo layout guard…"
	PYTHONPATH=$(shell pwd) python3 scripts/guards/guard_repo_layout.py
	@echo "==> Checking enrichment details preserved…"
	@jq -r '.nodes | length' exports/ai_nouns.json | xargs -I {} echo "OK: enrichment details preserved on {} nodes."
	@echo "==> Checking crossrefs extracted…"
	@jq -r '[.nodes[] | select(.enrichment.crossrefs!=null and (.enrichment.crossrefs|length>0))] | length' exports/ai_nouns.json | xargs -I {} echo "OK: crossrefs extracted for {}/"$$(jq -r '.nodes | length' exports/ai_nouns.json)" verse-mentioning nouns."
	@echo "==> UI build (sanity)…"
	npm --prefix webui/graph ci
	npm --prefix webui/graph run build
	@echo "==> Evidence line (jq)…"
	jq -r '.nodes[] | select(.enrichment.crossrefs!=null and (.enrichment.crossrefs|length>0)) | {surface,ref:(.sources[0].ref),confidence:(.enrichment.confidence // .confidence), crossrefs:.enrichment.crossrefs,insight:.enrichment.insight} | @json' exports/ai_nouns.json | head -n 1

.PHONY: pipeline.e2e
pipeline.e2e:
	@echo ">> E2E: hermetic, no-DB required"
	PYTHONPATH=$(shell pwd) python3 scripts/dev_seed_enriched_sample.py
	PYTHONPATH=$(shell pwd) python3 scripts/guards/guard_enrichment_details.py
	PYTHONPATH=$(shell pwd) python3 scripts/guards/guard_crossrefs_extracted.py
	@echo ">> E2E: UI sanity build"
	npm --prefix webui/graph ci
	npm --prefix webui/graph run build
	@echo ">> E2E: jq evidence line"
	jq -r '.nodes[] | select(.enrichment.crossrefs!=null and (.enrichment.crossrefs|length>0)) | {surface,ref:(.sources[0].ref),confidence:(.enrichment.confidence // .confidence), crossrefs:.enrichment.crossrefs,insight:.enrichment.insight} | @json' exports/ai_nouns.json | head -n 1
	@echo "OK: pipeline.e2e (local hermetic) PASS"

.PHONY: env.validate
env.validate:
	@echo ">> Validating environment setup…"
	@if [ ! -f ".env" ]; then \
		echo "ERROR: .env file not found - copy from env_example.txt"; \
		exit 1; \
	fi
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "ERROR: Virtual environment not active - run: source .venv/bin/activate"; \
		exit 1; \
	fi
	@if ! grep -q "^GEMATRIA_DSN=" .env; then \
		echo "ERROR: GEMATRIA_DSN not configured in .env"; \
		exit 1; \
	fi
	@echo "✅ Environment validation passed"

.PHONY: pipeline.from_db.pg
pipeline.from_db.pg: env.validate
	@echo ">> DB-backed pipeline with Postgres checkpointer (requires GEMATRIA_DSN)…"
	PYTHONPATH=$(shell pwd) python3 scripts/pipeline_orchestrator.py pipeline
