# Gemantria — Full Documentation

> Comprehensive guide for contributors, maintainers, and CI agents.
> For the quick overview, see the root `README.md`.

> Governance fast-lane: All exports stamp `generated_at` as RFC3339 and set `metadata.source="fallback_fast_lane"`. Run guards in HINT-only mode (`STRICT_RFC3339=0`) on main/PRs and STRICT (`STRICT_RFC3339=1`) on release builds. Always run `make housekeeping` after docs or script changes so the contract stays enforced.

---

## 1. Overview

Gemantria is an evaluation-driven pipeline for semantic networks over Hebrew biblical text. It calibrates edge strengths, tracks quality over time, detects anomalies, and renders badges to surface health at a glance.

**Current phase:** Phase 9 (as of Oct 26, 2025)
- Advanced calibration (Otsu-like 2-threshold on blended edge signals)
- Quality trend pipelines (history + sparkline SVG badge)
- Edge audit + anomaly badge (z-score + IQR)

---

## 2. Architecture

**Layers**
- **Data/Graph**: Edge metrics (cosine similarity, re-rank scores) blended via `EDGE_BLEND_WEIGHT`
- **Eval pipeline**: Make targets orchestrate calibration, trend, audit, and artifact mirroring
- **Share mirror**: `share/` holds generated artifacts and mirrored docs (for external consumption / CI checks)
- **CI gates**: Fast `ops.verify`, rule audits, docs sync, share drift guard

**Key scripts**
- `scripts/eval/calibrate_advanced.py` – compute optimal weak/strong thresholds, emit `share/eval/calibration_adv.json`
- `scripts/eval/quality_trend.py` – maintain `quality_history.jsonl` and render `badges/quality_trend.svg`
- `scripts/eval/edge_audit.py` – compute outliers (z-score > 3σ, IQR * 1.5)
- `scripts/eval/anomaly_badge.py` – color-coded anomaly badge
- `scripts/ci/ensure_db_then_migrate.sh` – CI bootstrap (create DB, enable `vector`, apply migrations)
- `scripts/hint.sh` – uniform `HINT:` emitter for triage-friendly logs

---

## 3. Features (Phase 9)

### 3.1 Advanced Calibration
- **Goal**: Separate edges into weak / strong bands with minimal overlap
- **Method**: Otsu-like 2-threshold optimization across a blended signal:
  `blend = W * cosine + (1 - W) * rerank`
- **Output**: `share/eval/calibration_adv.json` (includes `EDGE_BLEND_WEIGHT`, `EDGE_WEAK_THRESH`, `EDGE_STRONG_THRESH`)
- **Make**: `make -s eval.graph.calibrate.adv`

### 3.2 Quality Trend
- **Goal**: Track and visualize historical quality health
- **Artifacts**:
  - `share/eval/quality_history.jsonl`
  - `share/eval/badges/quality_trend.svg` (sparkline)
- **Make**: `make -s eval.quality.trend`

### 3.3 Edge Audit & Anomaly Badge
- **Goal**: Detect statistical anomalies in edge strengths
- **Artifacts**:
  - `share/eval/edge_audit.json`
  - `share/eval/badges/anomaly.svg` (green:0, yellow:1–5, red:6+)
- **Make**: `make -s eval.edge.audit`, `make -s eval.anomaly.badge`

---

## 4. Getting Started

### 4.1 Quickstart
```bash
make -s ops.verify          # fast path; expect: [ops.verify] OK
make -s eval.package        # run calibration + trend + audit + mirror share/
ls -1 share/eval
```

### 4.2 Dev setup (local)

* Python 3.11+
* Optional Postgres 15+ (CI bootstraps automatically)
* Recommended: `pre-commit install`

### 4.3 Reality Check #1: SSOT Docs → Postgres → LM Studio Q&A

The first end-to-end pipeline ingests SSOT documentation into Postgres and enables Q&A via LM Studio.

**Prerequisites:**
```bash
pip install -e .
```

**Run the pipeline:**
```bash
# 1. Ingest SSOT docs into control.doc_sources and control.doc_sections
python -m agentpm.scripts.ingest_docs

# 2. Ask questions using SSOT documentation
pmagent ask docs "What does Phase-6P deliver?"
```

**What it does:**
- Ingests curated SSOT files (MASTER_PLAN.md, AGENTS.md, graph.schema.json) into `control.doc_sources` and `control.doc_sections`
- Retrieves relevant doc sections based on query text match
- Uses LM Studio (guarded) to answer questions with provenance and budget enforcement
- Tolerates db_off mode (graceful degradation when DB/LM unavailable)

**Module locations:**
- Ingestion: `agentpm/scripts/ingest_docs.py`
- Retrieval: `agentpm/knowledge/retrieval.py`
- Q&A: `agentpm/knowledge/qa_docs.py`
- CLI: `pmagent ask docs` command

---

## 5. Make Targets (Full Catalog)

Essentials:

* `ops.verify` — fast integrity smoke; ends `[ops.verify] OK`
* `targets.check.dupes` — detects duplicate Makefile targets (CI smoke guard)

Eval:

* `eval.graph.calibrate.adv` → `share/eval/calibration_adv.json`
* `eval.quality.trend` → `share/eval/quality_history.jsonl`, `share/eval/badges/quality_trend.svg`
* `eval.edge.audit` → `share/eval/edge_audit.json`
* `eval.anomaly.badge` → `share/eval/badges/anomaly.svg`
* `eval.package` — orchestrates the above + share mirror

Share:

* `share.sync` — mirror docs to `share/` (guarded by `SHARE_MANIFEST.json`)

---

## 6. CI & Governance

**Core rules** (AlwaysApply):

* `050-ops-contract.mdc` — OPS/SSOT LOUD-FAIL + governance posture
* `051-cursor-insight.mdc` — Cursor reply format, evidence-first handoffs
* `052-tool-priority.mdc` — Tool ordering, SSOT usage, guardrails for automation

**Templates (required)**:

* `.github/pull_request_template.md` — every PR cites **Rules / Agents / Docs / SSOT** and includes an **Emitted Hints** section
* `.cursor/templates/NEXT_STEPS.template.md` — runbook with scope, steps, failure policy, emitted hints

**Emitted Hints**:

* Uniform logger: `scripts/hint.sh` → prints `HINT: <message>`
* Examples you’ll see in CI logs:

  * `HINT: verify: database bootstrap OK`
  * `HINT: eval: running advanced calibration`
  * `HINT: eval: writing quality trend badge`
  * `HINT: eval: auditing edges for anomalies`

**Share hygiene**:

* `share/SHARE_MANIFEST.json` must exist
* `make share.sync` keeps `/share` consistent; CI verifies

---

## 7. Contribution Guide

1. Create a branch from `main`.
2. Fill out the PR template (Rules/Agents/Docs/SSOT + Emitted Hints).
3. Keep scope **surgical**; list files in the PR body.
4. Paste **evidence tails** (OK lines / failing tails last ~200 lines).
5. CI must go green. We squash & delete the branch.

---

## 8. License

**Personal Use Only**. Commercial use requires a separate agreement. See `LICENSE`.

---

## 9. SSOT & References

* `docs/SSOT/RULES_INDEX.md`
* `docs/SSOT/MASTER_PLAN.md`
* `docs/SSOT/REFERENCES.md`
* `AGENTS.md`

---

## 10. FAQ (selected)

**Q: Does Postgres require manual setup locally?**
A: No for CI (bootstrapped). Locally, you can run without DB unless testing migrations.

**Q: Why no planner hints?**
A: PostgreSQL doesn’t support optimizer hints natively; we use **diagnostic HINTs** in errors/messages for triage clarity.

**Q: What if CI fails on mypy missing stubs?**
A: We configure mypy to ignore missing imports repo-wide while keeping strong typing in our code; fix 026-local errors, not legacy global ones.
