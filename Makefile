



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
	@EVAL_OUTDIR=share/eval \
	 python3 scripts/eval/report.py

# CI version writes to _artifacts/eval/
ci.eval.report:
	@EVAL_OUTDIR=_artifacts/eval \
	 python3 scripts/eval/report.py

.PHONY: eval.history ci.eval.history

# Temporal export history (writes share/eval/history.{json,md})
eval.history:
	@EVAL_OUTDIR=share/eval \
	 python3 scripts/eval/report_history.py

# CI version writes to _artifacts/eval/
ci.eval.history:
	@EVAL_OUTDIR=_artifacts/eval \
	 python3 scripts/eval/report_history.py

.PHONY: eval.catalog ci.eval.catalog

# Build an exports catalog (writes share/eval/exports_catalog.md)
eval.catalog:
	@EXPORTS_CATALOG_OUT=share/eval/exports_catalog.md \
	 python3 scripts/eval/build_exports_catalog.py

ci.eval.catalog:
	@EXPORTS_CATALOG_OUT=_artifacts/eval/exports_catalog.md \
	 python3 scripts/eval/build_exports_catalog.py

.PHONY: eval.snapshot ci.eval.snapshot

# Build an eval snapshot (writes share/eval/snapshot/)
eval.snapshot:
	@SNAPSHOT_DIR=share/eval/snapshot \
	 python3 scripts/eval/build_snapshot.py

ci.eval.snapshot:
	@SNAPSHOT_DIR=_artifacts/eval/snapshot \
	 python3 scripts/eval/build_snapshot.py

.PHONY: eval.html ci.eval.html

# Build HTML index from eval results (writes share/eval/index.html)
eval.html:
	@EVAL_HTML_OUTDIR=share/eval \
	 python3 scripts/eval/build_html_index.py

ci.eval.html:
	@EVAL_HTML_OUTDIR=_artifacts/eval \
	 python3 scripts/eval/build_html_index.py

.PHONY: eval.delta ci.eval.delta

# Build eval delta report (writes share/eval/delta.{json,md})
eval.delta:
	@EVAL_OUTDIR=share/eval \
	 python3 scripts/eval/report_delta.py

ci.eval.delta:
	@EVAL_OUTDIR=_artifacts/eval \
	 python3 scripts/eval/report_delta.py

.PHONY: eval.bundle ci.eval.bundle

# Build eval bundle tarball (writes share/eval/bundles/)
eval.bundle:
	@EVAL_BUNDLES_DIR=share/eval/bundles EVAL_DIR=share/eval \
	 python3 scripts/eval/build_bundle.py

ci.eval.bundle:
	@EVAL_BUNDLES_DIR=_artifacts/eval/bundles EVAL_DIR=_artifacts/eval \
	 python3 scripts/eval/build_bundle.py

.PHONY: eval.badges ci.eval.badges eval.release_notes ci.eval.release_notes eval.package ci.eval.package

eval.badges:
	@EVAL_OUTDIR=share/eval BADGES_OUTDIR=share/eval/badges \
	 python3 scripts/eval/build_badges.py

ci.eval.badges:
	@EVAL_OUTDIR=_artifacts/eval BADGES_OUTDIR=_artifacts/eval/badges \
	 python3 scripts/eval/build_badges.py

eval.release_notes:
	@EVAL_OUTDIR=share/eval \
	 python3 scripts/eval/build_release_notes.py

ci.eval.release_notes:
	@EVAL_OUTDIR=_artifacts/eval \
	 python3 scripts/eval/build_release_notes.py

# One-shot local packaging: snapshot → html → bundle → badges → release_notes
eval.package:
	@$(MAKE) eval.snapshot
	@$(MAKE) eval.html
	@$(MAKE) eval.bundle
	@$(MAKE) eval.badges
	@$(MAKE) eval.release_notes
	@echo "[eval.package] OK"

ci.eval.package:
	@$(MAKE) ci.eval.snapshot
	@$(MAKE) ci.eval.html
	@$(MAKE) ci.eval.bundle
	@$(MAKE) ci.eval.badges
	@$(MAKE) ci.eval.release_notes
	@echo "[ci.eval.package] OK"

.PHONY: repair.apply ci.repair.apply eval.policydiff ci.eval.policydiff eval.report.repaired ci.eval.report.repaired ci.eval.repairplan

repair.apply:
	@REPAIR_PLAN=share/eval/repair_plan.json \
	 REPAIRED_DIR=exports \
	 REPAIRED_BASENAME=graph_repaired.json \
	 python3 scripts/fix/apply_repair_plan.py

ci.repair.apply:
	@REPAIR_PLAN=_artifacts/eval/repair_plan.json \
	 REPAIRED_DIR=_artifacts/exports \
	 REPAIRED_BASENAME=graph_repaired.json \
	 python3 scripts/fix/apply_repair_plan.py

eval.report.repaired:
	@EVAL_OUTDIR=share/eval \
	 python3 scripts/eval/report_for_file.py exports/graph_repaired.json

ci.eval.report.repaired:
	@EVAL_OUTDIR=_artifacts/eval \
	 python3 scripts/eval/report_for_file.py _artifacts/exports/graph_repaired.json

eval.policydiff:
	@EVAL_OUTDIR=share/eval \
	 python3 scripts/eval/policy_diff.py

ci.eval.policydiff:
	@EVAL_OUTDIR=_artifacts/eval \
	 python3 scripts/eval/policy_diff.py

# Build repair plan for local development
eval.repairplan:
	@EVAL_OUTDIR=share/eval \
	 python3 scripts/eval/build_repair_plan.py

# Build repair plan for CI into _artifacts
ci.eval.repairplan:
	@EVAL_OUTDIR=_artifacts/eval \
	 python3 scripts/eval/build_repair_plan.py

# Profile targets for policy diff
eval.profile.strict:
	@EVAL_OUTDIR=share/eval \
	 python3 scripts/eval/report.py

eval.profile.dev:
	@EVAL_OUTDIR=share/eval \
	 python3 scripts/eval/report.py

.PHONY: eval.index ci.eval.index

# Build eval index (writes share/eval/index.md)
eval.index:
	@EVAL_DIR=share/eval \
	 python3 scripts/eval/build_index.py

ci.eval.index:
	@EVAL_DIR=_artifacts/eval \
	 python3 scripts/eval/build_index.py

# ---------- SSOT Validation (Hermetic, no pip) ----------

.PHONY: ssot.validate ssot.validate.changed

# SSOT schema files
SSOT_SCHEMAS := \
	docs/SSOT/graph-patterns.schema.json \
	docs/SSOT/graph-stats.schema.json \
	docs/SSOT/graph-correlations.schema.json \
	docs/SSOT/temporal-patterns.schema.json \
	docs/SSOT/pattern-forecast.schema.json

# Validate all SSOT JSON files against their schemas (hermetic, no pip)
ssot.validate:
	@echo "[ssot.validate] Validating all SSOT JSON against schemas..."
	@set -e; \
	for S in $(SSOT_SCHEMAS); do \
	  case "$$S" in \
	    *graph-patterns* ) INST="docs/SSOT/graph/*.json";; \
	    *graph-stats* )    INST="share/graph/*stats*.json share/graph/graph_stats.head.json";; \
	    *graph-correlations* ) INST="docs/SSOT/graph-correlations/*.json";; \
	    *temporal-patterns* ) INST="docs/SSOT/temporal/*.json";; \
	    *pattern-forecast* )  INST="docs/SSOT/forecast/*.json";; \
	    * ) INST="";; \
	  esac; \
	  if [ -n "$$INST" ]; then \
	    echo " - $$S"; \
	    python3 scripts/eval/jsonschema_validate.py --schema "$$S" --instance $$INST || exit 2; \
	  fi; \
	done

# Validate only changed SSOT JSON files (for PR-diff validation)
ssot.validate.changed:
	@echo "[ssot.validate.changed] Validating only changed SSOT JSON..."
	@base="${BASE_SHA:-$(git merge-base origin/main HEAD)}"; head="${HEAD_SHA:-HEAD}"; \
	files="$(git diff --name-only $$base $$head | grep -E '^(docs/SSOT|share/graph)/.*\\.json$$' || true)"; \
	if [ -z "$$files" ]; then echo " - no SSOT JSON changed"; exit 0; fi; \
	status=0; \
	for f in $$files; do \
	  case "$$f" in \
	    docs/SSOT/graph/* )     S="docs/SSOT/graph-patterns.schema.json";; \
	    share/graph/*stats*.json|share/graph/graph_stats.head.json ) S="docs/SSOT/graph-stats.schema.json";; \
	    docs/SSOT/graph-correlations/* )  S="docs/SSOT/graph-correlations.schema.json";; \
	    docs/SSOT/temporal/* )  S="docs/SSOT/temporal-patterns.schema.json";; \
	    docs/SSOT/forecast/* )  S="docs/SSOT/pattern-forecast.schema.json";; \
	    * ) S="";; \
	  esac; \
	  if [ -n "$$S" ]; then \
	    echo " - $$f vs $$S"; \
	    python3 scripts/eval/jsonschema_validate.py --schema "$$S" --instance "$$f" || status=2; \
	  fi; \
	done; \
	exit $$status

# ---------- Governance & Policy Gates ----------

.PHONY: rules.numbering.check share.check

# Check rule numbering integrity (no duplicates, required rules present)
rules.numbering.check:
	@python3 scripts/check_rule_numbering.py

# Verify share mirror is clean (no drift from source files)
share.check:
	@$(MAKE) share.sync >/dev/null
	@if git diff --quiet --exit-code -- share; then \
	  echo "[share.check] OK — share mirror is clean"; \
	else \
	  echo "[share.check] OUT OF DATE — run 'make share.sync' and commit updates"; exit 1; \
	fi
