PY=./.venv/bin/python
PIP=./.venv/bin/pip
PYTEST=./.venv/bin/pytest
RUFF=./.venv/bin/ruff
MYPY=./.venv/bin/mypy

.PHONY: deps lint type test.unit test.int test.integration test.e2e coverage.report graph-e2e

deps: ; $(PIP) install -U pip && $(PIP) install -r requirements.txt

lint: ; $(RUFF) check src tests

type: ; $(MYPY) src

test.unit: ; $(PYTEST) -q tests/unit

test.int test.integration: ; $(PYTEST) -q tests/integration

test.e2e: ; $(PYTEST) -q tests/e2e || true

coverage.report: ; $(PYTEST) --cov=src --cov-report=term-missing --cov-fail-under=98