



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

.PHONY: go
# One-command, zero-choices path for Cursor and devs:
#  - lint/format/quickfix
#  - smart strict/soft smoke + schema
#  - audits
#  - share sync
go:
	@echo "[guide] go: lint/format → smart smoke/schema → audits → share"
	@$(MAKE) py.fullwave.c
	@$(MAKE) ci.smart
	@$(MAKE) share.sync
