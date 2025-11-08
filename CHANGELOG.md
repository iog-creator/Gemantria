2025-11-08 — OPS: Land light xref extractor (HINT guard; schema preserved) [8b23eaf4]
2025-11-08 — OPS: Lock 3-role DB contract; AI-tracking guard (HINT on PRs, STRICT gated by vars.STRICT_DB_MIRROR_CI) [6ddce6ee]
# Changelog

## 2025-11-08 — Triad Enforcement Finalization

- Merge **PR #272**: lock Always-Apply triad to **050/051/052** only.
- Regenerate **RULES_INVENTORY** from `.cursor/rules/*.mdc`; add guard to **ops.verify**.
- Enforce **folder-scoped AGENTS.md** pattern; mirror to **share/**; tag **ops/agents-md-inventory-sync** to trigger STRICT agents-lint.

### ci: enforce RFC3339 on tag builds; add normalization step (PR #262)

## v0.1.0-rc1

- Phases 1–3 merged under reuse-first (schemas, pipeline, exports)
- Phase 4 adapters for Web UI (no new components)
- Phase 5 quality gates: reranker adapter + thresholds smoke
- Phase 6 CLI: Typer wrapper + quickstart

### Fixes

- **Confidence validator threshold**: Now runtime (env-respected); default lowered to **0.80** (uniform 0.85 artifact). See `AGENTS.md#environment`.