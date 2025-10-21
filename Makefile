PY=./.venv/bin/python
PIP=./.venv/bin/pip
PYTEST=./.venv/bin/pytest
RUFF=./.venv/bin/ruff
MYPY=./.venv/bin/mypy
.PHONY: deps lint type test.unit test.contract test.int test.e2e coverage.report graph-e2e
deps: ; $(PIP) install -U pip && $(PIP) install -r requirements.txt || true
lint: ; $(RUFF) src tests
type: ; $(MYPY) src
test.unit: ; $(PYTEST) tests/unit
test.contract: ; $(PYTEST) tests/contract
test.int: ; $(PYTEST) tests/integration
test.e2e: ; $(PYTEST) tests/e2e
coverage.report: ; $(PYTEST) --cov=src
graph-e2e: ; $(PY) -m src.graph.graph Genesis --mode START --dry-run
