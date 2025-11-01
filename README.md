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

## Pushing changes
A remote is not configured by default. Add the desired remote (for example, `git remote add origin <url>`) and push normally once credentials are available.
