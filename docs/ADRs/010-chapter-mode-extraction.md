# ADR-010: Chapter-Mode Execution for OT Extraction

## Status
Accepted (Phase 8). Enforced by runner policy gates. No schema changes.

## Context
We introduced per-chapter execution (plan/dry/stop/resume) to improve safety and resume-ability. This is an **operational change**, not a schema change, but it introduces batch semantics at chapter granularity.

## Decision
- Allow chapter-scoped runs **only** if:
  1) **Rule 003** batch policy is preserved: integration must enforce `noun_count == 50`. Lower thresholds are **not allowed**.
  2) **Rule 011** Qwen Live Gate: LM chat service must be reachable and explicitly asserted before network ops.
  3) No share-manifest expansion; only readiness proofs mirror; op logs stay local.

## Consequences
- The runner enforces:
  - Appending `--noun-min 50` to the chapter command if absent (or passing `NOUN_MIN=50` env, whichever the pipeline accepts).
  - Asserting LM chat (Qwen) port is up; run aborts if not.
- If any policy fails → hard exit with a clear message; no extraction proceeds.

## Rollback
- Disable chapter-mode by invoking book-level pipeline as before. This ADR does not change schemas or artifacts.

## References
- RULES_INDEX.md: Rule 003 (batch size), Rule 011 (Qwen live gate), Rule 034 (temporal).
