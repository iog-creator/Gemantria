# PLAN-072 — Milestone 2: Extraction Agents Correctness (hermetic)

## Objectives
- Define TVs for extraction correctness (TV-E01..E05) with golden fixtures.
- Add hermetic guard `guard_extraction_agents.py` (no DB/network).
- Wire pytest collection under `agentpm/tests/extractors/` (unit-only).
- Keep Tool Bus OFF; adapters RO-only on tag lane (no PR CI probes).

## Deliverables
- Tests: `agentpm/tests/extractors/test_extraction_correctness.py` (TV-E01..E05 placeholders).
- Fixtures: `agentpm/tests/extractors/fixtures/*.json` (tiny goldens).
- Guard: `scripts/ci/guard_extraction_agents.py` + `make guard.extractors`.
- Plan acceptance: ruff green, guard dry-run OK, CI hermetic.

## Out-of-scope
- DB writes, Tool Bus, UI changes, network probes.
