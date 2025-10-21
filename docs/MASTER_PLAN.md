# MASTER_PLAN — Phase 0 Bootstrap (Gemantria)

- SSOT: this file + ADRs drive implementation.
- Goals:
  - Deterministic, test-first pipeline foundations
  - Agent guardrails (AGENTS.md + .cursor/rules)
  - Strict CI (≥98% coverage)
- Phase 0 Acceptance:
  - Normalization verified (NFKD→strip→NFC)
  - Mispar Hechrachi: finals=regular
  - Adam=45, Hevel=37 tests green
  - No bible_db writes (policy locked; RO enforced in later PR)
