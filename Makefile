



.PHONY: py.quickfix py.longline py.fullwave
py.quickfix:
	@python3 scripts/quick_fixes.py && ruff check --fix src scripts
py.longline:
	@python3 scripts/longline_noqa.py
py.fullwave: py.quickfix py.longline
	@make py.format && make py.lint

.PHONY: test.smoke test.smoke.strict
test.smoke:
	pytest -q --no-cov -m smoke tests/smoke || true
test.smoke.strict:
	pytest -q --no-cov -m smoke tests/smoke

.PHONY: schema.validate.temporal schema.validate.temporal.strict
schema.validate.temporal:
	@echo "Schema validation not yet implemented - skipping"
schema.validate.temporal.strict:
	@echo "Schema validation not yet implemented - skipping"

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

# Apply SQL migrations (adjust DSN if needed)
db.migrate:
	@echo "[db] applying migrations…"
	@psql "$${GEMATRIA_DSN:-$${DB_DSN:-postgresql://localhost/gemantria}}" -v ON_ERROR_STOP=1 -f migrations/037_create_concepts.sql
	@echo "[db] migrations OK"

# Local exports smoke (Rule 038)
exports.smoke:
	@python3 scripts/exports_smoke.py

# CI gate (Rule 038)
ci.exports.smoke:
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

.PHONY: mini.go mini.extract mini.verify readiness.verify book.go ci.book.readiness \
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
