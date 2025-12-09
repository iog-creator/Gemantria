# PLAN-080 — Guarded Tool Calls P0 Execution (jsonschema + PoR + adapters + TVs)

**Context.** P0 scaffold + naming are merged. This plan implements execution logic safely and hermetically in PR checks, with DSN/STRICT proofs confined to tag lanes.

## Objectives

- **Validation:** Integrate `jsonschema` validation for all P0 tool I/O schemas (with `$ref` to provenance).

- **PoR (Proof-of-Readback):** Gatekeeper/Guard enforce readback of constraints/tokens before any tool call.

- **Adapters (RO):** Minimal Postgres adapter that reads `mcp.v_catalog` via centralized DSN loader; no writes in PR CI.

- **TVs:** Turn **TV-01..TV-05** green (missing-PoR, forbidden-tool, bad-args, ring-violation, bus-parity placeholder).

- **No Tool Bus:** Keep Tool Bus OFF by default (config defaults unchanged).

## Deliverables

- `pmagent/guard/impl.py`: `validate_first_response`, `validate_tool_call`, `record_violation` (stub write path, no CI DB writes).

- `pmagent/gatekeeper/impl.py`: `build_capability_session` (deterministic checklists + policy snapshot).

- `pmagent/adapters/mcp_db.py`: RO adapter using centralized DSN loader; skips on CI unless STRICT lane.

- Tests: `pmagent/tests/test_guarded_calls_tv.py` with real TVs 01–05 (pure-unit; no network).

- Make targets: `guard.mcp.db.ro` remains opt-in; no CI change in this PR.

## Acceptance Criteria

- `ruff` green, `pytest -q` green.

- TVs 01–05 pass locally in CI.

- Tag lane (STRICT) continues to pass without changes; adapter respects RO only.

## Out-of-Scope

- Tool Bus/RPC wiring, pg_cron, telemetry writes, or any DB writes in PR CI.

## Plan-of-Record (one PR)

- **PR: impl/guarded-calls-p0-execution**

  - Add `impl.py` for Guard + Gatekeeper + Adapter.

  - Add unit tests for TVs 01–05.

  - Update runbook excerpt in `docs/runbooks/MCP_KNOWLEDGE_DB.md` (usage notes).

  - Evidence bundle: ruff tail, pytest summary, guard JSONs, TV logs (short).

