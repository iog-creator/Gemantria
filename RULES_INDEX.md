# RULES_INDEX
<!-- alwaysapply.sentinel: 050,051,052 source=ai_interactions -->

> Governance fast-lane: All exports stamp `generated_at` as RFC3339 and set `metadata.source="fallback_fast_lane"`. Run guards in HINT-only mode (`STRICT_RFC3339=0`) on main/PRs and STRICT (`STRICT_RFC3339=1`) on release builds. Always run `make housekeeping` after docs or script changes so the contract stays enforced.

## Tooling Policy

- Use **python3** (runner is exported as `$(PYTHON)=python3` in Makefiles).  
- Never invoke bare `python ` in shell scripts or Makefiles — use `$(PYTHON)` or `python3`.  
- This policy is covered by the **python runner guard** and is part of the Always-Apply posture (050/051/052).

## DSN Policy

- All DSN access must go through the centralized loader in `scripts/config/env.py`.
- Never call `os.getenv("GEMATRIA_DSN")`, `os.getenv("BIBLE_DB_DSN")`, etc. directly in `src/` or `scripts/`.
- Use the canonical import pattern:
  ```python
  from scripts.config.env import get_rw_dsn, get_bible_db_dsn
  
  rw_dsn = get_rw_dsn()
  ro_dsn = get_bible_db_dsn()
  ```
- DSN precedence:
  - **RW DSN**: `GEMATRIA_DSN` → `RW_DSN` → `AI_AUTOMATION_DSN` → `ATLAS_DSN_RW` → `ATLAS_DSN`
  - **RO DSN**: `ATLAS_DSN` → (fallback to RW)
  - **Bible DB DSN**: `BIBLE_RO_DSN` → `RO_DSN` → `ATLAS_DSN_RO` → `ATLAS_DSN`
- This policy is enforced by the **DSN centralization guard** (`guard.dsn.centralized`).

### Centralization guard (policy)

- Guard: `guard.dsn.centralized` (HINT by default) and `guard.dsn.centralized.strict` (fails on violations).
- Temporary allowlist for legacy scripts: `scripts/guards/.dsn_direct.allowlist` (glob per line). Offenders must be removed from this list as they're migrated.
- Tests set `DISABLE_DOTENV=1` to prevent `.env` from influencing DSN precedence.

### Atlas DSN proof

- Make target: `atlas.proof.dsn` — writes `docs/evidence/atlas_proof_dsn.json` (masked) and `docs/evidence/atlas_proof_dsn.html` with a backlink to `../atlas/index.html`.
  - **HINT** by default; set `STRICT_ATLAS_DSN=1` (in tag lane) to require a real RW DSN.

| # | File | Title |
|---:|------|-------|
| 000 | 000-ssot-index.mdc | Non-negotiable rules for Gemantria |
| 000 | 000-ssot-index.mdc.tmp | # (Default-Apply) |
| 001 | 001-db-safety.mdc | DB safety and SQL discipline |
| 002 | 002-gematria-validation.mdc | Hebrew normalization and gematria validation |
| 003 | 003-graph-and-batch.mdc | Graph batch semantics and validation gates |
| 004 | 004-pr-workflow.mdc | Standard PR workflow for this repo |
| 005 | 005-github-operations.mdc | GitHub PR/Issue operations safety (agent-requested) |
| 006 | 006-agents-md-governance.mdc | Governance for AGENTS.md (always-on) |
| 007 | 007-infrastructure.mdc | Infrastructure and checkpointer safety |
| 008 | 008-cursor-rule-authoring.mdc | How to author Cursor rules (.mdc) correctly (agent-requested) |
| 009 | 009-documentation-sync.mdc | Documentation synchronization requirements |
| 010 | 010-task-brief.mdc | SHORT BRIEF format for all interactions |
| 010 | 010-task-brief.mdc.tmp | # (Default-Apply) |
| 011 | 011-production-safety.mdc | Deprecated alias of Rule 000 |
| 012 | 012-connectivity-troubleshooting.mdc | Connectivity troubleshooting and external service handling |
| 013 | 013-report-generation-verification.mdc | Report generation verification and template validation |
| 014 | 014-governance-index.mdc | Rule index continuity (reserved/spec-only) |
| 015 | 015-semantic-export-compliance.mdc | Ensure semantic export scripts produce both JSON-LD and RDF/Turtle formats |
| 016 | 016-visualization-contract-sync.mdc | Deprecated alias of Rule 022 |
| 017 | 017-agent-docs-presence.mdc | Enforce AGENTS.md presence in required source directories |
| 018 | 018-ssot-linkage.mdc | Ensure all SSOT docs are linked from ADRs and vice versa |
| 019 | 019-metrics-contract-sync.mdc | Ensure ADR-016 metrics contract is maintained across exports |
| 020 | 020-ontology-forward-compat.mdc | Ensure JSON-LD ontology extensions are add-only for forward compatibility |
| 021 | 021-stats-proof.mdc | Enforce PR-016/017 metrics proof and UI contract (Always-Verify Template exemplar) |
| 022 | 022-visualization-contract-sync.mdc | Enforce backend→frontend stats/graph contracts for WebUI |
| 023 | 023-visualization-api-spec.mdc | Visualization API spec linkage (ADR-023) |
| 024 | 024-dashboard-ui-spec.mdc | Dashboard UI spec linkage (ADR-023) |
| 025 | 025-phase-gate.mdc | Enforce ADR-025 multi-temporal analytics with rolling windows, forecasting, and interactive exploration |
| 026 | 026-system-enforcement-bridge.mdc | Bridge Cursor rules to system enforcement (pre-commit + CI + branch protection) |
| 027 | 027-docs-sync-gate.mdc | Require docs/ADR/SSOT updates for any code change |
| 028 | 028-phase-freshness.mdc | Forest must be regenerated within 24h before PR |
| 029 | 029-adr-coverage.mdc | Any new rules/migrations require ADR delta |
| 030 | 030-share-sync.mdc | Always sync share directory after changes |
| 030 | 030-share-sync.mdc.tmp | # (Default-Apply) |
| 031 | 031-correlation-visualization-validation.mdc | Validate correlation visualization exports and reporting |
| 032 | 032-pattern-integrity-validation.mdc | Validate cross-text pattern analytics exports and schema |
| 033 | 033-visualization-api-validation.mdc | Validate visualization API + dashboard presence |
| 034 | 034-temporal-suite.mdc | Phase 8 — Temporal Analytics Suite (spec + forecasts + visualization) consolidated into a single active rule. |
| 035 | 035-forecasting-spec.mdc | DEPRECATED — Forecasting spec consolidated into Rule 034 (Temporal Analytics Suite). |
| 036 | 036-temporal-visualization-spec.mdc | DEPRECATED — Temporal visualization spec consolidated into Rule 034 (Temporal Analytics Suite). |
| 037 | 037-data-persistence-completeness.mdc | Enforce complete data persistence and schema fulfillment for core pipeline artifacts. |
| 038 | 038-exports-smoke-gate.mdc | Fail-fast guard for export readiness; prevents running exports when upstream data is empty or malformed. |
| 039 | 039-execution-contract.mdc | Execution Contract Enforcement |
| 040 | 040-ci-triage-playbook.mdc | CI Triage Playbook |
| 041 | 041-pr-merge-policy.mdc | PR Merge Policy |
| 042 | 042-formatter-single-source-of-truth.mdc | Formatter Single Source of Truth |
| 043 | 043-ci-db-bootstrap.mdc | CI DB Bootstrap & Empty-Data Handling |
| 044 | 044-share-manifest-contract.mdc | Share Manifest Contract |
| 045 | 045-rerank-blend-SSOT.mdc | Rerank Blend is SSOT |
| 046 | 046-ci-hermetic-fallbacks.mdc | Hermetic CI Fallbacks |
| 047 | 047-reserved.mdc | RESERVED |
| 048 | 048-reserved.mdc | RESERVED |
| 049 | 049-gpt5-contract-v5.2.mdc | GPT-5 Contract v5.2 |
| 050 | 050-ops-contract.mdc | OPS Contract v6.2.3 (AlwaysApply) |
| 051 | 051-cursor-insight.mdc | Cursor Insight & Handoff (AlwaysApply) |
| 052 | 052-tool-priority.mdc | Tool Priority & Context Guidance (AlwaysApply) |
| 053 | 053-idempotence.mdc | Idempotent Baseline |
| 062 | (inline) | Rerank thresholds: HINT on main, STRICT on tags; SSOT in `configs/rerank_blend.json`; guard `guard.rerank.thresholds` |
| 054 | 054-reuse-first.mdc | Reuse-First, No-Scaffold-When-Exists |
| 055 | 055-auto-docs-sync.mdc | Auto-Docs Sync Pass |
| 056 | 056-ui-generation.mdc | UI Generation Standard |
| 057 | 057-embedding-consistency.mdc | Embedding Consistency CI Checks |
| 058 | 058-auto-housekeeping.mdc | Mandatory run `make housekeeping` after every change/PR. Fail-closed if skipped—critical error log/CI fail. Includes share.sync, governance, ADRs, rules audit, forest regen, and evidence archiving. |
| 059 | 059-context-persistence.mdc | Context Persistence |
| 060 | 060-response-style.mdc | Response Style Enforcement |
| 061 | 061-ai-learning-tracking.mdc | AI learning and interaction tracking system |
| 062 | 062-environment-validation.mdc | Environment validation and venv management (always-on) |
| 063 | 063-git-safety.mdc | Git safety - no destructive operations (always-on) |
| 064 | 064-ai-tracking-contract.mdc | AI tracking contract |
| 065 | 065-gpt-docs-sync.mdc | GPT Documentation Sync (AlwaysApply) |
| 066 | 066-lm-studio-appimage-update.mdc | LM Studio AppImage update and dock integration procedure |

---
