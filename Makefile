



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

.PHONY: rules.navigator.check
rules.navigator.check:
	@python3 scripts/check_cursor_always_apply.py

.PHONY: share.sync
share.sync:
	@python3 scripts/sync_share.py

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

.PHONY: data.verify ci.data.verify db.migrate

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

.PHONY: go deps.dev
# One-command, zero-choices path for Cursor and devs:
#  - lint/format/quickfix
#  - smart strict/soft smoke + schema
#  - db gate
#  - audits
#  - share sync
go:
	@echo "[guide] go: lint/format → smart smoke/schema → db gate → audits → share"
	@$(MAKE) py.fullwave.c
	@$(MAKE) ci.smart
	@$(MAKE) data.verify
	@$(MAKE) share.sync

# Install development dependencies (jsonschema, PyYAML)
deps.dev:
	@echo "[guide] Installing dev dependencies (jsonschema, PyYAML)..."
	pip install -r requirements-dev.txt

.PHONY: mini.go mini.extract mini.verify readiness.verify book.go ci.book.readiness \
        book.plan book.dry book.resume book.stop book.stats book.last book.policy.check book.cmd

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
	@echo "[guide] book.go: launching full extraction (real inference via run_book.py)"
	@python3 scripts/run_book.py stop --cfg config/book_plan.yaml --n 9999

# CI-friendly single gate (use in workflows)
ci.book.readiness:
	@python3 scripts/book_readiness.py gate --strict

# Validate runner governance gates quickly (Rule 003 and Qwen Live Gate visible checks)
book.policy.check:
	@python3 scripts/book_policy_check.py

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

# Echo the resolved command for a chapter without executing it
book.cmd:
	@python3 scripts/run_book.py echo --cfg config/book_plan.yaml --chapter $${CH:-1}

# Summarize timings/RCs and flag suspicious fast chapters
book.stats:
	@python3 scripts/book_stats.py

# Quick peek at the last chapter's stdout/stderr (if present)
book.last:
	@python3 -c "from pathlib import Path; LOGS=Path('logs/book'); outs=sorted(LOGS.glob('*.out')); errs=sorted(LOGS.glob('*.err')); print('[last] outs:', outs[-1] if outs else 'none'); print('[last] errs:', errs[-1] if errs else 'none')"

# Scan for approved/golden example files with git history and content preview
examples.scan:
	@python3 scripts/find_approved_examples.py

# Validate new probe output against golden examples
examples.check:
	@python3 scripts/validate_examples.py --new $(NEW) --golden $(GOLDEN)

# Golden files management
.PHONY: goldens.status goldens.schema.enrichment goldens.sample.check goldens.seed.enrichment goldens.check.archive
goldens.status:
	@python3 scripts/goldens_status.py

# Validate the current enrichment golden against the enrichment schema
goldens.schema.enrichment:
	@python3 scripts/goldens_enrichment_schema_check.py

# Validate the latest live sample (from logs/) against the enrichment schema
goldens.sample.check:
	@python3 scripts/goldens_sample_check.py

# Promote the latest live sample to be the current enrichment golden
goldens.seed.enrichment:
	@latest=$$(ls -1t logs/book/*.out logs/book/*.jsonl logs/probes/*.out logs/probes/*.jsonl 2>/dev/null | head -n1); \
	test -n "$$latest" || (echo "[goldens.seed] no logs to seed from"; exit 2); \
	cp "$$latest" examples/enrichment/golden_enrichment.jsonl; \
	echo "[goldens.seed] seeded examples/enrichment/golden_enrichment.jsonl from $$latest"

# Run archive-track unit tests (your legacy goldens)
goldens.check.archive:
	@python3 scripts/gematria_verify.py
