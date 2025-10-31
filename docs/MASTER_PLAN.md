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
  - Checkpointer infrastructure: Postgres placeholder + Memory fallback
  - No bible_db writes (policy locked; RO enforced in later PR)

### Documentation Alignment Phase (D-phase)

| Task | Description                             | Status |
| ---- | --------------------------------------- | ------ |
| D1   | Verify ADR <-> Rule <-> SSOT linkages   | ✅     |
| D2   | Ensure AGENTS.md present in all modules | ✅     |
| D3   | Run documentation-sync rule in Cursor   | ✅     |
