# Gemantria Project Context

## Mission
Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts.

## Priorities
1. **Correctness**: Code gematria > bible_db > LLM (LLM = metadata only)
2. **Determinism**: content_hash identity; uuidv7 surrogate; fixed seeds; position_index
3. **Safety**: bible_db is READ-ONLY; parameterized SQL only; fail-closed if <50 nouns (ALLOW_PARTIAL=1 is explicit)

## Environment Setup
```bash
# Virtual environment
python -m venv .venv && source .venv/bin/activate

# Dependencies
make deps

# Databases
export BIBLE_DB_DSN=postgresql://...  # read-only Bible database
export GEMATRIA_DSN=postgresql://...  # read/write application database

# Batch configuration
export BATCH_SIZE=50  # default noun batch size
export ALLOW_PARTIAL=0|1  # if 1, manifest must capture reason
export PARTIAL_REASON="<string>"  # required when ALLOW_PARTIAL=1

# Checkpointer
export CHECKPOINTER=postgres|memory  # default: memory for CI/dev
```

## Workflow Rules
- **Branch**: `feature/<short>` → write tests first → code → `make lint type test.unit test.int coverage.report` → commit → push → PR
- **Coverage**: ≥98%
- **Commit message**: `feat(area): what [no-mocks, deterministic, ci:green]`
- **PR format**: Goal, Files, Tests, Acceptance

## Code Quality Standards
- **Formatting**: Ruff format (single source of truth)
- **Linting**: Ruff check with zero tolerance
- **Type checking**: MyPy with `ignore_missing_imports=True`
- **Line length**: 120 characters maximum
- **Imports**: All at module top (no mid-file imports)

## Key Rules & Constraints

### Hebrew Normalization
- NFKD → strip combining → strip maqaf (U+05BE)/sof pasuq (U+05C3)/punct → NFC
- Mispar Hechrachi; finals=regular
- Surface-form gematria with calc strings

### Database Safety
- bible_db is READ-ONLY (RO adapter denies writes pre-connection)
- Parameterized SQL only
- No mock datasets or __mocks__ folders

### Batch Semantics
- Default: 50 nouns per batch
- Abort + write review.ndjson on failure
- ALLOW_PARTIAL=1 override logs manifest
- Batches: shared_prime (cap k=3); optional identical_value/gcd_gt_1 behind flags

### LLM Integration
- LM Studio only when enabled
- Confidence is metadata only
- Qwen Live Gate: ENFORCE_QWEN_LIVE=1 → assert_qwen_live() must pass before network aggregation

### Graph & Visualization
- Layouts persisted with (algorithm, params_json, seed, version)
- Edge reranking: edge_strength = 0.5*cos + 0.5*rerank
- Edges classified as strong (≥0.90), weak (≥0.75), or other

## CI Verification
- **Empty DB tolerance**: Handle missing tables gracefully (zero counts allowed)
- **Stats validation**: Zero nodes/edges when DB tables don't exist
- **File tolerance**: Missing graph/stats files use empty defaults
- **SSOT validation**: PR-diff scoped JSON validation against schemas
- **Required checks**: `ruff` (format + lint), `build` (CI pipeline)

## Operations
- **Share sync**: `make share.sync` after docs/scripts/rules changes
- **Branch protection**: CODEOWNERS reviews + required checks
- **Release process**: Auto-generated notes with semver compliance

## Makefile Targets
```bash
# Quality gates
make lint type test.unit test.int coverage.report

# Pipeline operations
make book.smoke eval.graph.calibrate.adv ci.exports.smoke

# Share synchronization
make share.sync

# Agent operations (local-only)
make codex.task TASK="..."  # Existing Codex integration
make gemini.task TASK="..."  # New Gemini CLI
```

## GitHub Operations
- Use MCP server for issues/PRs/search
- Confirm ownership before operations
- Search before creating new issues
- Use Copilot for AI-assisted tasks

## Safety Gates
- No outbound network in CI (hermetic validators only)
- No share/ writes in CI (route to _artifacts/)
- Ruff-format is single formatter SSOT
- Schema/algorithm changes require ADR + tests (+ migrations if DB)
