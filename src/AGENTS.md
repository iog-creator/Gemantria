# AGENTS.md - src/ Directory

## Directory Purpose

Core pipeline agents, data structures for gematria calc, correlations.

## Key Components

- correlations.py: Pattern engine (Related ADRs: 018)
- temporal.py: Span generation

## Development Workflow

- Use codex.task for codegen
- Always sync share/ after runs

## Housekeeping (Rule 058)

After ANY code changes in this directory, run comprehensive housekeeping:

```bash
# Rule 058 mandatory housekeeping checklist
python3 scripts/rules_audit.py
make share.sync
python3 scripts/generate_forest.py
ruff format --check . && ruff check .
# Check if ADR needed/updated (Rule 029)
PYTHONPATH=. python3 -m pytest tests/ -v --tb=short
# Verify docs updated (AGENTS.md, SSOT, README)
```

**DO NOT SKIP ANY STEP.** See [Rule 058](../../.cursor/rules/058-auto-housekeeping.mdc) for complete checklist.

## Related ADRs: 001,002,003,018

## Related Rules: 006,017,058