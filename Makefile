PY=./.venv/bin/python
PIP=./.venv/bin/pip
PYTEST=./.venv/bin/pytest
RUFF=./.venv/bin/ruff
MYPY=./.venv/bin/mypy

.PHONY: deps lint type test.unit test.int test.integration test.e2e test.live coverage.report graph-e2e report.run check.qwen analyze.graph exports.graph exports.jsonld webui doctor preflight run.small verify.metrics generate.forest hooks verify.all

deps: ; $(PIP) install -U pip && $(PIP) install -r requirements.txt

lint: ; $(RUFF) check src tests

type: ; $(MYPY) src

test.unit: ; ALLOW_MOCKS_FOR_TESTS=1 USE_QWEN_EMBEDDINGS=true QWEN_EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b QWEN_RERANKER_MODEL=qwen.qwen3-reranker-0.6b $(PYTEST) -q tests/unit

test.int test.integration: ; ALLOW_MOCKS_FOR_TESTS=1 USE_QWEN_EMBEDDINGS=true QWEN_EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b QWEN_RERANKER_MODEL=qwen.qwen3-reranker-0.6b $(PYTEST) -q tests/integration

test.e2e: ; $(PYTEST) -q tests/e2e || true

test.live: ; ALLOW_MOCKS_FOR_TESTS=0 $(PYTEST) -q -m "requires_live_qwen"

check.qwen: ; $(PY) -c "from src.services.lmstudio_client import assert_qwen_live, QWEN_EMBEDDING_MODEL, QWEN_RERANKER_MODEL; health = assert_qwen_live([QWEN_EMBEDDING_MODEL, QWEN_RERANKER_MODEL]); print(f'Qwen Health: {health.ok} - {health.reason}'); exit(0 if health.ok else 1)"

coverage.report: ; $(PYTEST) --cov=src --cov-report=term-missing --cov-fail-under=98

report.run: ; bash -c "set -a && source .env && set +a && PYTHONPATH=/home/mccoy/Projects/Gemantria.v2 $(PY) scripts/generate_report.py"

analyze.graph: ; bash -c "set -a && source .env && set +a && PYTHONPATH=/home/mccoy/Projects/Gemantria.v2 $(PY) scripts/analyze_graph.py"

exports.graph: ; bash -c "set -a && source .env && set +a && PYTHONPATH=/home/mccoy/Projects/Gemantria.v2 $(PY) scripts/export_graph.py"

exports.jsonld: ; bash -c "set -a && source .env && set +a && PYTHONPATH=/home/mccoy/Projects/Gemantria.v2 $(PY) scripts/export_jsonld.py"

analyze.metrics: ; bash -c "set -a && source .env && set +a && PYTHONPATH=/home/mccoy/Projects/Gemantria.v2 $(PY) scripts/analyze_metrics.py"

.PHONY: verify.metrics
verify.metrics:
	python scripts/export_stats.py
	python scripts/verify_pr016_pr017.py --dsn "$${GEMATRIA_DSN}" --stats exports/graph_stats.json --graph exports/graph_latest.json

.PHONY: generate.forest
generate.forest: ; python3 scripts/generate_forest.py

webui: ; cd webui/graph && npm install && npm run dev

doctor: ; $(PY) scripts/doctor.py

preflight:
	$(PY) scripts/doctor.py | tee .last_doctor.json
	@grep -q '"verdict": "pass"' .last_doctor.json || (echo "Doctor not PASS — fix env/LM Studio/Postgres"; exit 1)

run.small: preflight
	bash -c "set -a && source .env && set +a && PYTHONPATH=/home/mccoy/Projects/Gemantria.v2 $(PY) -m src.graph.graph --book Genesis --batch-size 8" && \
	bash -c "set -a && source .env && set +a && PYTHONPATH=/home/mccoy/Projects/Gemantria.v2 $(PY) scripts/analyze_graph.py" && \
	bash -c "set -a && source .env && set +a && PYTHONPATH=/home/mccoy/Projects/Gemantria.v2 $(PY) scripts/generate_report.py"

.PHONY: hooks
hooks:
	pre-commit install

.PHONY: verify.all
verify.all: generate.forest
	pre-commit run --all-files
	@$(MAKE) -s verify.metrics || true
	@$(MAKE) -s verify.correlations || true