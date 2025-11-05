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
  - **LM Studio Setup**: Run `lms server start --port 9994 --gpu=1.0` for live inference
  - **Default Models**: `EMBEDDING_MODEL=text-embedding-bge-m3`, `RERANKER_MODEL=qwen-reranker`
  - **Live Gate**: Pipeline fails-closed if `USE_QWEN_EMBEDDINGS=true` but models unavailable
- GitHub: MCP server active for repository operations (issues, PRs, search, Copilot integration).
- CI: MyPy configured with `ignore_missing_imports=True` for external deps; DB ensure script runs before verify steps.

## Workflow (small green PRs)
- Branch `feature/<short>` → **write tests first** → code → `make lint type test.unit test.int coverage.report` → commit → push → PR.
- Coverage ≥98%.
- Commit msg: `feat(area): what [no-mocks, deterministic, ci:green]`
- PR: Goal, Files, Tests, Acceptance.

## Code Quality Standards
- **Formatting**: Ruff format (single source of truth)
- **Linting**: Ruff check with zero tolerance for style issues
- **Type checking**: MyPy with `ignore_missing_imports=True` for external deps
- **Import organization**: All imports at module top (no mid-file imports)
- **Line length**: 120 characters maximum
- **String concatenation**: Use `["cmd", *args]` instead of `["cmd"] + args`

## UI / Frontend Generation (Standard)
**Primary model:** Gemini 2.5 Pro (terminal/CLI, long context)
**Fallback / refinement:** Claude Sonnet 4 (highest-fidelity styling, complex refactors)

### Usage rules
1) Start all UI codegen (React/Next, charts, search UI) with **Gemini 2.5 Pro**.
2) If spec unmet after ≤2 iterations, or multi-file refactor / high-fidelity styling is required → **escalate to Claude Sonnet 4**.
3) Minor tweaks (single-file CSS/prop changes) may use a cheaper model.
4) Log model + prompt + iteration count in the PR body (see template).

### Libraries & structure (defaults)
- React 18+ (Next.js when SSR/SSG needed)
- State: Zustand or React Context (keep light)
- Viz: Recharts, D3 wrapper, React Flow (graphs)
- Styling: Tailwind (or CSS Modules)
- Layout: `src/components/*`, `src/hooks/*`, `src/services/*`, `src/views/*`

### QA gates (always)
- Frontend: `npm run lint && npm run test` (if present)
- Backend: `ruff format --check . && ruff check .`
- Security: run static checks where configured
- PR must include "Model Usage" block (see template).

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
- **File Verification (Rule-046)**: All file operations verify existence first (`test -f`, `os.path.exists`, `head`). Missing critical files emit LOUD FAIL (no auto-creation, fail-closed). Critical files include SSOT artifacts, schema files, and core pipeline scripts.
- **SSOT JSONSchema validation**: PR-diff scoped validation of JSON files against schemas (non-blocking nightly sweep)
- **Rules audit strictness**: No ALLOW_RULES_GAP toggle; RESERVED stubs (047/048) maintain contiguous numbering
- **Pre-commit ordering**: `share.sync` runs before `repo.audit` to ensure share/ directory is synchronized before validation
- **Ruff version pinning**: CI workflows hard-pin ruff==0.13.0 with version verification to defeat cache drift (enforce-ruff.yml, lint-nightly.yml, soft-checks.yml, ci.yml)
- **Share sync robustness**: Content-only validation (mtime checks removed) ensures sync works across different filesystem timestamps

### Evaluation
* **Phase-8 local eval**: `make eval.smoke` runs a non-CI smoke to validate the eval harness. Do not wire into CI or `make go` until stabilized. Governance gates (037/038, share no-drift, NEXT_STEPS) remain unchanged.
* **Phase-8 manifest eval**: `make eval.report` loads `eval/manifest.yml` and emits `share/eval/report.{json,md}`. Keep this **local-only** until stabilized; no CI wiring and no `make go` edits.
* **Ops verifier (local)**: `make ops.verify` prints deterministic checks confirming Phase-8 eval surfaces exist (Makefile targets, manifest version, docs header, share dir). Local-only; not wired into CI.
* **Pipeline stabilization**: `eval.package` runs to completion with soft integrity gates; `targets.check.dupes` prevents Makefile regressions; `build_release_manifest.py` skips bundles/ for performance.

## Data Extraction Lineage

Phase 11 unified pipeline flow:

1. **graph_latest.json** (Phase 9 output)
   - Nodes with gematria values, Hebrew text, book/chapter/verse refs
   - Edges with cosine similarity, rerank scores, edge_strength blend

2. **temporal_patterns.json** + **pattern_forecast.json** (Phase 8 output)
   - Time-series data for frequency trends
   - Prophet forecasts with confidence intervals

3. **correlation_weights.json** (Phase 10 output)
   - Cross-text pattern analytics
   - Edge classification (strong/weak thresholds)

4. **unified_envelope.json** (Phase 11 output)
   - Single integrated format with all attributes
   - Versioned schema (`unified-v1`)
   - Configurable size extraction (100, 1k, 10k, 100k+ nodes)

**Extraction Script:** `scripts/extract/extract_all.py`
**Makefile Target:** `make ui.extract.all SIZE=10000 OUTDIR=ui/out`
**Validation:** JSON schema enforcement + size/performance gates + COMPASS mathematical correctness (>80% score)

### COMPASS: Comprehensive Pipeline Assessment Scoring System

**Purpose**: Mathematical envelope validation for data integrity and correctness
**Requirements**: >80% correctness threshold for envelope acceptance

**Capabilities**:
- Correlation weight validation (>0.5 significance threshold)
- Edge strength blend verification (0.5*cos + 0.5*rerank calculation)
- Temporal pattern integrity checks (monotonic timestamps, data consistency)
- CLI scoring with detailed issue reporting

**Usage**:
```bash
make test.compass  # Score envelope for mathematical correctness
python scripts/compass/scorer.py share/exports/envelope.json --verbose
```

**Scoring Categories**:
- **correlation_weights**: Edge significance validation (40% weight)
- **edge_strength_blend**: Blend calculation accuracy (40% weight)
- **temporal_patterns**: Time series data integrity (20% weight)

**Output**: PASS/FAIL status with detailed issue breakdown

## Cursor Execution Profile (AlwaysApply)

This repo expects Cursor to **show its work** in a fixed shape so that GPT-5 and human operators can continue from any point.

**Always output in 4 blocks:**

1. **Goal** — what this step is doing (e.g. "rebase PR #70 onto clean main and re-run hermetic bundle")
2. **Commands** — exact shell commands, top to bottom, no prose in between
3. **Evidence to return** — which command outputs we expect to see pasted back
4. **Next gate** — what happens once the evidence is pasted

**Minimum evidence per PR session:**

```bash
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git status -sb
ruff format --check . && ruff check .
make book.smoke
make eval.graph.calibrate.adv
make ci.exports.smoke
```

**GitHub PR policy for automated tools:**

* If `gh pr checks <N> --required` is **all SUCCESS** → non-required automated reviews are **advisory only**.
* Cursor must **say that** in the output:

  > "Required checks are green; automated review is advisory per AGENTS.md and RULE 051."

* Cursor must prefer **standard merge**:

  ```bash
  gh pr merge <N> --squash
  ```

  when checks are green.

**Fumbling prevention:**

* Do **not** re-ask for repo location if `git rev-parse --show-toplevel` already succeeded in this session.
* Do **not** re-run discovery (`gh pr list …`) more than once per handoff unless the previous output showed conflicts.
* Do **not** propose alternative tooling (Black, isort, flake8) — SSOT is `ruff`.
* **File Verification (Rule-046)**: All file operations MUST verify existence first using explicit checks (`test -f`, `os.path.exists`, `head`) before reading/writing. Missing critical files emit LOUD FAIL per Rule-039 (no auto-creation, fail-closed). Treat missing critical files as infra/contract breach.

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

## Integrated Pipeline Architecture

The Gemantria system now features a fully integrated pipeline that coordinates all components from data extraction through analysis and visualization.

### Pipeline Flow

```
Noun Extraction → Enrichment → Network Building → Schema Validation → Analysis → Export
     ↓              ↓              ↓                    ↓             ↓         ↓
collect_nouns → enrichment → network_aggregator → schema_validator → analysis → export_graph
```

### Core Components

#### Main Pipeline (`src/graph/graph.py`)
- **LangGraph orchestration** with 6 integrated nodes
- **Qwen health gate** enforcement (fail-closed)
- **State persistence** via Postgres/memory checkpointer
- **Comprehensive logging** and error handling

#### Pipeline Nodes
1. **collect_nouns**: Extract nouns from Bible database
2. **validate_batch**: Apply size and quality gates
3. **enrichment**: AI-powered theological analysis
4. **confidence_validator**: Quality threshold enforcement
5. **network_aggregator**: Semantic embeddings and relationships
6. **schema_validator**: JSON schema validation (NEW)
7. **analysis_runner**: Graph analysis and export (NEW)

#### Book Processing (`scripts/run_book.py`)
- **Chapter orchestration** with stop-loss and resume
- **Deterministic seeding** for reproducible runs
- **Service validation** before inference
- **Integrated with main pipeline** via orchestrator

#### Unified Orchestrator (`scripts/pipeline_orchestrator.py`)
- **Single entry point** for all pipeline operations
- **Coordinated workflows** (pipeline → analysis → export)
- **JSON output** for automation and monitoring
- **Error aggregation** and status reporting

### Usage Patterns

#### Quick Start
```bash
# Run complete integrated pipeline
make orchestrator.full BOOK=Genesis

# Run main pipeline only
make orchestrator.pipeline BOOK=Genesis

# Run analysis suite
make orchestrator.analysis OPERATION=all
```

#### Book Processing
```bash
# Plan book processing
make book.plan

# Dry run (validate services)
make book.dry

# Execute full book
make book.go

# Stop after N chapters
make book.stop N=5

# Resume from interruption
make book.resume
```

#### Schema Validation
```bash
# Validate all schemas
make schema.validate

# Validate specific exports
python scripts/eval/jsonschema_validate.py exports/graph_latest.json schemas/graph_output.schema.json
```

### Integration Benefits

- **End-to-end automation** from raw data to visualization
- **Consistent error handling** across all components
- **Unified logging** and monitoring
- **Schema enforcement** prevents data corruption
- **Modular architecture** allows component testing
- **Orchestrator abstraction** simplifies complex workflows

### Quality Gates

- **Schema validation** ensures data integrity
- **Integration tests** verify component interactions
- **Makefile targets** provide consistent interfaces
- **Hermetic CI** with conditional validation
- **Comprehensive logging** enables debugging

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
| 039 | # --- |
| 040 | # --- |
| 041 | # --- |
| 042 | # --- |
| 043 | # --- |
| 044 | # --- |
| 045 | # --- |
| 046 | # --- |
| 047 | # --- |
| 048 | # --- |
| 049 | # --- |
| 050 | # --- |
| 051 | # --- |
| 052 | # --- |
| 053 | # --- |
| 054 | # --- |
| 055 | # --- |
| 056 | # --- |
| 057 | # --- |
| 058 | # --- |
| 059 | # --- |
| 060 | # --- |
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

### Codex CLI Integration

- Optional, local-only tool for running terminal agents with fresh context.
- CI-gated: Exits early unless `ALLOW_CODEX=1`.
- No share writes, respects ruff formatting.
- See `docs/runbooks/CODEX_CLI.md` for installation, usage, and examples.
- Quick start: `make codex.task TASK="your instruction"`

### Runbook: PR Gating (required checks only)

**Note:** Ruff formatting applied during rebase conflict resolution in PR #70.

- **Script:** `scripts/pr_gate.sh <pr-number>`

- **Purpose:** Gate PR merges by required checks only (connector-less strategy)

- **Required checks:** `ruff` (formatting + linting), `build` (CI pipeline)

- **Usage:**
  ```bash
  # Check if PR #123 is ready to merge
  ./scripts/pr_gate.sh 123

  # In CI: exits 0 if mergeable, 1 if not ready
  ```

- **Branch protection:** Main branch requires reviews from CODEOWNERS + required checks

### Runbook: Codex CLI (optional, local-only)

- **Docs:** `docs/runbooks/CODEX_CLI.md`

- **Enable locally:** `npm i -g @openai/codex && codex login`

- **Config:** copy `.codex/config.example.toml` to `~/.codex/config.toml`

- **Use:** `make codex.task TASK="List last 5 commits; propose 2-line release note."`

- **Gating:** **Off in CI** by default; to allow in CI, set `ALLOW_CODEX=1` (not recommended).

---

# 🧭 Gemantria — OPS Contract v6.2.3

**Mode:** OPS MODE only (no small talk, no speculation without evidence)
**Scope:** Gemantria repository and its subprojects (pipeline, exports, viz)
**Authority chain:** Rules 039 → 041 → 046 → 050 → 051 → **052 (Tool Priority & Context Guidance)**

## 1 · Activation Rule

I operate *only if all three* are true:

1. **Repo present** → `git rev-parse --show-toplevel` succeeds.
2. **Governance docs present** → `AGENTS.md` and `RULES_INDEX.md` exist.
3. **Quality SSOT available** → `ruff format --check . && ruff check .` runs.

If any is missing → **FAIL-CLOSED (LOUD FAIL)**.

## 2 · LOUD FAIL Pattern

Emit **exactly** if a required tool/context is missing:

```
LOUD FAIL
governance: Gemantria OPS v6.2
tool: <name>              # e.g., codex, gemini, gh, local-make
action: <what you tried>
args: <key args>
error: <short reason>
fallback:

* git pull --ff-only
* make share.sync
* ruff format --check . && ruff check .
```

## 3 · Tool Priority & File References

Cursor **must** declare the tool and files used.

### Tool Order

1. **Local + GH tools** (`git`, `make`, `gh pr …`)
2. **Codex** — edits/patches/re-writes
   *If unavailable → print `Codex disabled (401)` and fallback*
3. **Gemini / MCP** — long-context reasoning or large docs

### Files Referenced

* `AGENTS.md`
* `RULES_INDEX.md`
* `.cursor/rules/050-ops-contract.mdc`
* `.cursor/rules/051-cursor-insight.mdc`
* `src/**/AGENTS.md` (scoped to relevant module)

### Example Cursor Header

```
governance: Gemantria OPS v6.2.3
tool-priority:
  1. local+gh
  2. codex (if available)
  3. gemini/mcp (for long files)
   files-referenced:
* AGENTS.md
* RULES_INDEX.md
* .cursor/rules/050-ops-contract.mdc
* .cursor/rules/051-cursor-insight.mdc
* .cursor/rules/053-idempotence.mdc
  output-shape: 4 blocks (Goal, Commands, Evidence, Next gate)
  ssot: ruff format --check . && ruff check .
```

## 4 · Context-Thinning Rule

If overflow, **reduce** to:

1. `AGENTS.md`
2. `RULES_INDEX.md`
3. `.cursor/rules/050-ops-contract.mdc`
4. `.cursor/rules/051-cursor-insight.mdc`
5. The single relevant submodule `AGENTS.md`

Do **not** reload the entire repo once this subset is set.

## 5 · Evidence-First Protocol

Before proposing changes:

```bash
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git status -sb
ruff format --check . && ruff check .
make book.smoke
make eval.graph.calibrate.adv
make ci.exports.smoke
```

For PR work:

```bash
gh pr view <N> --json number,title,headRefName,baseRefName,state,author,reviews,reviewDecision,mergeable,mergeStateStatus,checks
gh pr checks <N> --required --json name,state
```

## 6 · Output Shape (4-Block Standard)

1. **Goal** — one sentence defining the action.
2. **Commands** — runnable shell/gh/make lines only.
3. **Evidence to return** — numbered list of expected outputs.
4. **Next gate** — what to do after I see the evidence.

   Each command block begins with:

```
# source: AGENTS.md + RULES_INDEX.md + .cursor/rules/050 + .cursor/rules/051
```

## 7 · SSOT for Quality

```bash
ruff format --check . && ruff check .
```

If ruff fails → stop and request the last 60–200 lines.

## 8 · Hermetic Test Bundle

```bash
make book.smoke
make eval.graph.calibrate.adv
make ci.exports.smoke
```

If DB/services down → "correct hermetic behavior."

## 9 · Non-Required Automated Reviews

If required checks are green:

> "Required checks are green; non-required automated reviews are **advisory only** per AGENTS.md and Rule 051."

## 10 · CI Naming-Conflict Clause

If duplicate `build` jobs (one pass / one fail):

> "Treat as infra fault. With ruff + smokes green, **admin merge allowed** per Governance v6.2 §10."

## 11 · Handoff / New Chat Rule

On "prepare handoff" or "new chat", output **only** the 4 blocks and include baseline evidence (§5).

## 12 · Dirty-Branch Rule

If `git status -sb` shows dirty on `main`, open hygiene PR first:

```bash
git switch -c ci/hygiene-ruff-$(date +%Y%m%d-%H%M)
ruff format --check . && ruff check .
make ops.verify
make share.sync
git add .
git commit -m "ci: apply ruff/py.fullwave hygiene"
git push -u origin HEAD
gh pr create --title "ci: hygiene (ruff)" --body "Automated hygiene per OPS v6.2"
```

## 13 · Required-Checks Gate

Always emit:

```bash
gh pr checks <N> --required --json name,state \
  --jq 'if length==0 then "NO_REQUIRED_CHECKS" else all(.state=="SUCCESS") end'
```

If `NO_REQUIRED_CHECKS`, say: *"Automated checks present → advisory only (051)."*

## 14 · Fail-Closed on Share

If CI writes to `share/`:

1. Identify script. 2) Explain why it breaks hermetic CI.
2. `make share.sync`. 4) Re-run CI.

## 15 · No Async Promises

Never say "I'll check later" or give time estimates.

Always output commands runnable **now**.

## 16 · Header Banner for OPS Responses

Every OPS reply begins:

> **Governance: Gemantria OPS v6.2.3 (tool-aware, 050 + 051 + 052 active)**

> Then the 4-block format follows.

## 17 · Rule-053 — Idempotent Baseline

Cache baseline evidence by `(branch, HEAD)` for **60 minutes**.

If unchanged, **do not** re-ask for baseline; acknowledge cached evidence.

Emit `HINT[baseline.sha]: <sha>` when using cache.

## 18 · CI Single-Context Requirement

PRs expose **one** required status context: **`build-pr`**.

Use concurrency with `cancel-in-progress: true`.

Duplicate/legacy contexts = **infra fault** (see §10).

## 19 · Internal Guardrails (Branch Protection OFF allowed)

Merges are permitted only when **all** are true:

* **policy-gate** passed (Conventional Commits + signed-commit verification).
* **build-pr** passed.
* ≥ **1 human approval** present.
* Prefer **bot-mediated merge** (queue/automation) over manual "Merge".

## 20 · Security & Supply Chain

* Pin third-party actions to **full commit SHAs** (avoid `@v*` tags).
* Enable **Dependabot** for `github-actions` (weekly).
* Nightly **OpenSSF Scorecard** with SARIF upload to Security tab.

### Summary

* **SSOT:** Ruff
* **Hermetic:** book + eval + exports smokes
* **Reviews:** non-required = advisory
* **Tool Priority:** local+gh → codex → gemini/mcp
* **Files:** AGENTS.md, RULES_INDEX.md, 050, 051 (+ Rule-053)
* **Output:** 4 blocks
* **Failure:** LOUD FAIL v6.2
* **Chain:** 039→041→046→050→051→052→**053**

## Cursor-Specific Guidelines

- Respond in plain English; no structured OPS formats or Governance headers.
- Use tool calls for verification (e.g., read_file for existence checks).
- Paste file contents/head/tail when requested for state confirmation.
- Do not assume—verify first, fail-closed on missing critical files.
- For edits, provide patches/diffs only; no auto-apply without user confirmation.
