# Gemantria

This repository contains the planning scaffolding, lightweight gematria helpers, and hello-graph flow that anchor the larger rebuild effort.

## Local development
1. Create and activate a virtual environment (for example `.venv`).
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the lints and tests:
   - `make lint`
   - `make type`
   - `make test.unit`
   - `make coverage.report`

## Quick Start (5 minutes, hermetic)

Use the reuse-first CLI wrapper (no new logic):

```
python3 scripts/cli/gemantria_cli.py quickstart
# or simply:
make cli.quickstart
```

Key knobs (already in your env): `EDGE_STRONG`, `EDGE_WEAK`, `CANDIDATE_POLICY`, `PIPELINE_SEED`.

## Project structure
- `docs/`: ADRs and the SSOT master plan that describe the rebuild objectives.
- `schemas/`: JSON schema placeholders for contract validation.
- `src/`: Minimal core, graph, and infrastructure modules that drive the hello-graph runner.
- `tests/`: Focused unit tests with a mini coverage plug-in enforcing the 98% threshold.

## Quality & Trends

Local smoke artifacts (run via the eval tools) can render quality trends:

![Quality Trend](share/eval/badges/quality_trend.svg)
![Current Quality](share/eval/badges/quality.svg)

> In CI these are uploaded as artifacts; `share/**` remains read-only during CI.

## Required Checks

Main branch requires these checks to pass before merging:

![Ruff Format & Lint](https://img.shields.io/github/actions/workflow/status/mccoy/Gemantria.v2/enforce-ruff.yml?label=ruff&branch=main)
![CI Build](https://img.shields.io/github/actions/workflow/status/mccoy/Gemantria.v2/ci.yml?label=ci&branch=main)

> Branch protection requires: `ruff` (formatting + linting) and `build` (CI pipeline)

## Pushing changes
A remote is not configured by default. Add the desired remote (for example, `git remote add origin <url>`) and push normally once credentials are available.

## Developer Validation (Phase-9)

Local-only helpers (CI no-ops):

```bash
make ingest.local.validate
make ingest.local.validate.schema
```

See `docs/phase9/VALIDATION_README.md` for env knobs (SNAPSHOT_FILE, P9_SEED).

- Snapshot prep guide: see `docs/phase9/SNAPSHOTS.md`.
