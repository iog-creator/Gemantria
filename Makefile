PY=./.venv/bin/python
PIP=./.venv/bin/pip
PYTEST=./.venv/bin/pytest
RUFF=./.venv/bin/ruff
MYPY=./.venv/bin/mypy

.PHONY: deps lint type test.unit test.int test.integration test.e2e test.live coverage.report graph-e2e report.run check.qwen

deps: ; $(PIP) install -U pip && $(PIP) install -r requirements.txt

lint: ; $(RUFF) check src tests

type: ; $(MYPY) src

test.unit: ; ALLOW_MOCKS_FOR_TESTS=1 USE_QWEN_EMBEDDINGS=true QWEN_EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b QWEN_RERANKER_MODEL=qwen.qwen3-reranker-0.6b $(PYTEST) -q tests/unit

test.int test.integration: ; ALLOW_MOCKS_FOR_TESTS=1 USE_QWEN_EMBEDDINGS=true QWEN_EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b QWEN_RERANKER_MODEL=qwen.qwen3-reranker-0.6b $(PYTEST) -q tests/integration

test.e2e: ; $(PYTEST) -q tests/e2e || true

test.live: ; ALLOW_MOCKS_FOR_TESTS=0 $(PYTEST) -q -m "requires_live_qwen"

check.qwen: ; $(PY) -c "from src.services.lmstudio_client import assert_qwen_live, QWEN_EMBEDDING_MODEL, QWEN_RERANKER_MODEL; health = assert_qwen_live([QWEN_EMBEDDING_MODEL, QWEN_RERANKER_MODEL]); print(f'Qwen Health: {health.ok} - {health.reason}'); exit(0 if health.ok else 1)"

coverage.report: ; $(PYTEST) --cov=src --cov-report=term-missing --cov-fail-under=98

report.run: ; $(PY) scripts/generate_report.py