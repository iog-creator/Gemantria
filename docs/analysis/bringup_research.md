# Bring-up System Research Dossier

## LM Studio References

./env_example.txt:183:# Example: LM_STUDIO_MODEL_ID="lmstudio-community/Meta-Llama-3-8B-Instruct"
./tests/integration/test_relations_and_patterns.py:86:            patch("src.services.lmstudio_client.rerank_pairs") as mock_rerank,
./tests/unit/test_network_aggregator.py:20:from services.lmstudio_client import LMStudioClient
./tests/unit/test_network_aggregator.py:126:    @patch("services.lmstudio_client.requests.Session.post")
./tests/unit/test_network_aggregator.py:147:    @patch("services.lmstudio_client.requests.Session.post")
./tests/unit/test_lmstudio_client.py:3:from src.services.lmstudio_client import (
./agentpm/tests/pipelines/test_enrich_nouns_lm_routing.py:42:@patch("src.services.lmstudio_client.chat_completion")
./agentpm/tests/pipelines/test_enrich_nouns_lm_routing.py:65:@patch("src.services.lmstudio_client.chat_completion")
./agentpm/scripts/reality_check_1_live.py:13:   resolver (lmstudio_resolver.base_url) to determine the LM endpoint.
./agentpm/scripts/reality_check_1_live.py:58:import scripts.ai.lmstudio_resolver as lmstudio_resolver

## LM Studio Server Commands

./env_example.txt:186:# Port for the LM Studio HTTP server (used by lms server start).
./agentpm/scripts/reality_check_1.py:162:    Start LM Studio server using `lms server start`.
./agentpm/scripts/reality_check_1.py:183:            return False, f"lms server start succeeded but server not accessible: {reason}"
./agentpm/scripts/reality_check_1.py:189:        return False, f"lms server start failed: {stderr or stdout}"
./share/scripts_AGENTS.md:31:- Requires servers running (headless): `lms server start --port 9994 [--port 9991/9993]`
./share/LM_STUDIO_SETUP.md:63:lms server start --port 1234 --gpu=1.0
./share/LM_STUDIO_SETUP.md:69:lms server start --port 1234 --gpu=1.0
./share/LM_STUDIO_SETUP.md:297:lms server start --port 1234 --gpu=1.0
./scripts/AGENTS.md:31:- Requires servers running (headless): `lms server start --port 9994 [--port 9991/9993]`
./scripts/setup_lm_studio_and_db.sh:159:echo "3. Start LM Studio server: lms server start --port 1234"
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:104:lms server start --port 1234
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:107:lms server start --port 1234 --gpu=1.0
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:231:3. Start LM Studio server: `lms server start --port 1234`
./docs/runbooks/LM_STUDIO_SETUP.md:63:lms server start --port 1234 --gpu=1.0
./docs/runbooks/LM_STUDIO_SETUP.md:69:lms server start --port 1234 --gpu=1.0
./docs/runbooks/LM_STUDIO_SETUP.md:297:lms server start --port 1234 --gpu=1.0
./docs/runbooks/LM_HEALTH.md:69:   lms server start --port 1234 --gpu=1.0
./docs/qwen_integration.md:229:lms server start --port 9994
./docs/qwen_integration.md:300:   lms server start --port 9994

## LM Studio Load Commands

./env_example.txt:182:# LM Studio CLI model identifier to auto-load via `lms load`.
./agentpm/scripts/reality_check_1.py:194:    Load LM Studio model using `lms load` if LM_STUDIO_MODEL_ID is set.
./agentpm/scripts/reality_check_1.py:213:        return False, f"lms load failed: {stderr or stdout}"
./README_FULL.md:118:  - `LM_STUDIO_MODEL_ID`: Model identifier for `lms load` (e.g., `lmstudio-community/Meta-Llama-3-8B-Instruct`)
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:126:lms load christian-bible-expert-v2.0-12b

## Database Startup Patterns

./env_example.txt:178:# Example (macOS/Homebrew):  DB_START_CMD="brew services start postgresql"
./env_example.txt:179:# Example (systemd):         DB_START_CMD="sudo systemctl start postgresql"
./share/DB_HEALTH.md:70:   - Verify database server is running: `pg_isready` or `systemctl status postgresql`
./scripts/setup_lm_studio_and_db.sh:94:            echo "   Example: DB_START_CMD=\"sudo systemctl start postgresql\""
./scripts/setup_lm_studio_and_db.sh:122:    if command -v systemctl >/dev/null 2>&1 && systemctl list-units --type=service | grep -q postgresql; then
./scripts/setup_lm_studio_and_db.sh:123:        RECOMMENDATIONS+=("Set DB_START_CMD=\"sudo systemctl start postgresql\" in .env")
./scripts/setup_lm_studio_and_db.sh:140:    echo "  DB_START_CMD=\"sudo systemctl start postgresql\"  # or your system's command"
./scripts/bootstrap_dev.sh:18:sudo systemctl start postgresql 2>/dev/null || echo "PostgreSQL may already be running"
./README_FULL.md:117:  - `DB_START_CMD`: Shell command to start Postgres (e.g., `brew services start postgresql` or `sudo systemctl start postgresql`)
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:23:sudo systemctl start postgresql
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:24:sudo systemctl enable postgresql  # Auto-start on boot
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:29:brew services start postgresql
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:47:DB_START_CMD="sudo systemctl start postgresql"
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:50:DB_START_CMD="brew services start postgresql"
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:155:DB_START_CMD="sudo systemctl start postgresql"
./docs/runbooks/DB_HEALTH.md:70:   - Verify database server is running: `pg_isready` or `systemctl status postgresql`

## Port Configurations

./env_example.txt:45:LM_STUDIO_HOST=  # e.g. http://127.0.0.1:9994 (set in your .env)
./env_example.txt:48:# OpenAI-compatible API base URL (defaults to LM Studio on port 9994 per AGENTS.md)
./env_example.txt:49:OPENAI_BASE_URL=http://127.0.0.1:9994/v1
./env_example.txt:54:# Optional: override LM Studio embed host/port if not defaulting to 9994.
./env_example.txt:56:# LM_EMBED_PORT=9994
./env_example.txt:187:# Defaults to 1234 if left blank.
./tests/smoke/test_models.py:73:    port = int(os.getenv("LM_EMBED_PORT", "9994"))
./agentpm/tests/runtime/test_lm_routing.py:40:            "base_url": "http://localhost:1234/v1",
./agentpm/tests/runtime/test_lm_routing.py:56:            "base_url": "http://localhost:1234/v1",
./agentpm/tests/runtime/test_lm_routing.py:72:            "base_url": "http://localhost:1234/v1",
./agentpm/tests/lm/test_phase3b_lm_health_guard.py:25:            "base_url": "http://127.0.0.1:1234/v1",
./agentpm/tests/lm/test_phase3b_lm_health_guard.py:51:            "base_url": "http://127.0.0.1:1234/v1",
./agentpm/tests/lm/test_phase3b_lm_health_guard.py:77:            "base_url": "http://127.0.0.1:1234/v1",
./agentpm/tests/lm/test_phase3b_lm_health_guard.py:101:            "base_url": "http://127.0.0.1:1234/v1",
./agentpm/tests/lm/test_phase3b_lm_health_guard.py:121:            "base_url": "http://127.0.0.1:1234/v1",

## Model Environment Variables

./env_example.txt:59:THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
./env_example.txt:60:MATH_MODEL=self-certainty-qwen3-1.7b-base-math
./env_example.txt:61:EMBEDDING_MODEL=text-embedding-bge-m3
./env_example.txt:62:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./tests/integration/test_ai_enrichment_node.py:20:    monkeypatch.setenv("THEOLOGY_MODEL", "nonexistent-model")
./tests/integration/test_ai_enrichment_node.py:73:    assert os.getenv("THEOLOGY_MODEL")
./tests/smoke/test_models.py:77:    model = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
./agentpm/scripts/reality_check_1_live.py:197:    theology = os.getenv("THEOLOGY_MODEL")
./agentpm/scripts/reality_check_1_live.py:199:    math_model = os.getenv("MATH_MODEL")
./agentpm/scripts/reality_check_1_live.py:201:    embedding = os.getenv("EMBEDDING_MODEL") or os.getenv("LM_EMBED_MODEL")
./agentpm/scripts/reality_check_1_live.py:203:    reranker = os.getenv("RERANKER_MODEL")
./agentpm/scripts/reality_check_1_live.py:206:        ("THEOLOGY_MODEL", theology),
./agentpm/scripts/reality_check_1_live.py:207:        ("MATH_MODEL", math_model),
./agentpm/scripts/reality_check_1_live.py:208:        ("EMBEDDING_MODEL", embedding),
./agentpm/scripts/reality_check_1_live.py:209:        ("RERANKER_MODEL", reranker),
./archive/.env.backup:22:THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
./archive/.env.backup:23:MATH_MODEL=self-certainty-qwen3-1.7b-base-math
./archive/.env.backup:24:QWEN_EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b
./archive/.env.backup:25:QWEN_RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./src/infra/runs_ledger.py:54:        "embedding_model": os.getenv("EMBEDDING_MODEL", "unknown"),
./src/infra/runs_ledger.py:55:        "reranker_model": os.getenv("RERANKER_MODEL", "unknown"),
./src/infra/runs_ledger.py:56:        "theology_model": os.getenv("THEOLOGY_MODEL", "unknown"),
./src/infra/runs_ledger.py:57:        "math_model": os.getenv("MATH_MODEL", "unknown"),
./src/graph/AGENTS.md:89:required_models = [QWEN_EMBEDDING_MODEL, QWEN_RERANKER_MODEL, THEOLOGY_MODEL]
./src/graph/AGENTS.md:107:- **Environment Validation**: QWEN_EMBEDDING_MODEL and QWEN_RERANKER_MODEL must match LM Studio loaded models
./src/graph/graph.py:162:    """LangGraph node for math verification (gematria sanity checks via MATH_MODEL)."""
./src/graph/graph.py:163:    # Verify gematria calculations using MATH_MODEL
./src/nodes/math_verifier.py:7:Verifies gematria calculations using the MATH_MODEL for numeric sanity checks.
./src/nodes/math_verifier.py:26:    Verify gematria calculations using MATH_MODEL for numeric sanity checks.
./src/nodes/math_verifier.py:30:    2. Ask MATH_MODEL to verify the arithmetic
./src/nodes/math_verifier.py:39:    math_model = os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math")
./src/nodes/math_verifier.py:45:            message="MATH_MODEL not set, skipping verification",
./src/nodes/ai_noun_discovery.py:167:            discovery_model = os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b")
./src/nodes/enrichment.py:43:    theology_model = os.getenv("THEOLOGY_MODEL")
./src/nodes/enrichment.py:45:        raise ValueError("THEOLOGY_MODEL environment variable required")
./src/nodes/network_aggregator.py:192:    rerank_model = f"bge-m3-emb-proxy@{os.getenv('EMBEDDING_MODEL', 'text-embedding-bge-m3')}"
./src/nodes/network_aggregator.py:609:            model=os.getenv("QWEN_RERANKER_MODEL", "qwen-reranker"),
./src/nodes/network_aggregator.py:639:            rerank_model = os.getenv("QWEN_RERANKER_MODEL", "qwen-reranker")
./src/services/lmstudio_client.py:169:        embed_model = EMBEDDING_MODEL
./src/services/lmstudio_client.py:182:        rerank_model = RERANKER_MODEL
./src/services/lmstudio_client.py:265:THEOLOGY_MODEL = os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b")
./src/services/lmstudio_client.py:266:MATH_MODEL = os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math")
./src/services/lmstudio_client.py:267:EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
./src/services/lmstudio_client.py:268:RERANKER_MODEL = os.getenv("RERANKER_MODEL", "qwen-reranker")
./src/services/lmstudio_client.py:278:            if payload.get("model") == MATH_MODEL:
./src/services/lmstudio_client.py:339:            "model": THEOLOGY_MODEL,
./src/services/lmstudio_client.py:353:            "model": MATH_MODEL,
./src/services/lmstudio_client.py:378:            model: Model name (defaults to EMBEDDING_MODEL)
./src/services/lmstudio_client.py:397:        model = model or EMBEDDING_MODEL
./src/services/lmstudio_client.py:456:            model: Model name (defaults to RERANKER_MODEL)
./src/services/lmstudio_client.py:468:        model = model or RERANKER_MODEL
./src/services/rerank_via_embeddings.py:29:EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
./src/services/model_router.py:46:                name=os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b"),
./src/services/model_router.py:51:                fallback=os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b"),
./src/services/model_router.py:53:            "math": ModelConfig(name=os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math")),
./src/services/model_router.py:54:            "embedding": ModelConfig(name=os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")),
./src/services/model_router.py:55:            "reranker": ModelConfig(name=os.getenv("RERANKER_MODEL", "qwen.qwen3-reranker-0.6b")),
./.last_doctor.json:8:        "THEOLOGY_MODEL",
./.last_doctor.json:9:        "MATH_MODEL",
./.last_doctor.json:10:        "QWEN_EMBEDDING_MODEL",
./.last_doctor.json:11:        "QWEN_RERANKER_MODEL",
./.last_doctor.json:57:        "THEOLOGY_MODEL",
./.last_doctor.json:58:        "MATH_MODEL",
./.last_doctor.json:59:        "QWEN_EMBEDDING_MODEL",
./.last_doctor.json:60:        "QWEN_RERANKER_MODEL",
./.last_doctor.json:107:      "QWEN_EMBEDDING_MODEL": "text-embedding-qwen3-embedding-0.6b",
./.last_doctor.json:108:      "QWEN_RERANKER_MODEL": "qwen.qwen3-reranker-0.6b",
./backups/env/.env.20251107_101825.backup:22:THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
./backups/env/.env.20251107_101825.backup:23:MATH_MODEL=self-certainty-qwen3-1.7b-base-math
./backups/env/.env.20251107_101825.backup:24:EMBEDDING_MODEL=text-embedding-bge-m3
./backups/env/.env.20251107_101825.backup:25:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./test_bi_encoder_rerank.py:121:    assert "EMBEDDING_MODEL" in content, "Embedding model reference not found"
./AGENTS.md:44:  - **Default Models**: `EMBEDDING_MODEL=text-embedding-bge-m3`, `RERANKER_MODEL=qwen-reranker`, `THEOLOGY_MODEL=christian-bible-expert-v2.0-12b`
./AGENTS.md:341:4. **math_verifier**: Numeric verification of gematria calculations using MATH_MODEL (NEW)
./AGENTS.md:842:THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
./AGENTS.md:843:MATH_MODEL=self-certainty-qwen3-1.7b-base-math
./AGENTS.md:844:EMBEDDING_MODEL=text-embedding-bge-m3
./AGENTS.md:845:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./AGENTS.md:855:| `make ai.nouns`         | `discover_nouns_for_book()` | THEOLOGY_MODEL                   |
./AGENTS.md:856:| `make ai.enrich`        | enrichment loop             | THEOLOGY_MODEL                   |
./AGENTS.md:857:| `make ai.verify.math`   | gematria verification       | MATH_MODEL                       |
./AGENTS.md:859:| `make graph.score`      | rerank blend                | EMBEDDING_MODEL + RERANKER_MODEL |
./tools/smoke_lms_embeddings.py:7:model = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
./tools/genesis_autopilot.py:27:    "embed": os.environ.get("EMBED_MODEL_ID", os.environ.get("EMBEDDING_MODEL", "text-embedding-bge-m3")),
./share/env_example.txt:56:THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
./share/env_example.txt:57:MATH_MODEL=self-certainty-qwen3-1.7b-base-math
./share/env_example.txt:58:EMBEDDING_MODEL=text-embedding-bge-m3
./share/env_example.txt:59:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./share/projects/storymaker/AGENTS.md:55:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./share/projects/storymaker/AGENTS.md:56:EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b
./share/projects/storymaker/README.md:81:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./share/projects/storymaker/README.md:82:EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b
./share/AGENTS.md:44:  - **Default Models**: `EMBEDDING_MODEL=text-embedding-bge-m3`, `RERANKER_MODEL=qwen-reranker`, `THEOLOGY_MODEL=christian-bible-expert-v2.0-12b`
./share/AGENTS.md:341:4. **math_verifier**: Numeric verification of gematria calculations using MATH_MODEL (NEW)
./share/AGENTS.md:842:THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
./share/AGENTS.md:843:MATH_MODEL=self-certainty-qwen3-1.7b-base-math
./share/AGENTS.md:844:EMBEDDING_MODEL=text-embedding-bge-m3
./share/AGENTS.md:845:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./share/AGENTS.md:855:| `make ai.nouns`         | `discover_nouns_for_book()` | THEOLOGY_MODEL                   |
./share/AGENTS.md:856:| `make ai.enrich`        | enrichment loop             | THEOLOGY_MODEL                   |
./share/AGENTS.md:857:| `make ai.verify.math`   | gematria verification       | MATH_MODEL                       |
./share/AGENTS.md:859:| `make graph.score`      | rerank blend                | EMBEDDING_MODEL + RERANKER_MODEL |
./share/scripts_AGENTS.md:19:  - `EMBEDDING_MODEL=text-embedding-bge-m3`
./share/Makefile:830:	@PYTHONPATH=. $(PYTHON) scripts/pipeline_orchestrator.py embeddings --model $(EMBEDDING_MODEL) --dim $(EMBEDDING_DIM)
./share/Makefile:1071:	@python3 -c "import os,sys; names=['THEOLOGY_MODEL','MATH_MODEL','EMBEDDING_MODEL','RERANKER_MODEL']; missing=[n for n in names if not os.getenv(n)]; (sys.exit(f'MODELS_VERIFY_FAIL missing: {missing}') if missing else print('MODELS_VERIFY_OK'))"
./share/Makefile:1339:	@echo ">> Math Verifier Agent (gematria sanity via MATH_MODEL=$${MATH_MODEL:-self-certainty-qwen3-1.7b-base-math})"
./share/LM_STUDIO_SETUP.md:45:THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
./share/LM_STUDIO_SETUP.md:46:MATH_MODEL=self-certainty-qwen3-1.7b-base-math
./share/LM_STUDIO_SETUP.md:47:EMBEDDING_MODEL=text-embedding-bge-m3
./share/LM_STUDIO_SETUP.md:48:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./.cursor/rules/011-production-safety.mdc:15:- **Environment Validation**: QWEN_EMBEDDING_MODEL and QWEN_RERANKER_MODEL must match actual LM Studio loaded models.
./.cursor/rules/057-embedding-consistency.mdc:12:- **Model Name Consistency**: EMBEDDING_MODEL and RERANKER_MODEL must match loaded LM Studio models.
./.cursor/rules/062-environment-validation.mdc:64:export RERANKER_MODEL="qwen.qwen3-reranker-0.6b"
./.cursor/rules/062-environment-validation.mdc:65:export THEOLOGY_MODEL="christian-bible-expert-v2.0-12b"
./.cursor/rules/062-environment-validation.mdc:66:export EMBEDDING_MODEL="text-embedding-bge-m3"
./.cursor/rules/062-environment-validation.mdc:98:export RERANKER_MODEL="qwen.qwen3-reranker-0.6b"
./.cursor/rules/062-environment-validation.mdc:99:export THEOLOGY_MODEL="christian-bible-expert-v2.0-12b"
./.cursor/rules/062-environment-validation.mdc:100:export EMBEDDING_MODEL="text-embedding-bge-m3"
./.cursor/rules/062-environment-validation.mdc:123:export RERANKER_MODEL="qwen.qwen3-reranker-0.6b"
./.cursor/rules/062-environment-validation.mdc:124:export THEOLOGY_MODEL="christian-bible-expert-v2.0-12b"
./.cursor/rules/062-environment-validation.mdc:125:export EMBEDDING_MODEL="text-embedding-bge-m3"
./scripts/math_verifier.py:8:Standalone script to verify gematria calculations using MATH_MODEL.
./scripts/set_env.sh:10:export THEOLOGY_MODEL="christian-bible-expert-v2.0-12b"
./scripts/set_env.sh:12:export MATH_MODEL="self-certainty-qwen3-1.7b-base-math"
./scripts/set_env.sh:13:export EMBEDDING_MODEL="text-embedding-bge-m3"
./scripts/set_env.sh:14:export RERANKER_MODEL="qwen.qwen3-reranker-0.6b"
./scripts/set_env.sh:36:echo "  THEOLOGY_MODEL: $THEOLOGY_MODEL"
./scripts/set_env.sh:37:echo "  RERANKER_MODEL: $RERANKER_MODEL"
./scripts/set_env.sh:38:echo "  EMBEDDING_MODEL: $EMBEDDING_MODEL"
./scripts/repo_audit.py:107:    "EMBEDDING_MODEL",
./scripts/models_verify.py:67:        "model": os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3"),
./scripts/AGENTS.md:19:  - `EMBEDDING_MODEL=text-embedding-bge-m3`
./scripts/env/validate_env.sh:22:    "THEOLOGY_MODEL"
./scripts/env/validate_env.sh:23:    "MATH_MODEL"
./scripts/env/validate_env.sh:24:    "EMBEDDING_MODEL"
./scripts/env/validate_env.sh:25:    "RERANKER_MODEL"
./scripts/env_validate.sh:49:    local required_vars=("LM_STUDIO_HOST" "THEOLOGY_MODEL" "EMBEDDING_MODEL" "RERANKER_MODEL")
./scripts/env_validate.sh:66:        warn "  export THEOLOGY_MODEL=\"christian-bible-expert-v2.0-12b\""
./scripts/env_validate.sh:67:        warn "  export EMBEDDING_MODEL=\"text-embedding-bge-m3\""
./scripts/env_validate.sh:68:        warn "  export RERANKER_MODEL=\"qwen.qwen3-reranker-0.6b\""
./scripts/doctor.py:63:            "QWEN_EMBEDDING_MODEL",
./scripts/doctor.py:64:            "QWEN_RERANKER_MODEL",
./scripts/doctor.py:139:            os.environ.get("QWEN_EMBEDDING_MODEL"),
./scripts/doctor.py:140:            os.environ.get("QWEN_RERANKER_MODEL"),
./scripts/echo_env.py:18:    "EMBEDDING_MODEL",
./Makefile:830:	@PYTHONPATH=. $(PYTHON) scripts/pipeline_orchestrator.py embeddings --model $(EMBEDDING_MODEL) --dim $(EMBEDDING_DIM)
./Makefile:1071:	@python3 -c "import os,sys; names=['THEOLOGY_MODEL','MATH_MODEL','EMBEDDING_MODEL','RERANKER_MODEL']; missing=[n for n in names if not os.getenv(n)]; (sys.exit(f'MODELS_VERIFY_FAIL missing: {missing}') if missing else print('MODELS_VERIFY_OK'))"
./Makefile:1339:	@echo ">> Math Verifier Agent (gematria sanity via MATH_MODEL=$${MATH_MODEL:-self-certainty-qwen3-1.7b-base-math})"
./evidence/guards_all.after_merge.log:79:MODELS_VERIFY_FAIL missing: ['THEOLOGY_MODEL', 'MATH_MODEL', 'EMBEDDING_MODEL', 'RERANKER_MODEL']
./evidence/guards_all_with_xref_badges.tail:67:MODELS_VERIFY_FAIL missing: ['THEOLOGY_MODEL', 'MATH_MODEL', 'EMBEDDING_MODEL', 'RERANKER_MODEL']
./evidence/guards_all.log:78:MODELS_VERIFY_FAIL missing: ['THEOLOGY_MODEL', 'MATH_MODEL', 'EMBEDDING_MODEL', 'RERANKER_MODEL']
./evidence/guards.all.tail.txt:10:MODELS_VERIFY_FAIL missing: ['THEOLOGY_MODEL', 'MATH_MODEL', 'EMBEDDING_MODEL', 'RERANKER_MODEL']
./evidence/guards_all.triadfix.log:78:MODELS_VERIFY_FAIL missing: ['THEOLOGY_MODEL', 'MATH_MODEL', 'EMBEDDING_MODEL', 'RERANKER_MODEL']
./evidence/postmerge.guards.all.tail.txt:276:MODELS_VERIFY_FAIL missing: ['THEOLOGY_MODEL', 'MATH_MODEL', 'EMBEDDING_MODEL', 'RERANKER_MODEL']
./evidence/guard_env_usage.txt:3:  tools/smoke_lms_embeddings.py:7: model = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
./evidence/guard_env_usage.txt:8:  tools/genesis_autopilot.py:27: "embed": os.environ.get("EMBED_MODEL_ID", os.environ.get("EMBEDDING_MODEL", "text-embedding-bge-m3")),
./evidence/guard_env_usage.txt:50:  scripts/models_verify.py:67: "model": os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3"),
./evidence/guard_env_usage.txt:81:  scripts/doctor.py:138: os.environ.get("QWEN_EMBEDDING_MODEL"),
./evidence/guard_env_usage.txt:82:  scripts/doctor.py:139: os.environ.get("QWEN_RERANKER_MODEL"),
./evidence/guard_env_usage.txt:229:  src/infra/runs_ledger.py:54: "embedding_model": os.getenv("EMBEDDING_MODEL", "unknown"),
./evidence/guard_env_usage.txt:230:  src/infra/runs_ledger.py:55: "reranker_model": os.getenv("RERANKER_MODEL", "unknown"),
./evidence/guard_env_usage.txt:231:  src/infra/runs_ledger.py:56: "theology_model": os.getenv("THEOLOGY_MODEL", "unknown"),
./evidence/guard_env_usage.txt:232:  src/infra/runs_ledger.py:57: "math_model": os.getenv("MATH_MODEL", "unknown"),
./evidence/guard_env_usage.txt:253:  src/nodes/math_verifier.py:39: math_model = os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math")
./evidence/guard_env_usage.txt:258:  src/nodes/ai_noun_discovery.py:160: discovery_model = os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b")
./evidence/guard_env_usage.txt:263:  src/nodes/enrichment.py:44: theology_model = os.getenv("THEOLOGY_MODEL")
./evidence/guard_env_usage.txt:281:  src/nodes/network_aggregator.py:192: rerank_model = f"bge-m3-emb-proxy@{os.getenv('EMBEDDING_MODEL', 'text-embedding-bge-m3')}"
./evidence/guard_env_usage.txt:282:  src/nodes/network_aggregator.py:606: model=os.getenv("QWEN_RERANKER_MODEL", "qwen-reranker"),
./evidence/guard_env_usage.txt:283:  src/nodes/network_aggregator.py:636: rerank_model = os.getenv("QWEN_RERANKER_MODEL", "qwen-reranker")
./evidence/guard_env_usage.txt:293:  src/services/lmstudio_client.py:247: THEOLOGY_MODEL = os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b")
./evidence/guard_env_usage.txt:294:  src/services/lmstudio_client.py:248: MATH_MODEL = os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math")
./evidence/guard_env_usage.txt:295:  src/services/lmstudio_client.py:249: EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
./evidence/guard_env_usage.txt:296:  src/services/lmstudio_client.py:250: RERANKER_MODEL = os.getenv("RERANKER_MODEL", "qwen-reranker")
./evidence/guard_env_usage.txt:299:  src/services/rerank_via_embeddings.py:29: EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
./evidence/guard_env_usage.txt:300:  src/services/model_router.py:46: name=os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b"),
./evidence/guard_env_usage.txt:303:  src/services/model_router.py:51: fallback=os.getenv("THEOLOGY_MODEL", "christian-bible-expert-v2.0-12b"),
./evidence/guard_env_usage.txt:304:  src/services/model_router.py:53: "math": ModelConfig(name=os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math")),
./evidence/guard_env_usage.txt:305:  src/services/model_router.py:54: "embedding": ModelConfig(name=os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")),
./evidence/guard_env_usage.txt:306:  src/services/model_router.py:55: "reranker": ModelConfig(name=os.getenv("RERANKER_MODEL", "qwen.qwen3-reranker-0.6b")),
./evidence/guard_env_usage.txt:336:  tests/integration/test_ai_enrichment_node.py:73: assert os.getenv("THEOLOGY_MODEL")
./evidence/guard_env_usage.txt:436:  tests/smoke/test_models.py:77: model = os.getenv("EMBEDDING_MODEL", "text-embedding-bge-m3")
./evidence/guards_all.final.log:78:MODELS_VERIFY_FAIL missing: ['THEOLOGY_MODEL', 'MATH_MODEL', 'EMBEDDING_MODEL', 'RERANKER_MODEL']
./evidence/pr390.Makefile.pr:789:	@PYTHONPATH=. $(PYTHON) scripts/pipeline_orchestrator.py embeddings --model $(EMBEDDING_MODEL) --dim $(EMBEDDING_DIM)
./evidence/pr390.Makefile.pr:885:	@python3 -c "import os,sys; names=['THEOLOGY_MODEL','MATH_MODEL','EMBEDDING_MODEL','RERANKER_MODEL']; missing=[n for n in names if not os.getenv(n)]; (sys.exit(f'MODELS_VERIFY_FAIL missing: {missing}') if missing else print('MODELS_VERIFY_OK'))"
./evidence/pr390.Makefile.pr:1149:	@echo ">> Math Verifier Agent (gematria sanity via MATH_MODEL=$${MATH_MODEL:-self-certainty-qwen3-1.7b-base-math})"
./evidence/guards_all.after_fix.log:78:MODELS_VERIFY_FAIL missing: ['THEOLOGY_MODEL', 'MATH_MODEL', 'EMBEDDING_MODEL', 'RERANKER_MODEL']
./evidence/agents.dsn.excerpts.txt:21:292:4. **math_verifier**: Numeric verification of gematria calculations using MATH_MODEL (NEW)
./evidence/agents.dsn.excerpts.txt:34:790:| `make ai.verify.math`   | gematria verification       | MATH_MODEL                       |
./evidence/agents.dsn.txt:15:292:4. **math_verifier**: Numeric verification of gematria calculations using MATH_MODEL (NEW)
./evidence/agents.dsn.txt:29:790:| `make ai.verify.math`   | gematria verification       | MATH_MODEL                       |
./docs/ADRs/ADR-010-qwen-integration.md:41:- **Environment Variables**: `USE_QWEN_EMBEDDINGS`, `QWEN_EMBEDDING_MODEL`, `QWEN_RERANKER_MODEL`
./docs/ADRs/ADR-010-qwen-integration.md:119:QWEN_EMBEDDING_MODEL=qwen-embed   # Embedding model name
./docs/ADRs/ADR-010-qwen-integration.md:120:QWEN_RERANKER_MODEL=qwen-reranker # Reranker model name
./docs/projects/storymaker/AGENTS.md:55:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./docs/projects/storymaker/AGENTS.md:56:EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b
./docs/projects/storymaker/README.md:81:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./docs/projects/storymaker/README.md:82:EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b
./docs/SSOT/data_flow.md:275:        EMBEDDING_MODEL[Qwen Embedding<br/>text-embedding-qwen3-embedding-0.6b]
./docs/SSOT/data_flow.md:276:        RERANKER_MODEL[Qwen Reranker<br/>qwen.qwen3-reranker-0.6b]
./docs/SSOT/data_flow.md:308:    EMBEDDING_MODEL --> EMBED_API
./docs/SSOT/data_flow.md:316:    RERANKER_MODEL --> RERANK_FILTER
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:164:THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:165:MATH_MODEL=self-certainty-qwen3-1.7b-base-math
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:166:EMBEDDING_MODEL=text-embedding-bge-m3
./docs/runbooks/SETUP_LM_STUDIO_AND_DB.md:167:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./docs/runbooks/LM_STUDIO_SETUP.md:45:THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
./docs/runbooks/LM_STUDIO_SETUP.md:46:MATH_MODEL=self-certainty-qwen3-1.7b-base-math
./docs/runbooks/LM_STUDIO_SETUP.md:47:EMBEDDING_MODEL=text-embedding-bge-m3
./docs/runbooks/LM_STUDIO_SETUP.md:48:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./docs/runbooks/USAGE_PATTERNS_REFERENCE.md:140:THEOLOGY_MODEL=christian-bible-expert-v2.0-12b
./docs/runbooks/USAGE_PATTERNS_REFERENCE.md:141:MATH_MODEL=self-certainty-qwen3-1.7b-base-math
./docs/runbooks/USAGE_PATTERNS_REFERENCE.md:142:EMBEDDING_MODEL=text-embedding-bge-m3
./docs/runbooks/USAGE_PATTERNS_REFERENCE.md:143:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./docs/qwen_integration.md:55:EMBEDDING_MODEL=text-embedding-bge-m3
./docs/qwen_integration.md:56:RERANKER_MODEL=qwen.qwen3-reranker-0.6b
./docs/qwen_integration.md:306:   - Update `.env` with correct model IDs: `EMBEDDING_MODEL=text-embedding-bge-m3`, `RERANKER_MODEL=qwen.qwen3-reranker-0.6b`

## Current LM Studio Installation

total 56
drwxrwxr-x 13 mccoy mccoy 4096 Nov 12 08:09 .
drwxr-x--- 53 mccoy mccoy 4096 Nov 15 13:42 ..
drwxrwxr-x  2 mccoy mccoy 4096 Nov 12 08:09 bin
drwxrwxr-x  2 mccoy mccoy 4096 Oct 19 11:20 config-presets
drwxrwxr-x  2 mccoy mccoy 4096 Oct 19 12:50 conversations
drwxrwxr-x  2 mccoy mccoy 4096 Sep 30 20:28 credentials
drwxrwxr-x  5 mccoy mccoy 4096 Sep 30 20:28 extensions
drwxrwxr-x  4 mccoy mccoy 4096 Sep 30 20:28 hub
drwxrwxr-x 13 mccoy mccoy 4096 Nov 12 20:31 .internal
-rw-rw-r--  1 mccoy mccoy   95 Oct 19 12:49 mcp.json
drwxrwxr-x  9 mccoy mccoy 4096 Oct 23 18:44 models
drwxrwxr-x  5 mccoy mccoy 4096 Nov  4 10:27 server-logs
drwxrwxr-x  2 mccoy mccoy 4096 Sep 30 20:28 user-files
drwxrwxr-x  2 mccoy mccoy 4096 Oct 17 20:09 working-directories

## Summary and Findings

- LM Studio CLI: ~/.lmstudio/bin/lms available
- Historical port: 9994 (from AGENTS.md and old code)
- DB startup: systemctl start postgresql (systemd)
- Models: THEOLOGY_MODEL, MATH_MODEL, EMBEDDING_MODEL, RERANKER_MODEL
- Resolver: lmstudio_resolver.base_url() for endpoint detection
- GUI launch: lmstudio command or AppImage
