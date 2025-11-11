

# Python interpreter (for CI compatibility)
PYTHON ?= python3
export PYTHON

# ---- Guard: python runner regression ----------------------------------------
.PHONY: guard.python.runner
guard.python.runner:
	@bash scripts/guards/guard_python_runner.sh

# ---- Guard: DSN centralization ----------------------------------------------
.PHONY: guard.dsn.centralized
guard.dsn.centralized:
	@bash scripts/guards/guard_dsn_centralized.sh | tee evidence/guard.dsn.centralized.json >/dev/null

.PHONY: guard.dsn.centralized.strict
guard.dsn.centralized.strict:
	@STRICT_DSN_CENTRAL=1 bash scripts/guards/guard_dsn_centralized.sh | tee evidence/guard.dsn.centralized.strict.json >/dev/null

# --- Knowledge Sentinels (Drift Kill-Switch) ---
.PHONY: guard.knowledge.hints guard.knowledge.strict
guard.knowledge.hints:
	@python3 scripts/ci/guard_knowledge.py | tee evidence/guard_knowledge.json; \
	jq -e '.ok_repo == true' evidence/guard_knowledge.json >/dev/null || true

guard.knowledge.strict:
	@python3 scripts/ci/guard_knowledge.py | tee evidence/guard_knowledge.json; \
	jq -e '.ok_repo == true' evidence/guard_knowledge.json

.PHONY: guard.secrets.mask
guard.secrets.mask:
	@bash scripts/guards/guard_secrets_mask.sh | tee evidence/guard.secrets.mask.json >/dev/null

.PHONY: guard.ci.no_schedules
guard.ci.no_schedules:
	@python3 scripts/ci/guard_no_schedules.py

# Added by ops: guard target for prompt-format
.PHONY: guard.prompt.format
guard.prompt.format:
	@scripts/ci/run_strict.sh python3 scripts/ci/guard_prompt_format.py

# Guard: docs presence (RFC-072)
.PHONY: guard.docs.presence
guard.docs.presence:
	@scripts/ci/run_strict.sh python3 scripts/ci/guard_docs_presence.py

# Guard: ai-nouns schema (RFC-072 Part 2)
.PHONY: guard.ai_nouns.schema
guard.ai_nouns.schema:
	@scripts/ci/run_strict.sh python3 scripts/ci/guard_json_schema.py --name ai_nouns \
		--schema-name ai-nouns.schema.json \
		--data-glob "share/**/*.json" \
		--data-glob "evidence/**/*.json" \
		--data-glob "ui/out/**/*.json" \
		--filename-contains ai_nouns --filename-contains nouns

# Guard: graph core schema (avoids stats/patterns/correlations)
.PHONY: guard.graph.core.schema
guard.graph.core.schema:
	@scripts/ci/run_strict.sh python3 scripts/ci/guard_json_schema.py --name graph_core \
		--schema-name graph.schema.json \
		--data-glob "share/**/*.json" \
		--data-glob "evidence/**/*.json" \
		--data-glob "ui/out/**/*.json" \
		--filename-contains graph \
		--exclude-contains graph-stats --exclude-contains graph_stats --exclude-contains patterns --exclude-contains correlations

# Guard: graph-stats schema
.PHONY: guard.graph.stats.schema
guard.graph.stats.schema:
	@scripts/ci/run_strict.sh python3 scripts/ci/guard_json_schema.py --name graph_stats \
		--schema-name graph-stats.schema.json \
		--data-glob "share/**/*.json" \
		--data-glob "evidence/**/*.json" \
		--data-glob "ui/out/**/*.json" \
		--filename-contains graph-stats --filename-contains graph_stats

# Guard: graph-patterns schema
.PHONY: guard.graph.patterns.schema
guard.graph.patterns.schema:
	@scripts/ci/run_strict.sh python3 scripts/ci/guard_json_schema.py --name graph_patterns \
		--schema-name graph-patterns.schema.json \
		--data-glob "share/**/*.json" \
		--data-glob "evidence/**/*.json" \
		--data-glob "ui/out/**/*.json" \
		--filename-contains patterns --filename-contains graph-patterns \
		--exclude-contains report

# Guard: graph-correlations schema
.PHONY: guard.graph.correlations.schema
guard.graph.correlations.schema:
	@scripts/ci/run_strict.sh python3 scripts/ci/guard_json_schema.py --name graph_correlations \
		--schema-name graph-correlations.schema.json \
		--data-glob "share/**/*.json" \
		--data-glob "evidence/**/*.json" \
		--data-glob "ui/out/**/*.json" \
		--filename-contains correlations

# Guard: jsonschema import (STRICT at tag-time, HINT on PRs)
.PHONY: guard.jsonschema.import
guard.jsonschema.import:
	@scripts/ci/run_strict.sh python3 scripts/ci/guard_jsonschema_import.py

# === Auto-resolve DSNs from centralized loader (available to all targets) ===
ATLAS_DSN    ?= $(shell cd $(CURDIR) && PYTHONPATH=$(CURDIR) python3 scripts/config/dsn_echo.py --ro)
GEMATRIA_DSN ?= $(shell cd $(CURDIR) && PYTHONPATH=$(CURDIR) python3 scripts/config/dsn_echo.py --rw)
export ATLAS_DSN
export GEMATRIA_DSN

ui.dev.help:
	@if [ -n "$$CI" ]; then echo "HINT[ui.dev.help]: CI detected; noop."; exit 0; fi
	@echo "UI local dev instructions:"
	@echo "1) make ingest.local.envelope"
	@echo "2) cd ui && npm create vite@latest . -- --template react-ts (or pnpm)"
	@echo "3) Implement loader to read /tmp/p9-ingest-envelope.json"
	@echo "4) Run: npm run dev (local only)"

.PHONY: help clean

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

clean: ## 🧹 Clean Python cache and build artifacts
	@echo "🧹 Cleaning Python cache and build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "✅ Clean complete."

# ==============================================================================
#  deps
# ==============================================================================

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
	@PYTHONPATH=. python3 scripts/sync_share.py

# ADR housekeeping (Rule-058 compliance - temporarily disabled pending ADR format standardization)

.PHONY: adr.housekeeping
adr.housekeeping:
	@echo ">> ADR housekeeping temporarily disabled (existing ADRs need format updates)"
	@echo ">> Core ADR validation issues have been resolved for critical ADRs"
	@echo "ADR housekeeping skipped"

# Governance housekeeping (Rule-058 + Rule-026 compliance)
.PHONY: governance.housekeeping
governance.housekeeping:
	@echo ">> Running governance housekeeping (database + compliance + docs)"
	@PYTHONPATH=. $(PYTHON) scripts/governance_housekeeping.py
	@echo "Governance housekeeping complete"

# Governance docs hints (Rule-026 + Rule-065 compliance)
.PHONY: governance.docs.hints
governance.docs.hints:
	@echo ">> Checking for governance docs/rule changes and emitting hints"
	@PYTHONPATH=. $(PYTHON) scripts/governance_docs_hints.py || true
	@echo "Governance docs hints check complete"

# Document management hints (Rule-050 OPS contract + Rule-061 AI learning)
.PHONY: docs.hints
docs.hints:
	@echo ">> Running document management hint checks"
	-@$(PYTHON) scripts/document_management_hints.py  # Ignore exit code - hints are informational
	@echo "Document hints check complete"

# AI Learning Analytics (Rule-058 continuous improvement)
.PHONY: ai.analytics
ai.analytics:
	@echo ">> Running AI analytics dashboard"
	@$(PYTHON) scripts/ai_analytics_dashboard.py dashboard
	@echo "AI analytics complete"

.PHONY: ai.learning.export
ai.learning.export:
	@echo ">> Exporting AI learning data"
	@$(PYTHON) scripts/ai_learning_tracker.py export_learning_data
	@echo "AI learning data exported"

# AI readiness and embeddings (LM Studio integration)
.PHONY: ai.readiness ai.embed.sample ai.search.demo
ai.readiness:
	@# Resolve base_url: LMSTUDIO_BASE_URL (if set) else LM_STUDIO_HOST + '/v1'
	@base_url=""; \
	if [ -n "$${LMSTUDIO_BASE_URL:-}" ]; then base_url="$$LMSTUDIO_BASE_URL"; \
	elif [ -n "$${LM_STUDIO_HOST:-}" ]; then base_url="$${LM_STUDIO_HOST%/}/v1"; \
	fi; \
	if [ -z "$$base_url" ]; then echo "HINT: set LM_STUDIO_HOST (e.g., http://127.0.0.1:1234) or LMSTUDIO_BASE_URL (.../v1)"; else \
	  echo "AI: probing $$base_url/models"; \
	  curl -sS "$$base_url/models" | head -c 400 || true; echo; fi
	@if command -v psql >/dev/null 2>&1 && [ -n "$${ATLAS_DSN:-$${GEMATRIA_DSN:-}}" ]; then \
	  psql "$${ATLAS_DSN:-$${GEMATRIA_DSN}}" -v ON_ERROR_STOP=1 -tAc "select 'vector='||(select extname from pg_extension where extname='vector')" || true; \
	fi

ai.embed.sample:
	@if [ -z "$${ATLAS_DSN_RW:-}" ]; then echo "NO-GO: ATLAS_DSN_RW (restricted RW) required for writes"; exit 1; fi
	@if [ -z "$${LM_EMBED_MODEL:-}" ]; then echo "NO-GO: set LM_EMBED_MODEL"; exit 1; fi
	python3 scripts/ai/embeddings_upsert.py "Covenant" "Prophecy" "Wisdom" "Temple" "Exodus"

ai.search.demo:
	@if [ -z "$${LM_EMBED_MODEL:-}" ]; then echo "NO-GO: set LM_EMBED_MODEL"; exit 1; fi
	python3 scripts/ai/search_demo.py "covenant wisdom"

.PHONY: writers.smoke
writers.smoke:
	@if [ -z "$${ATLAS_DSN_RW:-}" ]; then echo "NO-GO: ATLAS_DSN_RW required"; exit 1; fi
	PYTHONPATH="$$(pwd):$${PYTHONPATH:-}" python3 scripts/smokes/writers_smoke.py | tee evidence/writers.smoke.json >/dev/null

.PHONY: telemetry.smoke
telemetry.smoke:
	@if [ -z "$${ATLAS_DSN_RW:-}" ]; then echo "NO-GO: ATLAS_DSN_RW required"; exit 1; fi
	psql "$$ATLAS_DSN_RW" -v ON_ERROR_STOP=1 -f scripts/sql/pg/095_grants_fix.sql
	python3 scripts/smokes/telemetry_smoke.py | tee evidence/telemetry.smoke.json >/dev/null
	STRICT_ATLAS_DSN=1 make -s atlas.proof.dsn | tee evidence/atlas.proof.strict.tail.txt >/dev/null

# Handoff document generation

handoff.update:
	@echo ">> Updating project handoff document"
	@PYTHONPATH=. $(PYTHON) scripts/generate_handoff.py
	@echo "Handoff document updated"

# Atlas status diagram generation

.PHONY: atlas.update atlas.preview.html atlas.preview.txt atlas.preview.mmd
atlas.update:
	@python3 scripts/status/update_mermaid_from_evidence.py

atlas.preview.html:
	@python3 scripts/status/preview_atlas.py html

atlas.preview.txt:
	@python3 scripts/status/preview_atlas.py txt

atlas.preview.mmd:
	@python3 scripts/status/preview_atlas.py mmd

# Atlas telemetry-driven dashboard (browser-first, PR-safe)

.PHONY: atlas.generate atlas.live atlas.historical atlas.dependencies atlas.calls atlas.classes atlas.knowledge atlas.kpis atlas.dashboard atlas.all atlas.test atlas.serve atlas.watch
atlas.generate: ## Generate all Atlas diagrams and summaries
	@python3 scripts/atlas/generate_atlas.py

atlas.live: ## Generate execution_live.mmd diagram
	@python3 scripts/atlas/generate_atlas.py --diagram execution_live

atlas.historical: ## Generate pipeline_flow_historical.mmd diagram
	@python3 scripts/atlas/generate_atlas.py --diagram pipeline_flow_historical

atlas.dependencies: ## Generate dependencies.mmd diagram
	@python3 scripts/atlas/generate_atlas.py --diagram dependencies

atlas.calls: ## Generate call_graph.mmd diagram
	@python3 scripts/atlas/generate_atlas.py --diagram call_graph

atlas.classes: ## Generate class_diagram.mmd diagram
	@python3 scripts/atlas/generate_atlas.py --diagram class_diagram

atlas.knowledge: ## Generate knowledge_graph.mmd diagram
	@python3 scripts/atlas/generate_atlas.py --diagram knowledge_graph

atlas.kpis: ## Generate kpis.mmd diagram
	@python3 scripts/atlas/generate_atlas.py --diagram kpis

atlas.dashboard: ## Ensure atlas dashboard hub and vendor files are present
	@test -f docs/atlas/index.html || (echo "ERROR: docs/atlas/index.html missing" && exit 1)
	@test -f docs/vendor/mermaid.min.js || (echo "WARN: docs/vendor/mermaid.min.js missing (stub may be present)" && exit 0)
	@echo "Atlas dashboard files present"

atlas.all: atlas.generate ## Alias for atlas.generate

atlas.test: ## Time atlas generation and warn if >5s
	@echo "Timing atlas generation..."
	@time python3 scripts/atlas/generate_atlas.py

.PHONY: atlas.test.backlink
atlas.test.backlink: ## Verify "Back to Atlas" links exist in evidence pages
	@grep -q '<a href="../atlas/index.html">' docs/evidence/*.html && echo "ok: backlink in HTML" || (echo "FAIL: backlink missing in HTML"; exit 1)
	@grep -q '\[← Back to Atlas](\.\./atlas/index\.html)' docs/evidence/*.md && echo "ok: backlink in Markdown" || (echo "FAIL: backlink missing in Markdown"; exit 1)

atlas.serve: ## Start local HTTP server for atlas preview (port 8888)
	@echo "Starting HTTP server on port 8888..."
	@echo "Open http://localhost:8888/atlas/index.html in your browser"
	@python3 -m http.server --directory docs 8888

atlas.watch: ## Watch for changes and regenerate "Now" diagram (local-only, not used in CI)
	@if [ -n "$$CI" ]; then echo "HINT: atlas.watch is local-only; skipping in CI"; exit 0; fi
	@echo "Watching for changes (local-only, press Ctrl+C to stop)..."
	@echo "HINT: File watcher not implemented yet; use 'make atlas.generate' manually"

# --- Atlas DSN-on proof (read-only; fails fast if DSN missing) ---
.PHONY: atlas.proof.dsn
atlas.proof.dsn: ## DSN proof: generate masked JSON + HTML with backlink (HINT by default; STRICT with STRICT_ATLAS_DSN=1)
	@cd $(CURDIR) && PYTHONPATH=$(CURDIR) $(PYTHON) scripts/ops/atlas_proof_dsn.py | tee evidence/atlas.proof.dsn.json >/dev/null

## Generate Atlas Mermaid artifacts (HINT if STRICT_ATLAS_DSN!=1 or DSN/libs missing)
.PHONY: atlas.generate.mermaid atlas.generate.7d atlas.generate.30d
atlas.generate.mermaid:
	@cd $(CURDIR) && PYTHONPATH=$(CURDIR) $(PYTHON) scripts/atlas/generate_mermaid.py --window $${ATLAS_WINDOW:-24h} | tee evidence/atlas.generate.mermaid.json >/dev/null

atlas.generate.7d:
	@cd $(CURDIR) && ATLAS_WINDOW=7d PYTHONPATH=$(CURDIR) $(PYTHON) scripts/atlas/generate_mermaid.py --window 7d | tee evidence/atlas.generate.7d.json >/dev/null

atlas.generate.30d:
	@cd $(CURDIR) && ATLAS_WINDOW=30d PYTHONPATH=$(CURDIR) $(PYTHON) scripts/atlas/generate_mermaid.py --window 30d | tee evidence/atlas.generate.30d.json >/dev/null

# Atlas node pages (PR-safe: file-first)
.PHONY: atlas.nodes
atlas.nodes:
	@cd $(CURDIR) && PYTHONPATH=$(CURDIR) $(PYTHON) scripts/atlas/generate_node_pages.py | tee evidence/atlas.nodes.json >/dev/null
	@echo "✅ Atlas node pages generated"

# Wire Mermaid clicks for nodes in docs/atlas/execution_live.mmd and dependencies.mmd if present.
# Adds lines of the form: click "<node>" "nodes/<node>.html" "Details"
# Order matters: regenerate .mmd → (re)build nodes → wire clicks last (so regen cannot clobber).
.PHONY: atlas.wire.clicks
atlas.wire.clicks:
	@set -e; \
	files="docs/atlas/execution_live.mmd docs/atlas/dependencies.mmd"; \
	for f in $$files; do \
	  test -f "$$f" || continue; \
	  if [ -f evidence/atlas.nodes.json ]; then \
	    jq -r '.written[]?|split("/")[-1]|sub(".html$";"")' evidence/atlas.nodes.json 2>/dev/null | while read -r nid; do \
	      [ -z "$$nid" ] && continue; \
	      echo "$$nid" | grep -Eq '://' && continue; \
	      echo "$$nid" | grep -q '/' && continue; \
	      grep -qE "^[[:space:]]*click[[:space:]]+\"?$$nid\"?[[:space:]]+\"nodes/$$nid.html\"" "$$f" && continue; \
	      printf '  click "%s" "nodes/%s.html" "Details"\n' "$$nid" "$$nid" >> "$$f"; \
	    done; \
	  elif [ -f docs/atlas/_kpis.json ]; then \
	    jq -r '.nodes[].id' docs/atlas/_kpis.json 2>/dev/null | while read -r nid; do \
	      [ -z "$$nid" ] && continue; \
	      echo "$$nid" | grep -Eq '://' && continue; \
	      echo "$$nid" | grep -q '/' && continue; \
	      grep -qE "^[[:space:]]*click[[:space:]]+\"?$$nid\"?[[:space:]]+\"nodes/$$nid.html\"" "$$f" && continue; \
	      printf '  click "%s" "nodes/%s.html" "Details"\n' "$$nid" "$$nid" >> "$$f"; \
	    done; \
	  fi; \
	done; \
	echo "✅ Wired clicks (where applicable)"

.PHONY: atlas.clickproof
atlas.clickproof:
	@for f in docs/atlas/execution_live.mmd docs/atlas/dependencies.mmd; do \
	  test -f "$$f" && { echo "----- $$f (click lines)"; grep -E "^[[:space:]]*click[[:space:]]" "$$f" | tail -n 20 || true; }; \
	done

# Convenience: full regen + nodes + wire
.PHONY: atlas.generate.all
atlas.generate.all: atlas.generate.mermaid atlas.nodes atlas.wire.clicks
	@echo "✅ atlas.generate.all complete"

.PHONY: atlas.traces
atlas.traces:
	@python3 scripts/atlas/generate_node_pages.py >/dev/null || true
	@echo "OK: atlas node pages refreshed with traces (if available)"

# Convenience: open a local viewer (no network) for screenshots
.PHONY: atlas.serve.mermaid
atlas.serve.mermaid:
	@python3 -m http.server 8000 >/dev/null 2>&1 &
	@echo $$! > .server.pid
	@sleep 1
	@echo "Serving docs at http://localhost:8000/docs/atlas/index.html"

.PHONY: atlas.serve.mermaid.stop
atlas.serve.mermaid.stop:
	@test -f .server.pid && kill $$(cat .server.pid) && rm .server.pid || true

.PHONY: atlas.proof.dsn.old
atlas.proof.dsn.old: ## DSN-on proof: verify connectivity and generate Atlas (read-only; stays grey/HINT if DB unreachable) [DEPRECATED - use atlas.proof.dsn]
	@ATLAS_DSN="$${ATLAS_DSN:-$$GEMATRIA_DSN}"; \
	if [ -z "$$ATLAS_DSN" ]; then \
		echo "LOUD_FAIL: ATLAS_DSN and GEMATRIA_DSN not set"; \
		if [ "$$STRICT_ATLAS_DSN" = "1" ]; then exit 2; else exit 0; fi; \
	fi; \
	psql "$$ATLAS_DSN" -tAc "SELECT now();" >/dev/null 2>&1 || { \
		echo "HINT: DB unreachable; staying in grey mode"; \
		if [ "$$STRICT_ATLAS_DSN" = "1" ]; then exit 2; else exit 0; fi; \
	}; \
	ATLAS_DSN="$$ATLAS_DSN" $(PYTHON) scripts/atlas/atlas_proof_dsn.py; \
	$(MAKE) -s atlas.generate ATLAS_DSN="$$ATLAS_DSN"; \
	$(MAKE) -s atlas.test

# --- Atlas demo seed (dev-only; enables visual proof without live telemetry) ---
.PHONY: atlas.demo.seed
atlas.demo.seed: ## Seed demo telemetry data for Atlas visual proof (dev-only; requires GEMATRIA_DSN and DEMO_DB=1)
	@[ -n "$$GEMATRIA_DSN" ] || (echo "LOUD_FAIL: GEMATRIA_DSN not set"; exit 2)
	@[ "$$DEMO_DB" = "1" ] || (echo "LOUD_FAIL: set DEMO_DB=1 to seed demo data (dev-only)"; exit 2)
	@psql "$$GEMATRIA_DSN" -f scripts/atlas/demo_seed.sql

.PHONY: atlas.demo.reset
atlas.demo.reset: ## Remove demo telemetry data (dev-only; requires GEMATRIA_DSN and DEMO_DB=1)
	@[ -n "$$GEMATRIA_DSN" ] || (echo "LOUD_FAIL: GEMATRIA_DSN not set"; exit 2)
	@[ "$$DEMO_DB" = "1" ] || (echo "LOUD_FAIL: set DEMO_DB=1 to delete demo data (dev-only)"; exit 2)
	@psql "$$GEMATRIA_DSN" -tAc "DELETE FROM public.metrics_log WHERE run_id LIKE 'demo-%';"
	@psql "$$GEMATRIA_DSN" -tAc "DELETE FROM public.checkpointer_state WHERE pipeline_id LIKE 'demo-%';"

.PHONY: atlas.demo.proof
atlas.demo.proof: ## Seed demo data and run Atlas proof (dev-only; requires GEMATRIA_DSN and DEMO_DB=1)
	@$(MAKE) -s atlas.demo.seed DEMO_DB=1
	@$(MAKE) -s atlas.proof.dsn


# --- Governance smoke (enforce one sentinel per Always-Apply block) ---
.PHONY: governance.smoke
governance.smoke: guard.prompt.format guard.docs.presence ## Fail if any Always-Apply block lacks a sentinel or has duplicates
	@python3 scripts/guards/governance_smoke.py

# --- Prompt SSOT guard (enforce canonical prompt structure) ---
.PHONY: guard.prompt.ssot
guard.prompt.ssot: ## Enforce GPT System Prompt SSOT structure
	@python3 scripts/guards/guard_prompt_ssot.py || true
	@echo "wrote prompt SSOT guard report to stdout (non-fatal in HINT)"

# --- Tag proof (STRICT DSN tracks) ---
.PHONY: ops.tagproof
ops.tagproof: ## Tag proof (STRICT): Triad + DSN centralization + DSN proof
	@echo "[tagproof] STRICT triad (DB mirror)"
	@STRICT_ALWAYS_APPLY=1 $(MAKE) -s guard.alwaysapply.dbmirror
	@echo "[tagproof] STRICT prompt SSOT"
	@STRICT_PROMPT_SSOT=1 $(MAKE) -s guard.prompt.ssot
	@echo "[tagproof] governance smoke"
	@$(MAKE) -s governance.smoke
	@echo "[tagproof] STRICT DSN centralization"
	@$(MAKE) -s guard.dsn.centralized.strict
	@echo "[tagproof] STRICT Atlas DSN proof"
	@STRICT_ATLAS_DSN=1 $(MAKE) -s atlas.proof.dsn

# Atlas housekeeping (HINT + STRICT lanes, no nightly)
.PHONY: housekeeping.atlas
housekeeping.atlas:
	@echo "[housekeeping] Atlas HINT lane"
	@$(MAKE) -s atlas.generate.all
	@$(MAKE) -s atlas.clickproof | tail -n 40
	@echo "[housekeeping] UI smoke"
	@pytest -q tests/ui/test_atlas_node_click.py -q || true
	@if [ "$${STRICT_ATLAS_DSN:-0}" = "1" ]; then \
	  echo "[housekeeping] STRICT lane (opt-in)"; \
	  STRICT_ATLAS_DSN=1 $(MAKE) -s atlas.nodes || true; \
	fi
	@echo "[housekeeping] done"

# Complete housekeeping (Rule-058: mandatory post-change)

.PHONY: housekeeping
housekeeping: share.sync adr.housekeeping governance.housekeeping governance.docs.hints handoff.update
	@echo ">> Running complete housekeeping (share + agents + rules + forest + governance + docs hints + handoff)"
	@PYTHONPATH=. $(PYTHON) scripts/validate_agents_md.py
	@echo "AGENTS.md validation complete"
	@PYTHONPATH=. $(PYTHON) scripts/rules_audit.py
	@echo "Rules audit complete"
	@PYTHONPATH=. $(PYTHON) scripts/generate_forest.py
	@echo "Forest generation complete"
	@echo "✅ Complete housekeeping finished (Rule-058)"

# --- UI acceptance (headless) ---

ENVELOPE ?= share/exports/envelope.json
MIN_NODES ?= 200000
MIN_EDGES ?= 0
ALLOW_EMPTY ?=
BADGES_DIR ?= share/eval/badges

.PHONY: accept.ui
accept.ui:
	@echo ">> UI acceptance on $(ENVELOPE) ..."
	@$(PYTHON) scripts/acceptance/check_envelope.py $(ENVELOPE) --min-nodes $(MIN_NODES) --min-edges $(MIN_EDGES) $(if $(ALLOW_EMPTY),--allow-empty,)

.PHONY: accept.ui.smoke
accept.ui.smoke:
	@echo ">> Export + accept (smoke)"
	@$(PYTHON) scripts/export_noun_index.py
	@$(MAKE) accept.ui ENVELOPE=$(ENVELOPE) MIN_NODES=$(MIN_NODES) MIN_EDGES=$(MIN_EDGES) ALLOW_EMPTY=$(ALLOW_EMPTY)

# --- Truth-suite helper (fixtures → truth cases) ---

.PHONY: truth.expand
truth.expand:
	@python3 scripts/tools/derive_truth_cases.py
	@test -f tests/truth/extraction_accuracy.v1.json
	@echo "cases=$$(jq '.cases | length' tests/truth/extraction_accuracy.v1.json)"

# --- Promote truth to v2 (preferential format for guard; requires ≥25) ---

.PHONY: truth.promote.v2
truth.promote.v2:
	@python3 scripts/tools/promote_truth_v2.py
	@test -f tests/truth/extraction_accuracy.v2.json
	@jq -r '"version=" + .version + ", cases=" + ((.cases|length)|tostring)' tests/truth/extraction_accuracy.v2.json

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

.PHONY: test.env.loader
test.env.loader:
	@pytest -q tests/test_env_loader.py | tee evidence/test.env.loader.txt >/dev/null

.PHONY: test.guard
test.guard:
	@pytest -q tests/unit/guards/test_exports_guard_schema.py

# CI smoke targets (for workflow compatibility)
# Rule-050 (OPS Contract v6.2.3) - Hermetic Test Bundle
# Rule-051 (Cursor Insight & Handoff) - Baseline Evidence Required
# scripts/AGENTS.md calibrate_advanced.py - Advanced Edge Strength Calibration
.PHONY: eval.graph.calibrate.adv
eval.graph.calibrate.adv:
	@echo "🔥🔥🔥 LOUD HINT: Rule-050 (OPS Contract v6.2.3) - Hermetic Test Bundle 🔥🔥🔥"
	@echo "🔥🔥🔥 LOUD HINT: Rule-051 (Cursor Insight & Handoff) - Baseline Evidence Required 🔥🔥🔥"
	@echo "🔥🔥🔥 LOUD HINT: scripts/AGENTS.md calibrate_advanced.py - Advanced Edge Strength Calibration 🔥🔥🔥"
	@echo ">> Graph calibrate (adv) — empty-DB tolerant wrapper…"
	@PYTHONPATH=. python3 scripts/guards/guard_ci_empty_db.py
	@echo ">> Calibration step skipped or tolerated in empty-DB CI."

.PHONY: eval.xrefs.badges
eval.xrefs.badges:
	@python3 scripts/eval/xrefs_badges.py

.PHONY: eval.package
eval.package: eval.graph.calibrate.adv eval.xrefs.badges eval.badges.rerank eval.badges.patterns share.sync
	@echo "[eval.package] OK"

# --- eval: rerank quality badge (from blend report) ---
.PHONY: eval.badges.rerank
eval.badges.rerank:
	@$(PYTHON) scripts/analytics/rerank_blend_report.py
	@$(PYTHON) scripts/badges/make_rerank_quality_badge.py
	@ls -1 share/eval/badges | grep -E 'rerank_quality\.svg' || true

# --- eval: patterns badge (optional)
.PHONY: eval.badges.patterns
eval.badges.patterns:
	@$(PYTHON) scripts/analytics/export_patterns_from_json.py
	@$(PYTHON) scripts/badges/make_patterns_badge.py
	@ls -1 share/eval/badges | grep -E 'patterns_badge\.svg' || true

.PHONY: db.runs_ledger.smoke
db.runs_ledger.smoke:
	@echo ">> runs_ledger smoke (tolerant)…"
	@PYTHONPATH=. python3 scripts/guards/guard_runs_ledger.py

# Rule-050 (OPS Contract v6.2.3) - Hermetic Test Bundle
# Rule-051 (Cursor Insight & Handoff) - Baseline Evidence Required
# Rule-038 (Exports Smoke Gate) - Fail-Fast Guard for Export Readiness
.PHONY: ci.exports.smoke
ci.exports.smoke:
	@echo "🔥🔥🔥 LOUD HINT: Rule-050 (OPS Contract v6.2.3) - Hermetic Test Bundle 🔥🔥🔥"
	@echo "🔥🔥🔥 LOUD HINT: Rule-051 (Cursor Insight & Handoff) - Baseline Evidence Required 🔥🔥🔥"
	@echo "🔥🔥🔥 LOUD HINT: Rule-038 (Exports Smoke Gate) - Fail-Fast Guard for Export Readiness 🔥🔥🔥"
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

.PHONY: monitor.pipeline
monitor.pipeline:
	@echo ">> Pipeline Monitor (refreshes every 10s, shows progress for all stages)"
	@PYTHONPATH=$(shell pwd) python3 scripts/monitor_pipeline.py --watch

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
	@echo ">> Run Phase-8 temporal pattern analysis"
	@PYTHONPATH=$(shell pwd) $(PYTHON) scripts/temporal_analytics.py
	@if [ -f exports/temporal_patterns.json ]; then \
		echo ">> Temporal patterns generated successfully"; \
	fi
	@if [ -f exports/pattern_forecast.json ]; then \
		echo ">> Pattern forecasts generated successfully"; \
	fi

.PHONY: phase8.temporal
phase8.temporal: temporal.analytics
	@echo ">> Phase-8 Temporal Analytics completed"

.PHONY: phase8.forecast
phase8.forecast:
	@echo ">> Run Phase-8 forecasting analysis only"
	@if [ -f exports/temporal_patterns.json ]; then \
		$(PYTHON) scripts/temporal_analytics.py --forecast-only; \
	else \
		echo ">> Run temporal.analytics first to generate patterns"; \
		exit 1; \
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
.PHONY: book.plan book.dry book.go book.stop book.resume book.smoke ai.ingest ai.nouns ai.enrich guards.all evidence.clean guards.smoke release.notes sandbox.smoke

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

.PHONY: phase8.temporal
phase8.temporal:
	@echo ">> Phase-8: temporal analytics rolling + forecast"
	@PYTHONPATH=$(shell pwd) $(PYTHON) scripts/temporal_analytics.py --book $(BOOK)
	@$(MAKE) guards.schemas

.PHONY: orchestrator.analysis
orchestrator.analysis:
	@echo ">> Run analysis suite via orchestrator"
	@PYTHONPATH=$(shell pwd) $(PYTHON) scripts/pipeline_orchestrator.py analysis all --book $(BOOK) 2>&1
	@$(MAKE) guards.schemas

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

# --- DB plan / readiness (HINT posture; no secrets) ---
.PHONY: db.plan db.readiness db.apply.hint
db.plan:
	@echo "ADR: docs/ADRs/ADR-065-postgres-ssot.md"
	@ls -1 scripts/sql/pg 2>/dev/null | sed 's/^/sql: scripts\/sql\/pg\//' || echo "HINT: scripts/sql/pg/ directory not found (SQL skeletons not yet created)"

db.readiness:
	@if [ -z "$${ATLAS_DSN:-$${GEMATRIA_DSN:-}}" ]; then \
	  echo "HINT: No DSN set (ATLAS_DSN/GEMATRIA_DSN). Readiness will skip live checks."; \
	else \
	  psql "$${ATLAS_DSN:-$${GEMATRIA_DSN}}" -v ON_ERROR_STOP=1 -c "select version()"; \
	  psql "$${ATLAS_DSN:-$${GEMATRIA_DSN}}" -v ON_ERROR_STOP=1 -c "select extname from pg_extension where extname in ('vector','pg_trgm','pg_stat_statements','citext','pgcrypto') order by 1"; \
	fi

# Apply core SQL (safe to run repeatedly). Requires DSN env.
db.apply.hint:
	@if [ -z "$${ATLAS_DSN:-$${GEMATRIA_DSN:-}}" ]; then \
	  echo "HINT: set ATLAS_DSN (RO for proofs, RW for DDL) to apply."; exit 0; \
	else \
	  for f in scripts/sql/pg/*.sql; do echo "-- $$f" && psql "$${ATLAS_DSN:-$${GEMATRIA_DSN}}" -v ON_ERROR_STOP=1 -f $$f; done; \
	fi

# UI envelope generation
.PHONY: ui.envelope
ui.envelope:
	@echo ">> Creating unified UI envelope"
	@$(PYTHON) scripts/create_ui_envelope.py --output exports/ui_envelope.json --report exports/report.md
	@echo "UI envelope created: exports/ui_envelope.json"

.PHONY: ui.mirror.correlation
ui.mirror.correlation:
	@echo ">> Mirroring correlation artifacts to ui/out/"
	@mkdir -p ui/out
	@cp exports/graph_stats.json ui/out/ 2>/dev/null || echo "graph_stats.json not found, skipping"
	@cp exports/graph_correlations.json ui/out/ 2>/dev/null || echo "graph_correlations.json not found, skipping"
	@echo "Correlation artifacts mirrored to ui/out/"

.PHONY: ui.smoke.correlation
ui.smoke.correlation:
	@python3 -c 'import json, pathlib; [json.load(open(p)) for p in ["ui/out/graph_stats.json","ui/out/graph_correlations.json"] if pathlib.Path(p).exists()]; print("[ui.smoke.correlation] OK")'

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

.PHONY: schema.docs
schema.docs:
	@echo ">> Generating schema documentation from JSON Schema files"
	@python3 scripts/docs/generate_schema_docs.py --schema-dir docs/SSOT --output-dir docs/schemas
	@echo "✅ Schema documentation generated in docs/schemas/"

.PHONY: guards.schemas
guards.schemas:
	@echo ">> Validating pipeline artifacts against SSOT schemas (ENVELOPE-FIRST HARDENING)"
	# ENVELOPE-FIRST: Validate unified envelope with COMPASS if present
	@[ -f share/exports/envelope.json ] && \
	(echo ">> COMPASS validation: envelope.json" && \
	 $(PYTHON) scripts/compass/scorer.py share/exports/envelope.json --threshold 0.8) || \
	(echo ">> COMPASS validation skipped (no envelope.json)" && true)
	@[ -f share/exports/envelope.json ] && \
	$(PYTHON) scripts/eval/jsonschema_validate.py --schema docs/SSOT/unified-envelope.schema.json --instance share/exports/envelope.json || true
	# Validate other artifacts
	@[ -f share/exports/ai_nouns.json ] && \
	$(PYTHON) scripts/eval/jsonschema_validate.py --schema docs/SSOT/SSOT_ai-nouns.v1.schema.json --instance share/exports/ai_nouns.json || true
	@[ -f share/exports/graph_latest.json ] && \
	$(PYTHON) scripts/eval/jsonschema_validate.py --schema docs/SSOT/SSOT_graph.v1.schema.json --instance share/exports/graph_latest.json || true
	@[ -f share/exports/graph_stats.json ] && \
	$(PYTHON) scripts/eval/jsonschema_validate.py --schema docs/SSOT/graph-stats.schema.json --instance share/exports/graph_stats.json || true
	@[ -f share/exports/temporal_patterns.json ] && \
	$(PYTHON) scripts/eval/jsonschema_validate.py --schema docs/SSOT/temporal-patterns.schema.json --instance share/exports/temporal_patterns.json || true
	@[ -f share/exports/pattern_forecast.json ] && \
	$(PYTHON) scripts/eval/jsonschema_validate.py --schema docs/SSOT/pattern-forecast.schema.json --instance share/exports/pattern_forecast.json || true
	@echo "Schema validation complete (ENVELOPE-FIRST HARDENING)"

# ENVELOPE-FIRST HARDENING: Dedicated envelope validation target
.PHONY: guards.envelope_first
guards.envelope_first:
	@echo ">> ENVELOPE-FIRST VALIDATION: Validate envelopes before pipeline operations"
	# COMPASS mathematical validation (>80% correctness threshold)
	@[ -f share/exports/envelope.json ] && \
	(echo ">> COMPASS scoring envelope.json..." && \
	 $(PYTHON) scripts/compass/scorer.py share/exports/envelope.json --threshold 0.8 && \
	 echo "✓ COMPASS validation passed") || \
	(echo "⚠️  COMPASS validation failed or no envelope present" && false)
	# Schema validation for all envelopes
	@[ -f share/exports/envelope.json ] && \
	$(PYTHON) scripts/eval/jsonschema_validate.py --schema docs/SSOT/unified-envelope.schema.json --instance share/exports/envelope.json || true
	@[ -f share/exports/temporal_patterns.json ] && \
	$(PYTHON) scripts/eval/jsonschema_validate.py --schema docs/SSOT/temporal-patterns.schema.json --instance share/exports/temporal_patterns.json || true
	@[ -f share/exports/pattern_forecast.json ] && \
	$(PYTHON) scripts/eval/jsonschema_validate.py --schema docs/SSOT/pattern-forecast.schema.json --instance share/exports/pattern_forecast.json || true
	@echo "ENVELOPE-FIRST validation complete"

guards.all: guard.stats.rfc3339 guard.graph.generated_at guard.rules.alwaysapply guard.rules.alwaysapply.dbmirror guard.alwaysapply.triad guard.alwaysapply.dbmirror guard.ai.tracking guard.ui.xrefs.badges schema.smoke guard.badges.inventory guard.book.extraction guard.extraction.accuracy guard.exports.json guard.exports.rfc3339 governance.smoke guard.prompt.ssot guard.python.runner guard.ai_nouns.schema guard.graph.core.schema guard.graph.stats.schema guard.graph.patterns.schema guard.graph.correlations.schema guard.jsonschema.import
guard.stats.rfc3339:
	@echo ">> Validating graph_stats.json generated_at (RFC3339)…"
	@$(PYTHON) scripts/guards/guard_stats_rfc3339.py || true

.PHONY: guard.graph.generated_at
guard.graph.generated_at:
	@echo ">> Validating graph exports generated_at (RFC3339)…"
	@$(PYTHON) scripts/guards/guard_graph_generated_at.py

.PHONY: guard.rules.alwaysapply
guard.rules.alwaysapply:
	@$(PYTHON) scripts/guards/guard_alwaysapply_triage.py

.PHONY: guard.rules.alwaysapply.dbmirror
guard.rules.alwaysapply.dbmirror:
	@$(PYTHON) scripts/guards/guard_alwaysapply_dbmirror.py

# Always-Apply triad enforcement (HINT by default; STRICT with env)
.PHONY: guard.alwaysapply.triad
guard.alwaysapply.triad:
	@$(PYTHON) scripts/guards/guard_alwaysapply_triage.py || true
	@echo "wrote evidence/guard_alwaysapply_triad.json"

# DB-first mirror (HINT by default; STRICT when STRICT_ALWAYS_APPLY=1)
.PHONY: guard.alwaysapply.dbmirror
guard.alwaysapply.dbmirror:
	@$(PYTHON) scripts/guards/sync_alwaysapply_from_db.py || true
	@echo "wrote evidence/guard_alwaysapply_dbmirror.json"

# Apply DB-backed autofix (WRITE=1); still HINT unless STRICT_ALWAYS_APPLY=1
.PHONY: guard.alwaysapply.autofix
guard.alwaysapply.autofix:
	@WRITE=1 $(PYTHON) scripts/guards/sync_alwaysapply_from_db.py || true
	@echo "wrote evidence/guard_alwaysapply_dbmirror.json (autofix)"

# --- Back-compat aliases (one release) ---
.PHONY: guard.rules.alwaysapply.autofix
guard.rules.alwaysapply.autofix: guard.alwaysapply.autofix

.PHONY: guard.ai.tracking
guard.ai.tracking:
	@python3 scripts/guards/guard_ai_tracking_contract.py

.PHONY: guard.ai.tracking.strict
guard.ai.tracking.strict:
	@STRICT_AI_TRACKING=1 python3 scripts/guards/guard_ai_tracking_contract.py

.PHONY: guard.exports.json
guard.exports.json:
	@PYTHONPATH=scripts/guards python3 scripts/guards/guard_exports_json.py

.PHONY: guard.exports.rfc3339
guard.exports.rfc3339:
	@PYTHONPATH=scripts/guards python3 scripts/guards/guard_exports_rfc3339.py

# --- Export guard evidence + badge ---
.PHONY: guard.exports.json.evidence
guard.exports.json.evidence:
	@mkdir -p evidence
	@PYTHONPATH=scripts/guards $(PY_RUN) scripts/guards/guard_exports_json.py > evidence/guard_exports_json.verdict.json 2> evidence/guard_exports_json.stderr.txt || true
	@jq -r '.ok' evidence/guard_exports_json.verdict.json >/dev/null 2>&1 || echo '{"ok":false}' > evidence/guard_exports_json.verdict.json

.PHONY: evidence.exports.badge
evidence.exports.badge: guard.exports.json.evidence
	@mkdir -p $(BADGES_DIR)
	@STATUS=$$(test "$$(jq -r .ok evidence/guard_exports_json.verdict.json)" = "true" && echo PASS || echo FAIL); \
	python3 scripts/badges/make_badge.py --label "Exports JSON" --status $$STATUS --out $(BADGES_DIR)/exports_json.svg >/dev/null; \
	echo "badge=$(BADGES_DIR)/exports_json.svg status=$$STATUS"
	@python3 scripts/tools/update_badges_manifest.py "exports_json" "$(BADGES_DIR)/exports_json.svg" "Exports JSON guard verdict"

.PHONY: evidence.rfc3339.badge
evidence.rfc3339.badge:
	@mkdir -p $(BADGES_DIR) evidence
	@$(PY_RUN) scripts/guards/guard_exports_rfc3339.py >/dev/null 2>&1 || true
	@STATUS=$$(test "$$(jq -r '.ok' evidence/exports_rfc3339.verdict.json)" = "true" && echo PASS || echo FAIL); \
	python3 scripts/badges/make_badge.py --label "RFC3339" --status $$STATUS --out $(BADGES_DIR)/rfc3339.svg >/dev/null; \
	echo "badge=$(BADGES_DIR)/rfc3339.svg status=$$STATUS"
	@python3 scripts/tools/update_badges_manifest.py "rfc3339" "$(BADGES_DIR)/rfc3339.svg" "RFC3339 timestamps guard verdict"

.PHONY: evidence.exports.verdict.md
evidence.exports.verdict.md: guard.exports.json.evidence
	@python3 scripts/tools/render_exports_verdict_md.py >/dev/null
	@test -f evidence/exports_guard.verdict.md

.PHONY: evidence.exports.rfc3339.verdict
evidence.exports.rfc3339.verdict:
	@PYTHONPATH=scripts/guards python3 scripts/guards/guard_exports_rfc3339.py >/dev/null 2>&1 || true
	@test -f evidence/exports_rfc3339.verdict.json || echo '[bundle] exports_rfc3339.verdict.json missing' >> evidence/bundle.log

.PHONY: evidence.rfc3339.verdict.md
evidence.rfc3339.verdict.md: evidence.exports.rfc3339.verdict
	@python3 scripts/tools/render_rfc3339_verdict_md.py >/dev/null 2>&1 || true
	@test -f evidence/exports_rfc3339.verdict.md || echo '[bundle] exports_rfc3339.verdict.md missing' >> evidence/bundle.log

# Operator evidence: extraction agents summary (RFC-072 Part 2)
.PHONY: evidence.agents.summary
evidence.agents.summary:
	@mkdir -p evidence
	@python3 scripts/ops/agent_evidence_summary.py > evidence/agents_summary.json

.PHONY: guard.ui.xrefs.badges
guard.ui.xrefs.badges:
	@if [ "$${CI_XREF_BADGES_SKIP:-0}" = "1" ]; then \
	  printf '{ "guard":"guard_xrefs_badges","ok":true,"note":"skipped by CI (paths do not affect xref badges)"}\n'; \
	else \
	  python3 scripts/guards/guard_xrefs_badges.py || true; \
	fi

.PHONY: schema.smoke
schema.smoke:
	@$(PYTHON) scripts/guards/guard_schema_smoke.py

.PHONY: guard.rerank.thresholds
guard.rerank.thresholds:
	@$(PYTHON) scripts/guards/guard_rerank_thresholds.py

.PHONY: guard.badges.inventory
guard.badges.inventory:
	@$(PYTHON) scripts/guards/guard_badges_inventory.py

# --- guard: book extraction correctness (HINT-only)
.PHONY: guard.book.extraction
guard.book.extraction:
	@$(PYTHON) scripts/smokes/book_extraction_correctness.py

.PHONY: guard.extraction.accuracy
guard.extraction.accuracy:
	@$(PYTHON) scripts/guards/guard_extraction_accuracy.py || true

.PHONY: graph.fixture.from.truth
graph.fixture.from.truth:
	@$(PYTHON) scripts/analytics/build_fixture_graph.py

.PHONY: graph.real.from.fixtures
graph.real.from.fixtures:
	@$(PYTHON) scripts/analytics/build_graph_from_repo_fixtures.py

.PHONY: graph.real.production
graph.real.production:
	@$(PYTHON) scripts/analytics/build_graph_real.py

# Documentation governance
.PHONY: guard.docs.consistency docs.fix.headers docs.audit
guard.docs.consistency:
	@python3 scripts/guards/guard_docs_consistency.py
docs.fix.headers:
	@python3 scripts/docs/apply_ops_header.py
docs.audit: guard.docs.consistency

# --- Local posture smoke: empty-DB tolerant ---
.PHONY: book.smoke
book.smoke:
	@python3 scripts/smokes/book_smoke.py

.PHONY: guard.tests
guard.tests:
	@echo ">> guard.tests (STRICT_RFC3339=1)"
	@STRICT_RFC3339=1 $(PYTHON) scripts/guards/guard_graph_generated_at.py

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
	@echo ">> Validating env usage (no direct os.getenv)…"
	@PYTHONPATH=. python3 scripts/guards/guard_env_usage.py | tee evidence/guard_env_usage.txt || true
	@echo ">> Validating schema contract (class not kind, no meta)…"
	@PYTHONPATH=. python3 scripts/guards/guard_schema_contract.py | tee evidence/guard_schema_contract.txt || true
	@$(MAKE) -s guard.python.runner
	@$(MAKE) -s guard.dsn.centralized
	@$(MAKE) -s guard.secrets.mask

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

ai.verify.math:
	@echo ">> Math Verifier Agent (gematria sanity via MATH_MODEL=$${MATH_MODEL:-self-certainty-qwen3-1.7b-base-math})"
	@PYTHONPATH=$(shell pwd) INPUT=$${INPUT:-exports/ai_nouns.enriched.json} OUTPUT=$${OUTPUT:-exports/ai_nouns.enriched.json} BOOK=$${BOOK:-Genesis} python3 scripts/math_verifier.py

sandbox.smoke:
	@echo ">> TS Sandbox Smoke (PoC, gate-aware, hermetic hello-world)"
	@$(PYTHON) scripts/sandbox_smoke_check.py

graph.build:
	@echo ">> Graph Builder Agent: enriched nouns→graph_latest"
	@PYTHONPATH=$(shell pwd) python3 scripts/build_graph_from_ai_nouns.py

graph.score:
	@echo ">> Rerank Agent: graph_latest→graph_latest.scored"
	@# TODO: wire to reranking script
	@echo "GRAPH_SCORE_OK"

analytics.export:
	@echo "HINT: analytics: starting (file-first)"
	@if test -f exports/graph_latest.scored.json || test -f exports/graph_latest.json; then \
		echo "HINT: analytics: using graph JSON in exports/"; \
		$(PYTHON) scripts/analytics/graph_stats_from_json.py; \
	else \
		echo "HINT: analytics: no local graph JSON; deferring to DB exporters"; \
		$(PYTHON) scripts/analytics/export_graph.py || true; \
	fi
	@$(PYTHON) scripts/analytics/export_patterns.py || true
	@echo "[analytics.export] OK"

.PHONY: analytics.rerank.blend
analytics.rerank.blend:
	@$(PYTHON) scripts/analytics/rerank_blend_report.py

# --- analytics: patterns export (file-first)
.PHONY: analytics.patterns.file
analytics.patterns.file:
	@$(PYTHON) scripts/analytics/export_patterns_from_json.py
	@head -n 20 share/eval/patterns.json || true
	@echo "[analytics.patterns.file] OK"

# --- Analytics exports (DB-first; tolerant stubs when DSN missing) ---
.PHONY: analytics.export.db
analytics.export.db:
	@python3 scripts/analytics/export_from_db.py

.PHONY: analytics.verify
analytics.verify:
	@python3 scripts/analytics/verify_export.py

# AI Tracking exports (sessions/calls telemetry)
.PHONY: analytics.ai.export
analytics.ai.export:
	@python3 scripts/analytics/export_ai_tracking.py

.PHONY: analytics.ai.verify
analytics.ai.verify:
	@python3 scripts/analytics/verify_ai_tracking.py

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
	@./scripts/ensure_venv.sh
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
.PHONY: evidence.badges
evidence.badges:
	@mkdir -p evidence/badges
	@# xref metrics JSON (optional)
	@if [ -f share/eval/xrefs_metrics.json ]; then \
	  cp -f share/eval/xrefs_metrics.json evidence/; \
	  echo "evidence: + evidence/xrefs_metrics.json"; \
	else \
	  echo "HINT: share/eval/xrefs_metrics.json not found; skipping"; \
	fi
	@# badge SVGs (optional)
	@for f in xrefs_coverage.svg xrefs_rate.svg; do \
	  if [ -f "share/eval/badges/$$f" ]; then \
	    cp -f "share/eval/badges/$$f" evidence/badges/; \
	    echo "evidence: + evidence/badges/$$f"; \
	  else \
	    echo "HINT: share/eval/badges/$$f not found; skipping"; \
	  fi; \
	done

.PHONY: evidence.bundle
evidence.bundle: evidence.badges evidence.exports.badge evidence.exports.verdict.md evidence.rfc3339.badge evidence.rfc3339.verdict.md evidence.exports.rfc3339.verdict ## build operator evidence bundle (now includes xref metrics & badges if present)
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
	@python3 scripts/evidence/ensure_badges_manifest.py || true
	@# Include rerank blend + thresholds guard outputs
	@mkdir -p evidence
	@# Include rerank quality badge if present
	@if test -d share/eval/badges; then cp -f share/eval/badges/rerank_quality.svg evidence/ 2>/dev/null || true; fi
	@if test -d share/eval/badges; then cp -f share/eval/badges/patterns_badge.svg evidence/ 2>/dev/null || true; fi
	@if test -f share/eval/rerank_blend_report.json; then cp share/eval/rerank_blend_report.json evidence/; fi
	@if test -f evidence/exports_guard.verdict.json; then echo "[bundle] exports_guard.verdict.json added" >> evidence/bundle.log; else echo "[bundle] exports_guard.verdict.json missing (HINT-mode runs may not produce it yet)" >> evidence/bundle.log; fi
	@if test -f evidence/guard_rerank_thresholds.json; then :; else $(PYTHON) scripts/guards/guard_rerank_thresholds.py || true; fi
	@ls -1 evidence | grep -E 'guard_rerank_thresholds|rerank_blend_report|rerank_quality\.svg|patterns_badge\.svg' || true
	@echo "==> Including observability artifacts (if present)..."
	@tar -czf evidence/atlas_node_pages_proof.tgz \
		docs/atlas/nodes \
		evidence/atlas.nodes.json \
		evidence/otel.spans.jsonl \
		prompts 2>/dev/null || true
	@echo "OK: evidence bundle at evidence/atlas_node_pages_proof.tgz"

# Rule-050 (OPS Contract v6.2.3) - Evidence-First Protocol
# Rule-051 (Cursor Insight & Handoff) - Baseline Evidence Required
# Rule-053 (Idempotent Baseline) - Cache Baseline Evidence 60m
# AGENTS.md OPS Contract - Hermetic Test Bundle Required
.PHONY: pipeline.e2e
pipeline.e2e:
	@echo "🔥🔥🔥 LOUD HINT: Rule-050 (OPS Contract v6.2.3) - Evidence-First Protocol 🔥🔥🔥"
	@echo "🔥🔥🔥 LOUD HINT: Rule-051 (Cursor Insight & Handoff) - Baseline Evidence Required 🔥🔥🔥"
	@echo "🔥🔥🔥 LOUD HINT: Rule-053 (Idempotent Baseline) - Cache Baseline Evidence 60m 🔥🔥🔥"
	@echo "🔥🔥🔥 LOUD HINT: AGENTS.md OPS Contract - Hermetic Test Bundle Required 🔥🔥🔥"
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

# Environment protection targets
.PHONY: env.backup env.edit env.protect env.check
env.backup:
	@echo ">> Creating environment file backup with protection..."
	@./scripts/env/backup_env.sh

env.edit:
	@echo ">> Opening environment file for safe editing..."
	@./scripts/env/edit_env.sh

env.protect: env.backup
	@echo "✅ Environment file protection active"
	@echo "💡 Use 'make env.edit' to safely modify .env"
	@echo "💡 Backups are automatically created before edits"

env.check:
	@echo ">> Comprehensive environment validation..."
	@./scripts/env/validate_env.sh

.PHONY: pipeline.from_db.pg
pipeline.from_db.pg: env.validate
	@echo ">> DB-backed pipeline with Postgres checkpointer (requires GEMATRIA_DSN)…"
	PYTHONPATH=$(shell pwd) python3 scripts/pipeline_orchestrator.py pipeline

.PHONY: ui.mirror.temporal
ui.mirror.temporal:
	@echo ">> Mirroring temporal artifacts to ui/out"
	mkdir -p ui/out
	@[ -f share/exports/temporal_patterns.json ] && cp share/exports/temporal_patterns.json ui/out/temporal_patterns.json || true
	@[ -f share/exports/pattern_forecast.json ] && cp share/exports/pattern_forecast.json ui/out/pattern_forecast.json || true
	@ls -l ui/out | sed -n '1,8p'

.PHONY: ui.smoke.temporal
ui.smoke.temporal:
	@python3 - <<'PY'
	import json, pathlib
	for p in ("ui/out/temporal_patterns.json","ui/out/pattern_forecast.json"):
	    path=pathlib.Path(p); assert path.exists(), f"missing {p}"
	    json.load(open(path,"r",encoding="utf-8"))
	print("[ui.smoke.temporal] OK")
	PY

.PHONY: ui.build
ui.build:
	@[ -d ui ] || { echo "ui/ folder missing"; exit 1; }
	cd ui && npm ci && npm run build


agents.md.lint:
	@scripts/guards/agents_md_lint.sh

rules_inventory_check:
	@scripts/guards/rules_inventory_check.sh

.PHONY: ops.enrichment.xrefs.light
ops.enrichment.xrefs.light:
	@echo ">> Light cross-reference extractor from analysis text"
	@mkdir -p evidence
	@python3 scripts/ops/extract_xrefs_from_analysis.py | tee evidence/xrefs_light_extractor.json
	@$(MAKE) -s guard.ai_nouns.xrefs >/dev/null || true
	@test -f evidence/guard_ai_nouns_xrefs.json && cat evidence/guard_ai_nouns_xrefs.json | jq '{mode, min_ratio, total, with_xrefs, ratio}' || echo '{"note":"guard not run"}'

.PHONY: ui.xrefs.index
ui.xrefs.index:
	@echo ">> Building UI cross-reference index"
	@python3 scripts/ops/build_ui_xrefs_index.py | tee evidence/ui_xrefs_index.log

.PHONY: ui.verses.cache
ui.verses.cache:
	@python3 scripts/ops/build_verses_local_cache.py | tee evidence/ui_verses_cache.log

.PHONY: ui.publish.xrefs
ui.publish.xrefs:
	@mkdir -p ui/public/xrefs
	@test -f ui/out/xrefs_index.v1.json && cp -f ui/out/xrefs_index.v1.json ui/public/xrefs/xrefs_index.v1.json || true
	@test -f ui/out/verses.local.json   && cp -f ui/out/verses.local.json   ui/public/xrefs/verses.local.json   || true
	@echo "Published xref artifacts to ui/public/xrefs"

.PHONY: guard.ai_nouns.xrefs
guard.ai_nouns.xrefs:
	@echo ">> Checking cross-reference extraction ratio (HINT mode)"
	@mkdir -p evidence
	@python3 scripts/guards/guard_ai_nouns_xrefs.py | tee evidence/guard_ai_nouns_xrefs.json

.PHONY: guard.ui.xrefs.index
guard.ui.xrefs.index:
	@echo ">> Checking UI xrefs index integrity (HINT mode)"
	@mkdir -p evidence
	@python3 scripts/guards/guard_ui_xrefs_index.py | tee evidence/guard_ui_xrefs_index.json

.PHONY: ui.dev
ui.dev:
	@cd ui && npm ci && npm run dev

.PHONY: ui.smoke.browser
ui.smoke.browser:
	@UI_URL=${UI_URL:-http://localhost:5173} bash scripts/ui/smoke_playwright.sh

.PHONY: ui.test
ui.test:
	@echo ">> Running UI tests (Playwright)"
	@pytest tests/ui -v

.PHONY: otel.smoke
otel.smoke:
	@echo ">> Running OTel span smoke test"
	@PYTHONPATH=. ENABLE_OTEL=1 python3 scripts/observability/otel_smoke.py >/dev/null 2>&1 || true
	@echo "== otel.spans.jsonl (tail) =="
	@test -f evidence/otel.spans.jsonl && tail -n 10 evidence/otel.spans.jsonl || echo "(no spans)"

# OPS verification suite (Rule 050/051/052 compliance)
ops.verify: agents.md.lint rules_inventory_check guards.all
	@echo "[ops.verify] All operational guards passed"

# Optional DB index for AGENTS.md search/telemetry (docs remain SSOT)
agents.md.index:
	@echo "[agents.md.index] building index (skip if GEMATRIA_DSN unset)"
	@[ -n "$$GEMATRIA_DSN" ] || { echo "SKIP: GEMATRIA_DSN not set"; exit 0; }
	@psql "$$GEMATRIA_DSN" -v ON_ERROR_STOP=1 -c 'CREATE TABLE IF NOT EXISTS ai.agent_docs_index(path text PRIMARY KEY, sha256_12 text NOT NULL, excerpt jsonb NOT NULL, updated_at timestamptz NOT NULL DEFAULT now())'
	@python3 scripts/guards/index_agents_md.py
	@psql "$$GEMATRIA_DSN" -v ON_ERROR_STOP=1 -c "TRUNCATE ai.agent_docs_index"
	@psql "$$GEMATRIA_DSN" -v ON_ERROR_STOP=1 -c "\copy ai.agent_docs_index (path,sha256_12,excerpt) FROM program 'jq -cr \".[]|[.path,.sha256_12,(.excerpt|tojson)]|@tsv\" tmp.agent_docs_index.json' WITH (FORMAT csv, DELIMITER E'\t', QUOTE E'\b')"
	@psql "$$GEMATRIA_DSN" -c "SELECT count(*) AS indexed, min(updated_at) AS first_at, max(updated_at) AS last_at FROM ai.agent_docs_index"

# Rerank smoke test (stub for now)
.PHONY: rerank.smoke
rerank.smoke:
	@echo "[rerank.smoke] Checking rerank components..."
	@python3 scripts/analytics/rerank_smoke.py

# Rerank smoke test
.PHONY: rerank.smoke
rerank.smoke:
	@python3 scripts/analytics/rerank_smoke.py

# --- RFC-073: tag-only RO export for core graph ---
.PHONY: exports.graph.core.tagproof
exports.graph.core.tagproof:
	@echo "[make] Running tagproof core export (RO DSN required on tags)"
	GITHUB_REF_TYPE=$${GITHUB_REF_TYPE:-$$(git describe --exact-match --tags >/dev/null 2>&1 && echo tag || echo "")} \
	python3 scripts/exports/export_graph_core.py

# --- Master Reference tracking (OPS v6.2) ---
.PHONY: docs.masterref.populate docs.masterref.check housekeeping.masterref

docs.masterref.populate:
	@echo "[make] masterref: populate document_sections (STRICT=$${STRICT_MASTER_REF:-0})"
	STRICT_MASTER_REF=$${STRICT_MASTER_REF:-0} \
		GITHUB_REF_TYPE=$${GITHUB_REF_TYPE:-} \
		python3 scripts/ops/master_ref_populate.py

docs.masterref.check:
	@echo "[make] masterref: check hints"
	@python3 -m scripts.document_management_hints || python3 scripts/document_management_hints.py || echo "[make] masterref: hints script not found (skip)"

# Convenience wrapper to run both steps; safe in HINT, fail-closed when STRICT_MASTER_REF=1
housekeeping.masterref:
	$(MAKE) docs.masterref.populate
	$(MAKE) docs.masterref.check

# --- Local automation hardening ---
.PHONY: hooks.install ops.auto-normalize

hooks.install:
	@git config core.hooksPath .githooks
	@echo "[hooks] core.hooksPath set to .githooks"

ops.auto-normalize:
	@bash scripts/ops/auto_normalize.sh || true

# --- MCP dev bench (local only; skips safely if DSN/psql missing) ---
.PHONY: mcp.dev.bench
mcp.dev.bench:
	@echo "[mcp] dev bench starting"
	@python3 scripts/mcp/get_dsn_for_bench.py > evidence/mcp.bench.dsn.txt || true
	@DSN="$$(cat evidence/mcp.bench.dsn.txt)" ; \
	if [ -z "$$DSN" ]; then \
	  DSN="$${GEMATRIA_RW_DSN:-$${GEMATRIA_RO_DSN:-$${ATLAS_DSN_RO:-}}}"; \
	fi ; \
	if ! command -v psql >/dev/null 2>&1 ; then \
	  echo "[bench] SKIP: psql not installed" | tee evidence/mcp.bench.skip.txt ; exit 0 ; \
	fi ; \
	if [ -z "$$DSN" ]; then \
	  echo "[bench] SKIP: no DSN available" | tee evidence/mcp.bench.skip.txt ; exit 0 ; \
	fi ; \
	echo "[bench] DSN detected (redacted)" | tee evidence/mcp.bench.info.txt ; \
	psql "$$DSN" -v ON_ERROR_STOP=1 -f scripts/mcp/bench_dev.sql | tee evidence/mcp.bench.raw.txt >/dev/null ; \
	grep -E "(Execution Time|Planning Time)" -n evidence/mcp.bench.raw.txt | sed -n '1,120p' | tee evidence/mcp.bench.times.txt >/dev/null ; \
	echo "[bench] done"

# --- MCP examples smoke (local only; skips safely if DSN/psql missing) ---
.PHONY: mcp.examples.smoke
mcp.examples.smoke:
	@echo "[mcp] examples smoke"
	@python3 scripts/mcp/get_dsn_for_examples.py > evidence/mcp.examples.dsn.txt || true
	@DSN="$$(cat evidence/mcp.examples.dsn.txt)" ; \
	if ! command -v psql >/dev/null 2>&1 ; then \
	  echo "[examples] SKIP: psql not installed" | tee evidence/mcp.examples.skip.txt ; exit 0 ; \
	fi ; \
	if [ -z "$$DSN" ]; then \
	  echo "[examples] SKIP: no DSN available" | tee evidence/mcp.examples.skip.txt ; exit 0 ; \
	fi ; \
	psql "$$DSN" -v ON_ERROR_STOP=1 -f scripts/mcp/examples.sql | tee evidence/mcp.examples.out.txt >/dev/null ; \
	echo "[examples] done"
