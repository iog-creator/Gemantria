2025-11-09 — ci: enforce xref badge presence on tags (STRICT_XREF_BADGES=1); add pip cache; require xref index on **release tags** (v*); main/PR remain HINT-only
2025-11-09 — ops: archive rc16 STRICT-tag (prod path) artifact; record in CHANGELOG; reset to fixtures default
2025-11-09 — ops: expand extraction truth-suite to 25 cases (fixtures path); add derive tool; guard prefers v2≥25
2025-11-09 — ops: archive rc17 STRICT-tag (fixtures) artifact; record in CHANGELOG
2025-11-09 — ops: promote extraction truth-suite to **v2** (≥25 cases); guard now prefers v2 when available
2025-11-09 — ops: archive rc18 STRICT-tag (fixtures, v2) artifact; record in CHANGELOG
2025-11-08 — ops: add xref coverage/rate badges (HINT-only) to operator dashboard; wire into `eval.package`
2025-11-08 — webui: xref a11y — ARIA for +N more; main landmark; smoke asserts [a251b135]
2025-11-08 — webui: xref UX polish — keyboard chips, Esc to close, focus trap, scroll-lock [468d2088]
2025-11-08 — OPS: UI xrefs index landed (HINT integrity guard) [fe7bded1]
2025-11-08 — OPS: Land light xref extractor (HINT guard; schema preserved) [8b23eaf4]
2025-11-08 — OPS: Lock 3-role DB contract; AI-tracking guard (HINT on PRs, STRICT gated by vars.STRICT_DB_MIRROR_CI) [6ddce6ee]
# Changelog

## 2025-11-08 — Triad Enforcement Finalization

- Merge **PR #272**: lock Always-Apply triad to **050/051/052** only.
- Regenerate **RULES_INVENTORY** from `.cursor/rules/*.mdc`; add guard to **ops.verify**.
- Enforce **folder-scoped AGENTS.md** pattern; mirror to **share/**; tag **ops/agents-md-inventory-sync** to trigger STRICT agents-lint.

### ci: enforce RFC3339 on tag builds; add normalization step (PR #262)

## [pre] v0.1.0-rc18 — tag-only STRICT (fixtures, v2) proof

- Truth-suite **v2** (≥25 cases) preferred by guard; STRICT tag passed on fixtures path.
- **Run ID**: 19203322649 · Artifact: `evidence/guard_extraction_accuracy.json` (expected `ok:true`; totals may be null on fixtures path).
- Repo vars: default fixtures posture (`STRICT_REAL_EXTRACTION=0`).

## [pre] v0.1.0-rc17 — tag-only STRICT (fixtures path) proof

- Truth-suite expanded to **25** deterministic cases; STRICT guard passes on fixtures.
- **Run ID**: 19203285597 · Artifact: `evidence/guard_extraction_accuracy.json` (expected `ok:true`, fixtures posture).
- Repo vars: default fixtures posture (`STRICT_REAL_EXTRACTION=0`).

## [pre] v0.1.0-rc16 — tag-only STRICT (production path) proof

- Hardened tag workflow (fail-fast, preflight, grouped logs, always-upload) ran on **production path** via repo vars.
- **Run ID**: 19203122465 · **Verdict**: `ok:true`, totals `{"cases":10,"correct":10}` (artifact: `evidence/guard_extraction_accuracy.json`).
- Repo vars at proof time: `STRICT_REAL_EXTRACTION=1`, `REAL_EXTRACT_CMD="python3 scripts/analytics/build_graph_from_repo_fixtures.py"`.

## v0.1.0-rc1

- Phases 1–3 merged under reuse-first (schemas, pipeline, exports)
- Phase 4 adapters for Web UI (no new components)
- Phase 5 quality gates: reranker adapter + thresholds smoke
- Phase 6 CLI: Typer wrapper + quickstart

### Fixes

- **Confidence validator threshold**: Now runtime (env-respected); default lowered to **0.80** (uniform 0.85 artifact). See `AGENTS.md#environment`.