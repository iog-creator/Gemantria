# RFC-073: Tagproof Core Graph Exports via Read-Only DSN (STRICT)

- **Author:** PM (GPT-5 Thinking)

- **Date:** 2025-11-11

- **Status:** Proposed

- **Related:** #386 (guard precision), #387 (patterns normalization + `--allow-empty` sim)

## Summary

On **tag builds**, generate a canonical **core graph artifact** from a **read-only Postgres DSN** *before* running schema guards, so `guard.graph.core.schema` can validate real data. Keep tags **STRICT** (no placeholders, no `--allow-empty`).

## Motivation

Tagproof shows `graph_core` fails (no matching files), while `graph_stats`, `graph_patterns`, and `graph_correlations` pass. This is correct—tags should validate real artifacts—but we currently do not emit a core graph on tags.

## Proposal (One-Path)

1. **Canonical artifact & path**

   - File: `ui/out/graph_core.json`

   - Contract: `graph.schema.json` (core graph only; excludes stats/patterns/correlations)

2. **RO-DSN input**

   - Use **read-only** DSN env var: `BIBLE_DB_DSN` (preferred) or `GEMATRIA_RO_DSN` fallback.

   - Absolutely **no writes**; SELECTs only.

3. **Build step (tag-only)**

   - New Make target: `exports.graph.core.tagproof`

   - Trigger when `GITHUB_REF_TYPE=tag` **and** a RO DSN is present.

   - Implementation sketch (separate PR after RFC acceptance):

     - `scripts/exports/export_graph_core.py` connects with RO DSN, queries the minimal node/edge view, and writes `ui/out/graph_core.json` conforming to `graph.schema.json`.

4. **Guards**

   - Tags: run `guard.graph.core.schema` (STRICT) against `ui/out/graph_core.json` (no `--allow-empty`).

   - Non-tag simulations: may continue to use `--allow-empty` **only** for the *core* guard when explicitly requested (already landed in #387).

5. **Failure mode**

   - If RO DSN is **missing** or export fails, tag build **fails** with a clear message:

     > "Tag build requires a read-only DSN to generate ui/out/graph_core.json."

## Scope

- **In**: Tag CI workflow, Makefile wiring, export script, docs.

- **Out**: Changing schema contracts; write-side pipelines; stats/patterns/correlations (already passing).

## Acceptance Criteria

1. **Tagproof PASS (core):** On a local temporary tag with valid RO DSN, `ui/out/graph_core.json` is produced and `guard.graph.core.schema` exits **0**.

2. **Tagproof FAIL (no DSN):** With RO DSN unset, the tag build fails before guards with the explicit error above.

3. **Non-tag unaffected:** HINT/STRICT simulations behave as today; `--allow-empty` remains **disallowed** for tag builds.

4. **Hermetic CI:** No external network. DSN must be configured as a GitHub environment secret/variable; job must **fail-closed** when unavailable.

5. **Docs & governance:** README/AGENTS mention tag-only RO export; RULES_INDEX references this RFC.

## QA Checklist

- [ ] Export script unit tests (mock DB) validate envelope + schema conformance.

- [ ] Make target only reads, never writes (DB role `SELECT` only).

- [ ] CI logs show DSN source redacted (`<REDACTED>`).

- [ ] Guard outputs archived under `evidence/` with summaries.

## Risks

- DSN provisioning on tag runners; mitigate via repo environment + protected branches.

- Export runtime flakiness; mitigate with clear retries + fail-fast messaging.

## Implementation Plan (post-acceptance)

- PR-1: Add `scripts/exports/export_graph_core.py` + `make exports.graph.core.tagproof`.

- PR-2: Wire tag workflow job: `if: ${{ github.ref_type == 'tag' }}` then run export, then guards.

- PR-3: Docs updates + badge showing core guard status on latest tag.

## Links

- #386 — Guard precision & split schema checks

- #387 — Pattern normalization + `--allow-empty` simulations

- Tagproof evidence: graph_core FAIL due to missing artifact (expected)
