# ADR-000: Orchestration via LangGraph (StateGraph)
Decision: Use LangGraph-style nodes for resumable batches. Phase 0 uses minimal Hello runner; checkpointer infrastructure implemented (Postgres placeholder + Memory fallback via CHECKPOINTER env var).
