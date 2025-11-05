# AGENTS.md - src/utils Directory

## Directory Purpose

The `src/utils/` directory contains utils components for the Gematria analysis pipeline.

## Key Components

<!-- Add key components and their purposes here -->

## API Contracts

<!-- Add function/class signatures and contracts here -->

## Testing Strategy

<!-- Add testing approach and coverage requirements here -->

## Development Guidelines

<!-- Add coding standards and patterns specific to this directory here -->

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


## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
<!-- Add ADR references here -->
