# AGENTS.md — Gemantria Agent Framework

## Mission
Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts.

## Priorities
1) Correctness: **Code gematria > bible_db > LLM (LLM = metadata only)**.
2) Determinism: content_hash identity; uuidv7 surrogate; fixed seeds; position_index.
3) Safety: **bible_db is READ-ONLY**; parameterized SQL only; **fail-closed if <50 nouns** (ALLOW_PARTIAL=1 is explicit).

## Environment
- venv: `python -m venv .venv && source .venv/bin/activate`
- install: `make deps`
- Databases:
  - `BIBLE_DB_DSN` — read-only Bible database (RO adapter denies writes pre-connection)
  - `GEMATRIA_DSN` — read/write application database
- Batch & overrides:
  - `BATCH_SIZE=50` (default noun batch size)
  - `ALLOW_PARTIAL=0|1` (if 1, manifest must capture reason)
  - `PARTIAL_REASON=<string>` (required when ALLOW_PARTIAL=1)
- Checkpointer: `CHECKPOINTER=postgres|memory` (default: memory for CI/dev)
- LLM: LM Studio only when enabled; confidence is metadata only.
- GitHub: MCP server active for repository operations (issues, PRs, search, Copilot integration).
- CI: MyPy configured with `ignore_missing_imports=True` for external deps; DB ensure script runs before verify steps.

## Workflow (small green PRs)
- Branch `feature/<short>` → **write tests first** → code → `make lint type test.unit test.int coverage.report` → commit → push → PR.
- Coverage ≥98%.
- Commit msg: `feat(area): what [no-mocks, deterministic, ci:green]`
- PR: Goal, Files, Tests, Acceptance.

### Runbook: Postgres checkpointer
1. Apply migration:
   ```bash
   psql "$GEMATRIA_DSN" -f migrations/002_create_checkpointer.sql
   ```
2. Verify locally:
   ```bash
   export CHECKPOINTER=postgres
   export GEMATRIA_DSN=postgresql://user:pass@localhost:5432/gemantria
   make lint type test.unit test.integration coverage.report
   ```
3. Expected: tests green, coverage ≥98%, checkpoint storage and retrieval works end-to-end.

### Runbook: Database Bootstrap (CI)
1. Bootstrap script ensures database exists before migrations:
   ```bash
   scripts/ci/ensure_db_then_migrate.sh
   ```
2. Handles missing database gracefully with admin connection fallback
3. Applies vector extension and all migrations in order
4. Migration 014 fixed to handle schema evolution from migration 007 (composite primary key preservation, view recreation)
5. Used in CI workflows for reliable database setup

## Operations

### CI Verification
- **Empty DB tolerance**: Verify scripts handle missing tables gracefully in CI (zero counts allowed when DB empty)
- **Stats validation**: Allows zero nodes/edges when DB tables don't exist (prevents CI failures on empty databases)
- **File tolerance**: Handles missing graph/stats files in CI by using empty defaults
- **SSOT JSONSchema validation**: PR-diff scoped validation of JSON files against schemas (non-blocking nightly sweep)
- **Rules audit strictness**: No ALLOW_RULES_GAP toggle; RESERVED stubs (047/048) maintain contiguous numbering

### Evaluation
* **Phase-8 local eval**: `make eval.smoke` runs a non-CI smoke to validate the eval harness. Do not wire into CI or `make go` until stabilized. Governance gates (037/038, share no-drift, NEXT_STEPS) remain unchanged.
* **Phase-8 manifest eval**: `make eval.report` loads `eval/manifest.yml` and emits `share/eval/report.{json,md}`. Keep this **local-only** until stabilized; no CI wiring and no `make go` edits.
* **Ops verifier (local)**: `make ops.verify` prints deterministic checks confirming Phase-8 eval surfaces exist (Makefile targets, manifest version, docs header, share dir). Local-only; not wired into CI.
* **Pipeline stabilization**: `eval.package` runs to completion with soft integrity gates; `targets.check.dupes` prevents Makefile regressions; `build_release_manifest.py` skips bundles/ for performance.

## Rules (summary)
- Normalize Hebrew: **NFKD → strip combining → strip maqaf/sof pasuq/punct → NFC**
- Mispar Hechrachi; finals=regular. Surface-form gematria with calc strings.
- Ketiv primary; variants recorded with `variant_type`; store span_start/end for instances.
- Batches default to 50; abort + `review.ndjson` on failure; `ALLOW_PARTIAL=1` override logs manifest.
- Default edges: shared_prime (cap k=3); optional identical_value/gcd_gt_1 behind flags.
- Layouts persisted with (algorithm, params_json, seed, version). New params → new layout id.
- Checkpointer: `CHECKPOINTER=postgres|memory` (memory default); Postgres requires `GEMATRIA_DSN`.
- GitHub operations: Use MCP server for issues/PRs/search; confirm ownership; search before creating; use Copilot for AI tasks.

### Edge reranking & classification (Phase-10)
All exported edges now carry a `rerank` score and an `edge_strength = 0.5*cos + 0.5*rerank`.
Edges are classified as **strong** (≥0.90), **weak** (≥0.75), or **other**.
Counts are emitted to `share/eval/edges/edge_class_counts.json` for telemetry.

### SSOT Blend Validation (Phase-10)
Hermetic validation enforces `edge_strength = α*cosine + (1-α)*rerank_score` contract (Rule-045).
- **Validator**: `scripts/eval/validate_blend_ssot.py` (non-fatal HINTs only)
- **Field aliases**: Accepts SSOT names first, then legacy (`similarity`→`cosine`, `rerank`→`rerank_score`, `strength`→`edge_strength`)
- **Exporter**: `scripts/export_graph.py` emits SSOT field names with proper blend computation
- **Reclassifier**: `scripts/eval/reclassify_edges.py` prefers SSOT edge_strength for classification
- **Defaults**: `EDGE_ALPHA=0.5`, `BLEND_TOL=0.005`
- **Artifacts**: `share/eval/edges/blend_ssot_report.json` and `.md` (deterministic)
- **Integration**: Wired into `ops.verify` as non-fatal validation step

## How agents should use rules

* Global constraints live in `.cursor/rules/000-always-apply.mdc`.
* See .cursor/rules/049-gpt5-contract-v5.2.mdc (alwaysApply).
* Path-scoped rules auto-attach via `globs`.
* One-off procedures live as agent-requested rules (invoke by referencing their `description` in the prompt).
* Any change to rules affecting workflows must update this AGENTS.md and ADRs in the same PR.


<!-- RULES_INVENTORY_START -->
| # | Title |
|---:|-------|
| 000 | # --- |
| 001 | # --- |
| 002 | # --- |
| 003 | # --- |
| 004 | # --- |
| 005 | # --- |
| 006 | # --- |
| 007 | # --- |
| 008 | # --- |
| 009 | # --- |
| 010 | # --- |
| 011 | # --- |
| 012 | # --- |
| 013 | # --- |
| 014 | # --- |
| 015 | # --- |
| 016 | # --- |
| 017 | # --- |
| 018 | # --- |
| 019 | # --- |
| 020 | # --- |
| 021 | # --- |
| 022 | # --- |
| 023 | # --- |
| 024 | # --- |
| 025 | # --- |
| 026 | # --- |
| 027 | # --- |
| 028 | # --- |
| 029 | # --- |
| 030 | # --- |
| 031 | # --- |
| 032 | # --- |
| 033 | # --- |
| 034 | # --- |
| 035 | # --- |
| 036 | # --- |
| 037 | # --- |
| 038 | # --- |
| 039 | # id: 039_EXECUTION_CONTRACT |
| 040 | # id: 040_CI_TRIAGE_PLAYBOOK |
| 041 | # id: 041_PR_MERGE_POLICY |
| 042 | # 042 — Formatter Single Source of Truth (AlwaysApply) |
| 043 | # 043 — CI DB Bootstrap & Empty-Data Handling (AlwaysApply) |
| 044 | # 044 — Share Manifest Contract (AlwaysApply) |
| 045 | # 045 — Rerank Blend is SSOT (AlwaysApply) |
| 046 | # 046 — Hermetic CI Fallbacks (AlwaysApply) |
| 047 | # --- |
| 048 | # --- |
| 049 | # id: 049_GPT5_CONTRACT_V5_2 |
<!-- RULES_INVENTORY_END -->

---

## Editor Baseline (Cursor 2.0)

**Purpose:** speed up surgical PR work while preserving SSOT governance.

### Settings (per developer)

- **Multi-Agents:** **Enabled**; set parallel agents to **4–8** as hardware allows. Cursor isolates agents via **git worktrees / remote machines** to avoid file conflicts. :contentReference[oaicite:1]{index=1}

- **Models:** **Plan with your top reasoner**; **Build with *Composer*** (Cursor's agentic coding model, ~**4× faster**, most turns **<30s**). :contentReference[oaicite:2]{index=2}

- **Browser for Agent:** Allowed **in-editor** for research/design only (CI remains hermetic). Browser is **GA** in 2.0 and can forward DOM to the agent. :contentReference[oaicite:3]{index=3}

- **Sandboxed Terminals:** Prefer sandboxed agent shells (no network) where supported; keep our CI "no network" invariant regardless. :contentReference[oaicite:4]{index=4}

### Team Rules / Commands

- SSOT remains in-repo (`.cursor/rules/*.mdc`). Optional dashboard **Team Rules/Commands** may drift or fail to sync; if used, generate them **from** the repo and treat dashboard as a mirror only. :contentReference[oaicite:5]{index=5}

### Guardrails we keep

- **No outbound network in CI.** Use hermetic validators and artifacts-first routing.

- **No `share/**` writes in CI.** Route CI outputs to `_artifacts/**`.

- **Ruff-format is the single formatter.** Workflows should run `ruff format --check .` and `ruff check .`.
