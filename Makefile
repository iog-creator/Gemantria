



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
	@echo "[ops.verify] running"
	@if [ -f share/eval/release_manifest.json ]; then \
	  echo "[ops.verify] integrity check present → verifying"; \
	  $(MAKE) -s eval.verify.integrity.soft; \
	else \
	  echo "[ops.verify] no release_manifest.json → skipping integrity check"; \
	fi
	@missing=0; \
	for f in share/eval/graph_latest.json share/eval/centrality.json share/eval/release_manifest.json share/eval/provenance.json share/eval/quality_report.txt share/eval/summary.md share/eval/summary.json share/eval/badges/quality.svg; do \
	  if [ ! -f $$f ]; then echo "[ops.verify] MISSING $$f"; missing=1; fi; \
	done; \
	if [ $$missing -ne 0 ]; then echo "[ops.verify] FAIL required artifacts missing"; exit 2; fi
	@python3 scripts/ops/verify_repo.py
	@echo "[ops.verify] OK"

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


# Provenance (writes share/eval/provenance.{json,md})


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
	@$(MAKE) eval.graph.rerank.refresh
	@$(MAKE) eval.graph.rerank_blend
	@$(MAKE) eval.graph.centrality
	@$(MAKE) eval.snapshot.rotate
	@$(MAKE) eval.graph.tables
	@$(MAKE) eval.graph.delta
	@$(MAKE) eval.bundle
	@$(MAKE) eval.badges
	@$(MAKE) eval.release_notes
	@$(MAKE) eval.bundle.all
	@$(MAKE) eval.provenance
	@$(MAKE) eval.release_manifest
	@$(MAKE) eval.schema.verify
	@$(MAKE) -s eval.verify.integrity.soft
	@$(MAKE) eval.summary
	@$(MAKE) eval.quality.check
	@$(MAKE) eval.quality.badge
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

.PHONY: eval.bundle.all

# Create a single tar.gz of share/eval for handoff (idempotent path)
eval.bundle.all:
	@mkdir -p share/eval/bundles
	@ts=$$(date -u +%Y%m%dT%H%M%SZ); \
	out="share/eval/bundles/eval_$${ts}.tar.gz"; \
	(cd share && tar -czf "../$${out}" --mtime='UTC 2020-01-01' --owner=0 --group=0 --numeric-owner eval); \
	echo "[eval.bundle.all] wrote $${out}"

.PHONY: eval.verify.integrity ci.eval.verify.integrity
eval.verify.integrity:
	@python3 scripts/eval/verify_integrity.py

ci.eval.verify.integrity:
	@python3 scripts/eval/verify_integrity.py

.PHONY: eval.verify.integrity.soft
# Fast, non-blocking soft integrity: cached by release_manifest fingerprint
RELEASE_MANIFEST ?= share/eval/release_manifest.json
eval.verify.integrity.soft:
	@python3 scripts/eval/integrity_fast.py --manifest "$(RELEASE_MANIFEST)" \
	  --hard-cmd "make -s eval.verify.integrity" ; true

.PHONY: eval.graph.centrality eval.graph.rerank_blend eval.graph.rerank.refresh eval.graph.tables eval.graph.delta eval.schema.verify
eval.graph.centrality:
	@.venv/bin/python3 scripts/eval/compute_centrality.py
eval.graph.rerank_blend:
	@.venv/bin/python3 scripts/eval/apply_rerank_blend.py
eval.graph.rerank.refresh:
	@python3 scripts/eval/apply_rerank_refresh.py
eval.graph.tables:
	@python3 scripts/eval/export_graph_tables.py
eval.graph.delta:
	@python3 scripts/eval/compute_delta.py
eval.schema.verify:
	@python3 -c "import jsonschema" >/dev/null 2>&1 || (echo '[schema] installing jsonschema' && pip3 install --quiet jsonschema)
	@python3 scripts/eval/verify_schema.py
eval.snapshot.rotate:
	@python3 scripts/eval/rotate_snapshot.py
eval.quality.check:
	@python3 scripts/eval/check_quality.py
eval.summary:
	@python3 scripts/eval/build_run_summary.py
.PHONY: eval.quality.badge eval.graph.calibrate
eval.quality.badge:
	@python3 scripts/eval/make_quality_badge.py
eval.graph.calibrate:
	@python3 scripts/eval/calibrate_thresholds.py

.PHONY: eval.open
eval.open:
	@echo "[eval.open] Opening dashboard..."
	@python3 -c "import pathlib, webbrowser; p = pathlib.Path('share/eval/index.html').resolve(); print('[eval.open]', p); webbrowser.open(p.as_uri())"

.PHONY: eval.provenance ci.eval.provenance
eval.provenance:
	@python3 scripts/eval/build_provenance.py

ci.eval.provenance:
	@python3 scripts/eval/build_provenance.py
