# BibleScholar Reference Answer Slice (Phase-6P)

## Purpose

Single end-to-end BibleScholar interaction using:
- LM Studio (guarded, with budget & provenance)
- `bible_db` (read-only, verse context resolution)
- Gematria adapter (numeric pattern retrieval)
- Optional knowledge slice (DB-backed knowledge retrieval)

This slice demonstrates the complete flow from natural-language question → verse context → gematria patterns → LM synthesis → traceable answer.

## Inputs

- **Question**: Natural-language question (e.g., "What does Genesis 1:1 mean?")
- **Optional verse reference**: OSIS reference (e.g., "Gen.1.1") or book/chapter/verse string
- **Optional context**: Additional context hints (e.g., "focus on gematria patterns")

## Flow

1. **Verse Context Resolution** (via `bible_db_adapter`)
   - Parse verse reference if provided
   - Retrieve verse text from `bible_db` (read-only)
   - Retrieve surrounding context (previous/next verses) if needed
   - Handle DB-off mode gracefully (return empty context, set `db_status`)

2. **Gematria Pattern Retrieval** (via `gematria_adapter`)
   - If verse text contains Hebrew, compute gematria values
   - Retrieve related gematria patterns from Gematria module (if available)
   - Optional: Cross-reference with other verses sharing numeric patterns

3. **Knowledge Slice Retrieval** (optional, via `knowledge_adapter`)
   - Query DB-backed knowledge slice for relevant documents
   - Semantic search over `kb_document` and `kb_embedding` tables
   - Return top-k relevant knowledge snippets

4. **LM Studio Guarded Call** (via `guarded_lm_call`)
   - Assemble context: verse text + gematria patterns + knowledge snippets
   - Call LM Studio with:
     - Budget enforcement (per-app budget checks)
     - Provenance tracking (call_site, token usage, latency)
     - Control-plane logging (success/failure, error types)
   - Synthesize answer with justification
   - Handle budget exhaustion gracefully (return "budget_exceeded" mode)

5. **Output Assembly**
   - Combine LM answer with trace information
   - Include context_used (verse refs, gematria values, knowledge sources)
   - Include provenance (call_site, tokens, latency, budget_status)

## Outputs

```json
{
  "answer": "string — synthesized answer with justification",
  "trace": [
    {
      "step": "verse_context",
      "result": {...},
      "db_status": "ok|off"
    },
    {
      "step": "gematria_patterns",
      "result": {...},
      "patterns_found": true|false
    },
    {
      "step": "knowledge_slice",
      "result": {...},
      "snippets_count": 0|N
    },
    {
      "step": "lm_synthesis",
      "result": {...},
      "provenance": {
        "call_site": "biblescholar.reference_slice",
        "tokens_used": N,
        "latency_ms": N,
        "budget_status": "ok|exceeded"
      }
    }
  ],
  "context_used": {
    "verse_refs": ["Gen.1.1"],
    "gematria_values": [913, 203, 86],
    "knowledge_sources": ["kb_doc_123", "kb_doc_456"]
  }
}
```

## Constraints

- **No new DSNs**: Must use existing `BIBLE_DB_DSN` (read-only) and `GEMATRIA_DSN` (read-only for Gematria adapter)
- **DB-off hermetic mode**: Must pass when DB is unavailable (graceful degradation, return empty results, set `db_status`)
- **Budget enforcement**: Must respect per-app LM budgets (fail-closed on budget exhaustion)
- **Provenance required**: All LM calls must be logged to control-plane with call_site, tokens, latency
- **Read-only adapters**: Must use existing read-only adapters (`bible_db_adapter`, `gematria_adapter`, `vector_adapter`)
- **No control-plane mutations**: This slice does not write to control-plane (only reads for budget checks and logs LM calls)

## Dependencies

- **Phase-6J**: BibleScholar Gematria adapter (read-only) — COMPLETE
- **Phase-6M**: Bible DB read-only adapter + passage flow — COMPLETE
- **Phase-6O**: Vector similarity adapter + verse-similarity flow — COMPLETE
- **Phase-6A**: LM Studio live usage enablement (guarded calls + logs) — COMPLETE
- **Phase-6B**: LM usage budgets + rate tracking — COMPLETE
- **Phase-6C**: Knowledge Slice v0 (DB-backed) — COMPLETE

## Implementation Notes

- **Entry point**: `pmagent/biblescholar/reference_slice.py` — `answer_reference_question(question: str, verse_ref: str | None = None) -> ReferenceAnswerResult`
- **Flow orchestration**: Use existing adapters in sequence, assemble context, call LM, return structured result
- **Error handling**: Graceful degradation at each step (DB-off, LM-off, budget-exceeded)
- **Testing**: Hermetic tests with mocks for DB/LM, verify trace structure, verify provenance logging

## Next Steps

- **Implementation PR (Phase-6P code)**: Implement `reference_slice.py` with full flow, tests, and integration
- **Integration**: Wire into BibleScholar UI (future PR, not in Phase-6P scope)
- **Documentation**: Update AGENTS.md, BIBLESCHOLAR_MIGRATION_PLAN.md with Phase-6P completion

