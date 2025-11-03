

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
MIN_NODES ?= 1
MIN_EDGES ?= 0
ALLOW_EMPTY ?=

.PHONY: accept.ui
accept.ui:
	@echo ">> UI acceptance on $(ENVELOPE) ..."
	@$(PYTHON) scripts/acceptance/check_envelope.py $(ENVELOPE) --min-nodes $(MIN_NODES) --min-edges $(MIN_EDGES) $(if $(ALLOW_EMPTY),--allow-empty,)

.PHONY: accept.ui.smoke
accept.ui.smoke:
	@echo ">> Export + accept (smoke)"
	@$(PYTHON) scripts/export_noun_index.py --limit 1000
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

# COMPASS evaluation (mathematical correctness scoring)
ENVELOPE ?= share/exports/envelope.json

.PHONY: test.compass
test.compass:
	@echo ">> COMPASS evaluation on $(ENVELOPE)"
	@python3 scripts/compass/scorer.py $(ENVELOPE) --verbose

# Quick plan viewer (local-only convenience)
.PHONY: plan
plan:
	@if ls .cursor/plans/*.plan.md 1> /dev/null 2>&1; then \
		cat .cursor/plans/*.plan.md | head -100; \
		echo ""; \
		echo "[Full plan: $$(ls .cursor/plans/*.plan.md)]"; \
	else \
		echo "No active plan found in .cursor/plans/"; \
		echo ""; \
		echo "## Phase 11 Breadcrumb (Current Status)"; \
		echo "*Sprint 1 forks resolved: 1d unified pipeline (graph + temporal + correlations), 2a modern-minimalist UI, 3a virtual scrolling + chunked rendering for large datasets, 4d dual performance/metrics views (user badges + dev debug panel)."; \
		echo "*Success criteria for stub: extract stub generates ≥10 000 nodes in <2 sec, GraphPreview logs 'Chunked rendering' for >10 k nodes."; \
		echo "*Badge thresholds defined: Green <200 ms, Yellow <500 ms, Red ≥500 ms."; \
		echo "*Fallback decision: if UI render time >3 sec for 50 k nodes, escalate to WebGL (Sprint 3)."; \
		echo "*COMPASS thresholds: >80% correctness (>0.5 weights, edge blend 0.5*cos+0.5*rerank, temporal integrity)."; \
	fi

# PR automation checks (non-blocking)
.PHONY: pr.check.model-usage
pr.check.model-usage: ## Check if PR description contains "Model Usage" block
	@if [ -z "$(PR_NUM)" ]; then echo "Usage: make pr.check.model-usage PR_NUM=<number>"; exit 1; fi
	@echo ">> Checking PR #$(PR_NUM) for 'Model Usage' block..."
	@gh pr view $(PR_NUM) --json body --jq '.body' | grep -q "Model Usage" && echo "✅ Model Usage block found" || echo "⚠️  Model Usage block missing (advisory)"

.PHONY: docs.links
docs.links: ## Check for broken documentation links (lychee-style)
	@echo ">> Checking documentation links..."
	@if command -v lychee >/dev/null 2>&1; then \
		find docs/ -name "*.md" -exec lychee --exclude-mail {} \;; \
	else \
		echo "⚠️  lychee not installed, skipping link check"; \
	fi

# UI acceptance harness (headless a11y + perf, emits artifacts)
UI_ACCEPT_OUTDIR ?= ui/accept
UI_ACCEPT_URL ?= http://localhost:3000
UI_ACCEPT_TIMEOUT ?= 10000

.PHONY: ui.accept
ui.accept: ## Run headless UI acceptance tests (a11y + perf), emit md/json artifacts
	@echo ">> UI acceptance harness: a11y + performance checks"
	@mkdir -p $(UI_ACCEPT_OUTDIR)
	@echo "# UI Acceptance Report" > $(UI_ACCEPT_OUTDIR)/report.md
	@echo "- **Timestamp**: $$(date)" >> $(UI_ACCEPT_OUTDIR)/report.md
	@echo "- **URL**: $(UI_ACCEPT_URL)" >> $(UI_ACCEPT_OUTDIR)/report.md
	@echo "- **Timeout**: $(UI_ACCEPT_TIMEOUT)ms" >> $(UI_ACCEPT_OUTDIR)/report.md
	@echo "" >> $(UI_ACCEPT_OUTDIR)/report.md
	@if command -v lighthouse >/dev/null 2>&1; then \
		echo "## Lighthouse Performance" >> $(UI_ACCEPT_OUTDIR)/report.md; \
		lighthouse $(UI_ACCEPT_URL) --output=json --output-path=$(UI_ACCEPT_OUTDIR)/lighthouse.json --quiet --chrome-flags="--headless --no-sandbox" || echo "⚠️  Lighthouse failed (server not running?)" >> $(UI_ACCEPT_OUTDIR)/report.md; \
	else \
		echo "⚠️  Lighthouse not installed, install with: npm install -g lighthouse" >> $(UI_ACCEPT_OUTDIR)/report.md; \
	fi
	@if command -v pa11y >/dev/null 2>&1; then \
		echo "## Accessibility (pa11y)" >> $(UI_ACCEPT_OUTDIR)/report.md; \
		pa11y --reporter json $(UI_ACCEPT_URL) > $(UI_ACCEPT_OUTDIR)/a11y.json 2>/dev/null && echo "✅ pa11y completed" >> $(UI_ACCEPT_OUTDIR)/report.md || echo "⚠️  pa11y failed (server not running?)" >> $(UI_ACCEPT_OUTDIR)/report.md; \
	else \
		echo "⚠️  pa11y not installed, install with: npm install -g pa11y" >> $(UI_ACCEPT_OUTDIR)/report.md; \
	fi
	@echo "## Load Time Check" >> $(UI_ACCEPT_OUTDIR)/report.md
	@if command -v curl >/dev/null 2>&1; then \
		load_time=$$(curl -o /dev/null -s -w "%{time_total}" $(UI_ACCEPT_URL) 2>/dev/null || echo "0"); \
		if [ "$$load_time" != "0" ]; then \
			echo "- **Total load time**: $${load_time}s" >> $(UI_ACCEPT_OUTDIR)/report.md; \
			if python3 -c "import sys; sys.exit(0 if float('$$load_time') < 3.0 else 1)"; then \
				echo "- **Status**: ✅ Under 3s threshold" >> $(UI_ACCEPT_OUTDIR)/report.md; \
			else \
				echo "- **Status**: ⚠️  Over 3s threshold" >> $(UI_ACCEPT_OUTDIR)/report.md; \
			fi; \
		else \
			echo "- **Status**: ⚠️  Server not responding" >> $(UI_ACCEPT_OUTDIR)/report.md; \
		fi; \
	else \
		echo "- **Status**: ⚠️  curl not available" >> $(UI_ACCEPT_OUTDIR)/report.md; \
	fi
	@echo ">> Artifacts emitted to $(UI_ACCEPT_OUTDIR)/:" && ls -la $(UI_ACCEPT_OUTDIR)/
