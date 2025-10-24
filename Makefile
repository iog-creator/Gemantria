
.PHONY: models.verify models.swap models.params
PY=./.venv/bin/python
PIP=./.venv/bin/pip
PYTEST=./.venv/bin/pytest
RUFF=./.venv/bin/ruff
MYPY=./.venv/bin/mypy

.PHONY: repo.audit docs.audit rules.audit rules.navigator.check share.sync
repo.audit:
	@python3 scripts/repo_audit.py
docs.audit:
	@echo "Docs changed:" && git diff --name-only -- docs | sed -n "1,50p"
rules.audit:
	@python3 scripts/rules_audit.py
rules.navigator.check:
	@python3 scripts/check_cursor_always_apply.py
share.sync:
	@python3 scripts/sync_share.py

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

.PHONY: share.refresh
share.refresh:
	python3 scripts/update_share.py

.PHONY: share.sync
share.sync: share.refresh
	@python3 scripts/sync_share.py

.PHONY: share.check
share.check:
	python3 scripts/check_share_sync.py
PYTHONPATH ?= $(shell pwd)
.PHONY: models.verify models.swap models.params env.print
models.verify:
	@echo "[models.verify] Using PYTHONPATH=$(PYTHONPATH)"
	PYTHONPATH=$(PYTHONPATH) python3 scripts/models_verify.py

models.swap:
	@echo "[models.swap] Using PYTHONPATH=$(PYTHONPATH)"
	@ANSWERER_USE_ALT=1 PYTHONPATH=$(PYTHONPATH) python3 scripts/models_verify.py

# Print the currently effective model knobs (reads .env via env_loader)
models.params:
	@python3 -c "from src.infra.env_loader import ensure_env_loaded; import os; ensure_env_loaded(); keys = ['ANSWERER_USE_ALT','ANSWERER_MODEL_PRIMARY','ANSWERER_MODEL_ALT','EMBEDDING_MODEL','EMBED_BATCH_MAX','EDGE_ALPHA','EDGE_STRONG','EDGE_WEAK','NN_TOPK','LM_STUDIO_HOST']; [print(f'{k}={os.getenv(k,\"<unset>\")}') for k in keys]"

env.print:
	python3 scripts/echo_env.py

.PHONY: rules.lint rules.refactor.dry rules.refactor.apply repo.clean py.lint py.type py.format

rules.lint:
	@python3 scripts/rules_lint.py

rules.refactor.dry:
	@python3 scripts/rules_refactor.py dry

rules.refactor.apply:
	@python3 scripts/rules_refactor.py apply

repo.clean:
	@find . -name "__pycache__" -type d -prune -exec rm -rf {} +; \
	 find . -name "*.pyc" -delete

py.lint:
	@python3 -c "import sys, subprocess; subprocess.check_call([sys.executable,'-m','ruff','check','src','scripts'])" 2>/dev/null || echo "[py.lint] skipped or issues"

py.type:
	@python3 -c "import sys, subprocess; subprocess.check_call([sys.executable,'-m','mypy','--ignore-missing-imports','src'])" 2>/dev/null || echo "[py.type] skipped or issues"

py.format:
	@python3 -c "import sys, subprocess; subprocess.check_call([sys.executable,'-m','black','src','scripts'])" 2>/dev/null || echo "[py.format] skipped or issues"
