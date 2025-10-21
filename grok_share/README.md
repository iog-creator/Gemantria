# Gemantria v2 - Current Progress (PR-001 Complete)

## Overview
This is a snapshot of our progress building a deterministic, resumable LangGraph pipeline for gematria data processing. We've completed PR-001 (Postgres Checkpointer) and are ready for PR-002 (bible_db RO validation).

## Architecture Overview

### Core Components Built
- **LangGraph Pipeline**: Minimal hello runner with checkpointer infrastructure
- **Hebrew Processing**: NFKD→strip→NFC normalization, Mispar Hechrachi gematria
- **Checkpointer System**: Postgres placeholder + Memory fallback via `CHECKPOINTER=postgres|memory`
- **Agent Framework**: Comprehensive governance via AGENTS.md and .cursor rules
- **Testing**: 100% coverage with unit + integration tests

### Database Design
- `bible_db`: Read-only source database (RO enforced in PR-002)
- `gematria`: Read-write processing database
- Environment variables: `GEMATRIA_DSN`, `BIBLE_DB_DSN`

## Key Files Structure

```
grok_share/
├── src/                    # Source code
│   ├── core/              # Hebrew processing & identity
│   │   ├── ids.py         # Normalization & content hashing
│   │   └── hebrew_utils.py # Gematria calculations
│   ├── graph/             # LangGraph pipeline
│   │   └── graph.py       # Hello runner + checkpointer wiring
│   └── infra/             # Infrastructure
│       └── checkpointer.py # Postgres + Memory checkpointers
├── tests/                 # 100% coverage test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                  # Documentation
│   ├── ADRs/              # Architectural decisions
│   └── MASTER_PLAN.md     # Phase 0 acceptance criteria
├── cursor_rules/          # Agent governance rules
├── AGENTS.md              # Agent framework documentation
├── pyproject.toml         # Tool configuration
├── requirements.txt       # Dependencies (pinned to majors)
├── Makefile               # Development commands
└── .env.example           # Environment variables template
```

## Current Status

### ✅ Completed (PR-000 + PR-001)
- **Agent Framework**: AGENTS.md governance with 7 Cursor rules
- **Code Quality**: Lint, type, 100% coverage, no mocks
- **Hebrew Processing**: Verified Adam=45, Hevel=37 normalization
- **Checkpointer Infrastructure**: Factory pattern with env-driven selection
- **Testing**: Comprehensive unit + integration tests

### 🚀 Next Steps (PR-002)
- `bible_db` read-only validation with parameterized SQL
- Connection pooling and RO role enforcement
- Integration with validation nodes

## Quality Gates
- **Linting**: ruff (E, F, I, UP, B, SIM)
- **Type Checking**: mypy strict mode
- **Coverage**: ≥98% (currently 100%)
- **Security**: No mocks, parameterized SQL, RO db policy

## Key Rules & Priorities
1. **Code > bible_db > LLM** (LLM = metadata only)
2. **Determinism**: content_hash identity, uuidv7 surrogates
3. **Safety**: bible_db read-only, fail-closed if <50 nouns

## Getting Started
```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run gates
make lint type test.unit test.integration coverage.report
```

## Agent Governance
See `AGENTS.md` for complete agent framework documentation. Key rules:
- Always consult AGENTS.md before multi-step tasks
- Test-first development, small green PRs
- Documentation lockstep with code changes
