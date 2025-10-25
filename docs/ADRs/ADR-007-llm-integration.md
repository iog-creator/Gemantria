# ADR-007: LLM Integration and Confidence Metadata

## Status

Accepted

## Decision

Integrate LM Studio locally for theological enrichment and gematria confidence scoring.

## Rationale

- Keeps all inference offline and reproducible
- Adds structured confidence metadata to each noun
- Enforces deterministic behavior through fixed prompts, models, and thresholds

## Implementation

- `lmstudio_client.py`: Handles LM Studio REST API and mock mode
- `enrichment_node.py`: Performs inference and inserts results into `ai_enrichment_log`
- Confidence stored (0 – 1) with models recorded for provenance

## Consequences

- Requires LM Studio running locally
- Adds minor runtime cost per noun
- Enables deeper semantic enrichment for downstream analysis
