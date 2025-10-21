# ADR-000: Orchestration via LangGraph (StateGraph)
Decision: Use LangGraph-style nodes for resumable batches. Phase 0 uses minimal Hello runner; checkpointer infrastructure implemented (Postgres placeholder + Memory fallback via CHECKPOINTER env var).

## Status Update (PR-004)
- Implemented full LangGraph-compatible Postgres checkpointer with BaseCheckpointSaver interface.
- JSONB storage for checkpoint data and metadata with checkpoint versioning.
- Transactional upsert semantics with ON CONFLICT handling.
- CHECKPOINTER=postgres now fully functional when GEMATRIA_DSN is set; memory remains default for CI/dev.
