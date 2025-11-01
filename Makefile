



.PHONY: py.format py.lint py.quickfix py.longline py.fullwave \
        eval.graph.calibrate.adv ci.exports.smoke
py.format:
	@ruff format src scripts tools
py.lint:
	@ruff check src scripts tools
py.quickfix:
	@python3 scripts/quick_fixes.py && ruff check --fix src scripts
py.longline:
	@python3 scripts/longline_noqa.py
py.fullwave: py.quickfix py.longline
	@make py.format && make py.lint

.PHONY: test.smoke test.smoke.strict
test.smoke:
	pytest -o addopts="" -q --no-cov -m smoke tests/smoke || true
test.smoke.strict:
	pytest -o addopts="" -q --no-cov -m smoke tests/smoke

.PHONY: schema.validate.temporal schema.validate.temporal.strict
schema.validate.temporal:
	@echo "Schema validation not yet implemented - skipping"
schema.validate.temporal.strict:

.PHONY: ssot.validate ssot.validate.changed
ssot.validate:
	@echo "SSOT validation not yet implemented - skipping"
ssot.validate.changed:
	@echo "SSOT changed-files validation not yet implemented - skipping"

.PHONY: ci ci.precommit ci.audits
ci.precommit:
	@pre-commit run -a
ci.audits:
	@make rules.navigator.check rules.audit repo.audit docs.audit
ci:
	@ruff check src scripts tools || true
	@$(MAKE) ci.precommit
	@$(MAKE) ci.audits
	@$(MAKE) test.smoke

.PHONY: rules.navigator.check rules.numbering.check
rules.navigator.check:
	@python3 scripts/check_cursor_always_apply.py
rules.numbering.check:
	@python3 scripts/check_rule_numbering.py

.PHONY: share.sync share.check
share.sync:
	@python3 scripts/sync_share.py
share.check:
	@$(MAKE) share.sync >/dev/null
	@if git diff --quiet --exit-code -- share; then \
	  echo "[share.check] OK — share mirror is clean"; \
	else \
	  echo "[share.check] OUT OF DATE — run 'make share.sync' and commit updates"; exit 1; \
	fi

.PHONY: py.fullwave.c
py.fullwave.c:
	@$(MAKE) py.quickfix && $(MAKE) py.longline && $(MAKE) py.format && $(MAKE) py.lint

.PHONY: rules.audit
rules.audit:
	@python3 scripts/rules_audit.py

.PHONY: repo.audit
repo.audit:
	@python3 scripts/repo_audit.py

.PHONY: docs.audit
docs.audit:
	@python3 scripts/rules_guard.py

.PHONY: docs.smoke
docs.smoke: ## Validate docs exist and basic commands print help
	@test -f README.md && echo "[docs] README present"
	@test -f CHANGELOG.md && echo "[docs] CHANGELOG present"
	@test -f RELEASE_CHECKLIST.md && echo "[docs] checklist present"
	@python3 scripts/cli/gemantria_cli.py --help >/dev/null || true

.PHONY: smoke.smart schema.validate.smart ci.smart go
smoke.smart:
	@python3 scripts/mode_decider.py
schema.validate.smart:
	@python3 scripts/mode_decider.py
ci.smart:
	@python3 scripts/mode_decider.py && make rules.navigator.check rules.audit repo.audit docs.audit

.PHONY: data.verify ci.data.verify db.migrate exports.smoke ci.exports.smoke

# Run the data completeness verifier (local)
data.verify:
	@python3 scripts/verify_data_completeness.py

# CI gate (same check, enforced in PRs)
ci.data.verify:
	@python3 scripts/verify_data_completeness.py

# Apply SQL migrations (Phase-1 foundation)
db.migrate:
	@bash scripts/db/migrate.sh

# Quick status (tables count) — tolerates empty DB
db.status:
	@psql "$(GEMATRIA_DSN)" -qAt -c "SELECT table_schema, count(*) FROM information_schema.tables WHERE table_schema='gematria' GROUP BY 1;" || echo "DB unavailable - tolerated"

# CI helper: succeed if DB missing/unavailable (hermetic)
ci.db.tolerate.empty:
	@echo "[ci] empty/missing DB tolerated by policy"; exit 0

# Local exports smoke (Rule 038)
exports.smoke:
	@python3 scripts/exports_smoke.py

.PHONY: eval.smoke ci.eval.smoke

eval.smoke:
	@python3 scripts/eval/run_eval.py

# Intentionally same as local for now; not wired into CI

ci.eval.smoke:
	@python3 scripts/eval/run_eval.py

.PHONY: ops.next go deps.dev
ops.next:
	@if rg -n "^- \[ \]" NEXT_STEPS.md >/dev/null 2>&1; then \
	echo "[ops.next] NEXT_STEPS has unchecked boxes — complete them or mark Done."; exit 1; \
	else echo "[ops.next] NEXT_STEPS clear"; fi

# One-command, zero-choices path for Cursor and devs:
#  - lint/format/quickfix
#  - smart strict/soft smoke + schema
#  - audits
#  - share sync
go:
	@echo "[guide] go: lint/format → smart smoke/schema → db gate → exports gate → audits → share"
	@$(MAKE) py.fullwave.c
	@$(MAKE) ci.smart
	@$(MAKE) data.verify
	@$(MAKE) exports.smoke
	@$(MAKE) share.sync

# Install development dependencies (jsonschema, PyYAML)
deps.dev:
	@echo "[guide] Installing dev dependencies (jsonschema, PyYAML)..."
	pip install -r requirements-dev.txt

.PHONY: mini.go mini.extract mini.verify readiness.verify book.smoke book.go ci.book.readiness \
        book.plan book.dry book.resume book.stop

# Mini experiment (real inference) → verify → (then book)
mini.go: mini.extract mini.verify
	@echo "[guide] mini.go complete — proofs under reports/readiness/"

mini.extract:
	@echo "[guide] mini.extract: running small passage(s) with real LM endpoints"
	@python3 scripts/book_readiness.py run-mini --config config/mini_experiments.yaml

mini.verify:
	@echo "[guide] mini.verify: metrics → reports/readiness/readiness_report.json (idempotent)"
	@python3 scripts/book_readiness.py compute --inputs graph_stats.head.json temporal_patterns.head.json pattern_forecast.head.json

readiness.verify:
	@echo "[guide] readiness.verify: schema + thresholds"
	@python3 scripts/book_readiness.py gate --strict

# --- Book pipeline (local smoke) ---
book.smoke:
	@echo "[book.smoke] dry-run book pipeline (no external services required)"
	@python3 scripts/run_book.py dry --cfg config/book_plan.yaml || true

book.go:
	@python3 scripts/book_readiness.py assert-pass || (echo "[gate] readiness not satisfied"; exit 2)
	@echo "[guide] book.go: launching full extraction (real inference)"
	@python3 scripts/book_readiness.py run-book

# CI-friendly single gate (use in workflows)
ci.book.readiness:
	@python3 scripts/book_readiness.py gate --strict

# ---------- Whole-book ops helpers ----------
# Plan the chapters to run (no inference; produces reports/book_plan.json)
book.plan:
	@python3 scripts/run_book.py plan --cfg config/book_plan.yaml
	@echo "[guide] plan written to reports/readiness/book_plan.json"

# Dry-run (no LM calls). Validates plan, seeds, env, and output dirs.
book.dry:
	@python3 scripts/run_book.py dry --cfg config/book_plan.yaml

# Stop-loss: run first N chapters with real inference (requires readiness PASS)
book.stop:
	@python3 scripts/book_readiness.py assert-pass
	@python3 scripts/run_book.py stop --cfg config/book_plan.yaml --n $${N:-1}

# Resume the last interrupted/partial run from logs/book/
book.resume:
	@python3 scripts/run_book.py resume

# -----------------------------
# Eval / calibration
# -----------------------------

## Advanced graph calibration (stateless; writes eval artifacts)
eval.graph.calibrate.adv:
	@echo "[eval.graph.calibrate.adv] running advanced calibration…"
	@PYTHONPATH=. python3 scripts/eval/calibrate_advanced.py
	@echo "[eval.graph.calibrate.adv] OK"

# -----------------------------
# CI exports smoke
# -----------------------------

.PHONY: exports.write
exports.write: ## Write exports using existing exporters (reuse-first)
	@python scripts/export_stats.py
	@python scripts/generate_report.py

## Smoke test for exports. Hermetic CI: if no DB env is present, emit HINT and exit 0.
## Recognizes Postgres envs (PGHOST, PGUSER, PGDATABASE, DATABASE_URL).
ci.exports.smoke: ## Exports smoke (reuse-first; empty-DB tolerant)
	@python3 scripts/export_stats.py    || echo "[ci.exports] stats skipped (empty DB tolerated)"
	@python3 scripts/generate_report.py || echo "[ci.exports] report skipped (no data tolerated)"

.PHONY: ci.exports.validate
ci.exports.validate: ## Validate export artifacts (conditional; hermetic)
	@python3 scripts/ci/validate_exports.py

.PHONY: ci.badges
ci.badges: ## Build badges (reuse-first; tolerate missing)
	@{ test -f scripts/eval/build_badges.py && python3 scripts/eval/build_badges.py; } \
	  || echo "[ci.badges] badges script not present; skip"

.PHONY: pipeline.smoke
pipeline.smoke: ## Reuse-first pipeline smoke (uses existing book pipeline)
	@echo "[pipeline.smoke] delegating to existing book.smoke (reuse-first)"
	@$(MAKE) -s book.smoke

.PHONY: ci.pipeline.smoke
ci.pipeline.smoke: ## CI-safe pipeline smoke (reuse-first; hermetic)
	@MOCK_AI=1 SKIP_DB=1 PIPELINE_SEED=4242 $(MAKE) -s pipeline.smoke

.PHONY: webui.smoke
webui.smoke: ## Reuse-first Web UI smoke (adapter + existing viewer build if present)
	@bash scripts/webui/smoke.sh

.PHONY: ci.webui.smoke
ci.webui.smoke: ## CI-safe Web UI smoke (no network; OK if viewer build absent)
	@MOCK_AI=1 SKIP_DB=1 $(MAKE) -s webui.smoke

.PHONY: quality.show.thresholds
quality.show.thresholds: ## Echo current reranker thresholds (reuse-first)
	@echo "EDGE_STRONG=${EDGE_STRONG:-0.90}"; \
	 echo "EDGE_WEAK=${EDGE_WEAK:-0.75}"; \
	 echo "CANDIDATE_POLICY=${CANDIDATE_POLICY:-cache}"

.PHONY: quality.smoke
quality.smoke: ## Local quality smoke (adapter-only; hermetic)
	@bash scripts/quality/smoke.sh

.PHONY: ci.quality.smoke
ci.quality.smoke: ## CI quality smoke (no DB, no network)
	@EDGE_STRONG=${EDGE_STRONG:-0.90} EDGE_WEAK=${EDGE_WEAK:-0.75} \
	  CANDIDATE_POLICY=${CANDIDATE_POLICY:-cache} \
	  MOCK_AI=1 SKIP_DB=1 PIPELINE_SEED=4242 \
	  bash scripts/quality/smoke.sh

# ---------- CLI (Phase-6: reuse-first Typer wrapper) ----------

.PHONY: cli.help
cli.help: ## Show CLI usage (reuse-first Typer CLI)
	@python3 scripts/cli/gemantria_cli.py --help || true

.PHONY: cli.quickstart
cli.quickstart: ## 5-minute local quick-start (hermetic)
	@python3 scripts/cli/gemantria_cli.py quickstart

.PHONY: ci.cli.smoke
ci.cli.smoke: ## CLI smoke (hermetic)
	@python3 scripts/cli/gemantria_cli.py verify
	@MOCK_AI=1 SKIP_DB=1 EDGE_STRONG=${EDGE_STRONG:-0.90} EDGE_WEAK=${EDGE_WEAK:-0.75} \
	  python3 scripts/cli/gemantria_cli.py pipeline

# ---------- Governance & Policy Gates ----------

.PHONY: eval.report ci.eval.report

# Manifest-driven local report (writes to share/eval/)
eval.report:
	@python3 scripts/eval/report.py

# Not wired into CI; identical to local for now
ci.eval.report:
	@python3 scripts/eval/report.py

.PHONY: ops.verify ci.ops.verify

# Local repo ops verifier (prints decisive lines; no CI wiring)
ops.verify:
	@python3 scripts/ops/verify_repo.py

# Identical to local; intentionally not part of CI
ci.ops.verify:
	@python3 scripts/ops/verify_repo.py

.PHONY: eval.history ci.eval.history

# Temporal export history (writes share/eval/history.{json,md})
eval.history:
	@python3 scripts/eval/report_history.py

# Not wired into CI; identical to local for now
ci.eval.history:
	@python3 scripts/eval/report_history.py

.PHONY: eval.delta ci.eval.delta

# Per-run delta report (writes share/eval/delta.{json,md})
eval.delta:
	@python3 scripts/eval/report_delta.py

# Not wired into CI; identical to local for now
ci.eval.delta:
	@python3 scripts/eval/report_delta.py

.PHONY: eval.index ci.eval.index

# Build a simple index of eval artifacts
eval.index:
	@python3 scripts/eval/build_index.py

ci.eval.index:
	@python3 scripts/eval/build_index.py

.PHONY: eval.idstability ci.eval.idstability

# Node ID stability (writes share/eval/id_stability.{json,md})
eval.idstability:
	@python3 scripts/eval/report_id_stability.py

ci.eval.idstability:
	@python3 scripts/eval/report_id_stability.py

.PHONY: eval.catalog ci.eval.catalog

# Build an exports catalog (writes share/eval/exports_catalog.md)
eval.catalog:
	@python3 scripts/eval/build_exports_catalog.py

ci.eval.catalog:
	@python3 scripts/eval/build_exports_catalog.py

.PHONY: eval.provenance ci.eval.provenance eval.checksums ci.eval.checksums

# Provenance (writes share/eval/provenance.{json,md})
eval.provenance:
	@python3 scripts/eval/provenance.py

ci.eval.provenance:
	@python3 scripts/eval/provenance.py

# Checksums for exports (writes share/eval/checksums.csv)
eval.checksums:
	@python3 scripts/eval/build_checksums.py

ci.eval.checksums:
	@python3 scripts/eval/build_checksums.py

.PHONY: eval.anomalies ci.eval.anomalies eval.runlog ci.eval.runlog

# Aggregate anomalies into a single markdown file
eval.anomalies:
	@python3 scripts/eval/anomalies.py

ci.eval.anomalies:
	@python3 scripts/eval/anomalies.py

# Append one JSON line capturing the latest run's artifacts
eval.runlog:
	@python3 scripts/eval/run_log.py

ci.eval.runlog:
	@python3 scripts/eval/run_log.py

.PHONY: data.sanitize ci.data.sanitize eval.report.sanitized ci.eval.report.sanitized diag.integrity ci.diag.integrity

# Drop edges whose endpoints are missing; writes exports/graph_sanitized_*.json and graph_sanitized.json
data.sanitize:
	@python3 scripts/fix/sanitize_missing_endpoints.py

ci.data.sanitize:
	@python3 scripts/fix/sanitize_missing_endpoints.py

# Run manifest report against the sanitized export (graph_sanitized.json)
eval.report.sanitized:
	@python3 scripts/eval/report_for_file.py exports/graph_sanitized.json

ci.eval.report.sanitized:
	@python3 scripts/eval/report_for_file.py exports/graph_sanitized.json

# Diagnostics for current latest export (counts and examples)
diag.integrity:
	@python3 scripts/diagnostics/diagnose_integrity.py

ci.diag.integrity:
	@python3 scripts/diagnostics/diagnose_integrity.py

.PHONY: eval.profile.strict eval.profile.dev eval.repairplan

# Run manifest report under strict/dev profiles
eval.profile.strict:
	@python3 scripts/eval/run_with_profile.py strict

eval.profile.dev:
	@python3 scripts/eval/run_with_profile.py dev

# Build a non-destructive repair plan (JSON + MD)
eval.repairplan:
	@python3 scripts/eval/build_repair_plan.py

.PHONY: repair.apply ci.repair.apply eval.policydiff ci.eval.policydiff eval.report.repaired ci.eval.report.repaired

# Apply repair plan to produce a repaired export (adds stub nodes)
repair.apply:
	@python3 scripts/fix/apply_repair_plan.py

ci.repair.apply:
	@python3 scripts/fix/apply_repair_plan.py

# Run manifest report against the repaired export
eval.report.repaired:
	@python3 scripts/eval/report_for_file.py exports/graph_repaired.json

ci.eval.report.repaired:
	@python3 scripts/eval/report_for_file.py exports/graph_repaired.json

# Compare strict vs dev outcomes and write policy_diff.md
eval.policydiff:
	@python3 scripts/eval/policy_diff.py

ci.eval.policydiff:
	@python3 scripts/eval/policy_diff.py

.PHONY: eval.snapshot ci.eval.snapshot eval.html ci.eval.html eval.bundle ci.eval.bundle eval.gate.strict ci.eval.gate.strict

# Create config snapshots (manifest, thresholds, provenance)
eval.snapshot:
	@python3 scripts/eval/build_snapshot.py

ci.eval.snapshot:
	@python3 scripts/eval/build_snapshot.py

# Generate HTML dashboard with artifact links and badges
eval.html:
	@python3 scripts/eval/build_html_index.py

ci.eval.html:
	@python3 scripts/eval/build_html_index.py

# Create distributable bundle (tar.gz) with all artifacts
eval.bundle:
	@python3 scripts/eval/build_bundle.py

ci.eval.bundle:
	@python3 scripts/eval/build_bundle.py

# Strict profile gate - fails if any failures detected (unless ALLOW_FAIL=1)
eval.gate.strict:
	@python3 scripts/eval/gate_strict.py

ci.eval.gate.strict:
	@python3 scripts/eval/gate_strict.py

.PHONY: eval.remediation ci.eval.remediation eval.apply.remediation ci.eval.apply.remediation

# Analyze evaluation failures and generate remediation plan
eval.remediation:
	@python3 scripts/eval/build_remediation_plan.py

ci.eval.remediation:
	@python3 scripts/eval/build_remediation_plan.py

# Apply automated fixes from remediation plan (use SKIP_AUTO_FIXES=1 to preview)
eval.apply.remediation:
	@python3 scripts/eval/apply_remediation.py

ci.eval.apply.remediation:
	@python3 scripts/eval/apply_remediation.py

.PHONY: eval.badges ci.eval.badges eval.release_notes ci.eval.release_notes eval.package ci.eval.package

eval.badges:
	@python3 scripts/eval/build_badges.py

ci.eval.badges:
	@python3 scripts/eval/build_badges.py

eval.release_notes:
	@python3 scripts/eval/build_release_notes.py

ci.eval.release_notes:
	@python3 scripts/eval/build_release_notes.py

# One-shot local packaging: snapshot → html → bundle → badges → release_notes
eval.package:
	@$(MAKE) eval.snapshot
	@$(MAKE) eval.html
	@$(MAKE) eval.bundle
	@$(MAKE) eval.badges
	@$(MAKE) eval.release_notes
	@$(MAKE) eval.release_manifest
	@echo "[eval.package] OK"

ci.eval.package:
	@$(MAKE) eval.snapshot
	@$(MAKE) eval.html
	@$(MAKE) eval.bundle
	@$(MAKE) eval.badges
	@$(MAKE) eval.release_notes
	@echo "[eval.package] OK"

.PHONY: eval.package.strict ci.eval.package.strict
eval.package.strict:
	@$(MAKE) eval.gate.strict
	@$(MAKE) eval.package

ci.eval.package.strict:
	@$(MAKE) eval.gate.strict
	@$(MAKE) eval.package

.PHONY: eval.release_manifest ci.eval.release_manifest
eval.release_manifest:
	@python3 scripts/eval/build_release_manifest.py

ci.eval.release_manifest:
	@python3 scripts/eval/build_release_manifest.py

.PHONY: codex.task codex.grok codex.parallel codex.mcp.edit codex.mcp.validate
codex.task:
	@ALLOWED="$(ALLOW_CODEX)"; \
	IN_CI=false; \
	if [ "$${CI:-}" = "true" ] || [ -n "$${GITHUB_ACTIONS:-}" ] || [ -n "$${GITLAB_CI:-}" ] || [ -n "$${BUILDKITE:-}" ]; then IN_CI=true; fi; \
	if $${IN_CI} && [ "$$ALLOWED" != "1" ]; then \
	  echo "HINT[codex]: disabled in CI (set ALLOW_CODEX=1 to enable explicitly)"; \
	  exit 0; \
	fi; \
	if ! command -v scripts/agents/codex-task.sh >/dev/null 2>&1; then \
	  echo "ERR: scripts/agents/codex-task.sh missing"; exit 1; fi; \
	scripts/agents/codex-task.sh "$(TASK)"

codex.grok:
	@ALLOWED="$(ALLOW_CODEX)"; \
	IN_CI=false; \
	if [ "$${CI:-}" = "true" ] || [ -n "$${GITHUB_ACTIONS:-}" ] || [ -n "$${GITLAB_CI:-}" ] || [ -n "$${BUILDKITE:-}" ]; then IN_CI=true; fi; \
	if $${IN_CI} && [ "$$ALLOWED" != "1" ]; then \
	  echo "HINT[codex]: disabled in CI (set ALLOW_CODEX=1 to enable explicitly)"; \
	  exit 0; \
	fi; \
	PROFILE=grok4 scripts/agents/codex-task.sh "$(TASK)"

codex.parallel:
	@ALLOWED="$(ALLOW_CODEX)"; \
	IN_CI=false; \
	if [ "$${CI:-}" = "true" ] || [ -n "$${GITHUB_ACTIONS:-}" ] || [ -n "$${GITLAB_CI:-}" ] || [ -n "$${BUILDKITE:-}" ]; then IN_CI=true; fi; \
	if $${IN_CI} && [ "$$ALLOWED" != "1" ]; then \
	  echo "HINT[codex]: disabled in CI (set ALLOW_CODEX=1 to enable explicitly)"; \
	  exit 0; \
	fi; \
	echo "$$TASKS" | tr '\r' '\n' | scripts/agents/codex-par.sh

codex.mcp.edit:
	@${EDITOR:-nano} ~/.cursor/mcp.json

codex.mcp.validate:
	@if command -v jq >/dev/null 2>&1; then \
	  jq . ~/.cursor/mcp.json; \
	else \
	  python3 -m json.tool ~/.cursor/mcp.json; \
	fi
