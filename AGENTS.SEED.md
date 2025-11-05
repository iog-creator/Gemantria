# Gemantria Agent Framework - Seed

## Mission
Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts.

## Priorities
1) Correctness: Code gematria > bible_db > LLM (LLM = metadata only)
2) Determinism: content_hash identity; uuidv7 surrogate; fixed seeds; position_index
3) Safety: bible_db is READ-ONLY; parameterized SQL only; fail-closed if <50 nouns

## Environment Setup
```bash
# Python environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Database connections
export GEMATRIA_DSN="postgresql://..."
export BIBLE_DB_DSN="postgresql://..."

# Model configuration
export INFERENCE_PROVIDER=lmstudio
export EMBEDDING_MODEL=text-embedding-bge-m3
```

## Pipeline Execution
```bash
# Full pipeline run
make orchestrator.full BOOK=Genesis

# Individual stages
make orchestrator.pipeline BOOK=Genesis
make orchestrator.analysis OPERATION=all

# Validation
make schemas.normalize
make exports.guard
make exports.verify
```

## Data Integrity
- **Staging Schema:** `staging.*_norm` tables with constraints
- **Normalization:** Canonical JSON field mappings
- **Guards:** Pre-insertion validation prevents corruption
- **ADR-029:** Schema normalization infrastructure

## Export Formats
- `exports/graph_latest.json` - Main graph data
- `exports/graph_stats.json` - Statistics and metrics
- `exports/graph_patterns.json` - Pattern analysis
- `exports/temporal_patterns.json` - Time-series analysis
- `exports/pattern_forecast.json` - Forecasting results

## Quality Assurance
- **Rules Audit:** `python scripts/rules_audit.py`
- **Share Sync:** `make share.sync`
- **Forest Regen:** `python scripts/generate_forest.py`
- **Code Quality:** `ruff format --check . && ruff check .`

## Governance
- **ADR Required:** Major changes need documentation
- **Rule 029:** ADR coverage for architectural decisions
- **Rule 058:** Mandatory housekeeping after changes
