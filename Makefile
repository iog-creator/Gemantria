

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

# UI temporal export targets (local-only)

OUTDIR ?= ui/out

ui.export.temporal.span:
	@echo ">> Temporal strip export (span mode) to $(OUTDIR)"
	@$(PYTHON) scripts/ui/export_temporal_strip.py $(ENVELOPE) --outdir $(OUTDIR) --mode span

# --- Publish temporal artifacts to public/ with versioned names ---

PUBLIC_DIR ?= webui/public
VERSION ?=

.PHONY: ui.publish.temporal
ui.publish.temporal:
	@echo ">> Publish temporal exports to $(PUBLIC_DIR) (version=$(VERSION))"
	@$(PYTHON) scripts/ui/copy_exports.py --src $(OUTDIR) --dst $(PUBLIC_DIR) $(if $(VERSION),--version $(VERSION),)

# --- PR metadata enforcement (local)

.PHONY: pr.check.model_usage
pr.check.model_usage:
	@$(PYTHON) scripts/ci/check_pr_model_usage.py

# --- P11 acceptance: perf, a11y, metrics (local-only) ---

.PHONY: ui.perf.load
ui.perf.load:
	@echo ">> Timed-load probe (UI_URL=$${UI_URL:-''} / file fallback)"
	@$(PYTHON) scripts/ui/perf_load.py --url "$${UI_URL:-}" --index webui/public/index.html --out var/ui/perf.json

.PHONY: ui.a11y.smoke
ui.a11y.smoke:
	@echo ">> A11y smoke (zero-Node) on webui/public/index.html"
	@$(PYTHON) scripts/ui/a11y_smoke.py --path webui/public/index.html --out var/ui/a11y.json

.PHONY: ui.metrics.log
ui.metrics.log:
	@echo ">> Append UI metrics entry (temporal artifacts, git sha)"
	@$(PYTHON) scripts/ui/metrics_log.py --log var/ui/metrics.jsonl

.PHONY: ui.accept
ui.accept: ui.perf.load ui.a11y.smoke ui.metrics.log
	@echo ">> P11 acceptance bundle complete. See var/ui/{perf.json,a11y.json,metrics.jsonl}"
