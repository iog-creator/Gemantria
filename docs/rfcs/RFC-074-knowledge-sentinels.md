# RFC-074: Knowledge Sentinels (Drift Kill-Switch)

- **Author:** PM (GPT-5 Thinking)
- **Date:** 2025-11-11
- **Status:** Proposed
- **Related:** Rule-050/051/052 (Always-Apply triad), RFC-073 (tagproof RO-DSN), DSN centralization guard

## Summary

Introduce **Knowledge Sentinels**: a repo guard + hints layer that fails-closed in STRICT/tag builds if required governance/docs/agents/DSN entrypoints drift or disappear. In HINT/dev it prints actionable gaps.

## Motivation

We observed drift where Cursor/PM forget features, rules, and docs. DSN policy exists but wasn't uniformly enforced as a *knowledge* presence gate. We need an automated "are the rails still on?" signal.

## Proposal

1) Add `scripts/ci/guard_knowledge.py` that checks for:

   - Governance sentinels: `RULES_INDEX.md` includes 050/051/052.

   - SSOT prompt sentinel: `docs/SSOT/GPT_SYSTEM_PROMPT.md` *or* `GPT_SYSTEM_PROMPT.md`.

   - Agents sentinel: `AGENTS.md` has "Always-Apply Triad" callout and Release/Operator section.

   - DSN loader sentinel: `scripts/config/env.py` exports `env`, `get_ro_dsn`, `get_rw_dsn`.

   - Tagproof entrypoints: `scripts/exports/export_graph_core.py`, `.github/workflows/tagproof-core-export.yml`.

   - DSN guard workflow: `.github/workflows/dsn-guard-tags.yml`.

   - Master Reference lane: `scripts/ops/master_ref_populate.py` and Make targets present.

   - Atlas sentinel: at least one of `docs/atlas/*` **or** `webui/graph/*` **or** `ui/*` (browser hub path).

2) Make targets:

   - `guard.knowledge.hints` (HINT): emit JSON with missing items; never fail CI on PRs by default.

   - `guard.knowledge.strict` (STRICT/tag): fail when *critical* sentinels missing.

3) CI: run STRICT on tags only (no nightlies).

## Scope

Guard + Make targets + docs clarification. No runtime behavior changes beyond guards.

## Acceptance Criteria

- HINT target prints structured JSON and lists all missing sentinels.

- STRICT target fails when any *critical* sentinel is missing (triad, DSN loader, tagproof exporter, DSN guard workflow).

- Tag build passes with all sentinels present; fails if any are removed.

## QA Checklist

- No DB/network calls.

- Works with missing optional paths by design.

- Produces `evidence/guard_knowledge.json` for audits.

## Links

- Rule-050/051/052, RFC-073, DSN centralization guard.

