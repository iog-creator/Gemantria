# RFC 000 — Instrumentation rollout: lightweight span helpers & initial instruments

**Author:** Gemantria PM  
**Date:** 2025-11-11  
**Status:** Draft

## Summary

Introduce small, HINT-mode tracing helpers (`span_llm`, `span_tool`) and example instrumented modules to standardize how we capture LLM and DB/tool spans into `evidence/otel.spans.jsonl`. Then instrument three high-value call sites (enrich_nouns, extract_book, rerank) in separate small PRs after RFC review.

## Motivation

We need structured trace evidence surfaced in Atlas node pages to debug LLM and DB/tool behaviors. Current logs are inconsistent. A small opt-in pattern allows collecting proof-of-concept traces without enabling OTLP or risking secret leaks, aligning with our SSOT and governance rules.

## Proposal

1. Add `scripts/observability/otel_helpers.py` with `span_llm(agent, model, prompt_len)` and `span_tool(name, **attrs)` context managers (writes JSONL to `evidence/otel.spans.jsonl`).

2. Add example modules for review only:

   - `scripts/agents/enrich_nouns.py` (uses `span_llm`)

   - `scripts/agents/extract_book.py` (wraps DB calls with `span_tool`)

   - `scripts/agents/rerank.py` (uses `span_llm`)

3. After this RFC is accepted, instrument real call sites in:

   - `services/enrichment` (enrich_nouns)

   - `services/extractor` (extract_book)

   - `services/rerank` (rerank)

   Each will be a focused PR with minimal changes and tests.

4. Validate by running:

   - `ENABLE_OTEL=1 PIPELINE_RUN_ID=instrument-YYYYMMDD make otel.smoke`

   - `make atlas.traces`

   - Capture screenshots and spans to `evidence/`.

## Scope & Non-Goals

- Scope: helpers + example modules + per-service instrumentation PRs after acceptance.

- Non-Goals: global instrumentation in a single massive PR; enabling remote OTLP by default.

## Backwards compatibility & Safety

- Helpers are HINT-mode; default `ENABLE_OTEL=0` is safe (no writes).

- Spans record metadata (prompt length) not full prompts; redact or mask full text unless explicitly approved.

## Testing & Evidence

- Unit smoke for helpers.

- Proof steps and required artifacts: `evidence/otel.spans.jsonl`, `evidence/atlas_index_post_instrument.png`, node pages with traces.

## Rollout plan

- Phase 0: Merge RFC and helper/examples PR (this PR).

- Phase 1: Instrument 3 highest-value call sites in separate small PRs.

- Phase 2: Run proof, review traces in Atlas; expand gradually.

- Phase 3: Optional OTLP exporter and collector when infra available.

## Security & Privacy

- Do not store secrets or raw prompt text in spans. Default behavior is to store `prompt_len` only. Any change to record content must be separately approved.

## Alternatives considered

- Adopt OpenTelemetry SDK + OTLP collector (heavier infra).

- Continue ad-hoc logging (no structured traces).

## Open questions

- Accept storing masked/truncated prompt snippets in spans? (Y/N)

- Confirm the first service to instrument if change needed from recommended list.

## Links

- AGENTS.md, RULES_INDEX.md

- PR #375 (handoff snapshot)

- PR #376 (instrumentation helpers)
