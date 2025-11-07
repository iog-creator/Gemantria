# ADR-033: AI Nouns SSOT Contract (v1)

## Status

Accepted

## Decision

Adopt `gemantria/ai-nouns.v1` as the single contract for AI-discovered nouns and enrichment inputs/exports.

All discovery/enrichment must write/read this schema; DB tables mirror the same fields.

## Consequences

- Deterministic export/guard; downstream UI/analytics read one envelope.
- `ai_noun_alignment` lets us map back to bible_db when/if desired without blocking AI flow.

## Verification

CI job `ai-nouns-ssot` exports and validates against the JSON Schema; PRs fail closed on drift.

## Context

The AI noun discovery and enrichment pipeline produces structured data that feeds into multiple downstream consumers (graph building, analytics, UI). Without a standardized contract, different components would develop incompatible expectations, leading to integration issues, data drift, and maintenance complexity. A single source of truth contract ensures all components work with consistent, validated data structures.

## Rationale

- **Consistency**: Single schema ensures all components work with identical data structures
- **Validation**: JSON schema validation prevents data drift and integration issues
- **Maintainability**: Clear contract reduces coupling and simplifies testing
- **Evolution**: Versioned schema supports future enhancements while maintaining compatibility
- **Traceability**: Complete audit trail from AI discovery through enrichment to consumption

## Alternatives Considered

1. **Component-specific Schemas**: Each component defines its own data format
   - Pros: Flexibility for component-specific needs
   - Cons: Integration complexity, data transformation overhead, maintenance burden

2. **Database-driven Schema**: Schema defined by database table structure
   - Pros: Single source of truth in database
   - Cons: Database coupling, migration complexity, less portable

3. **Runtime Type Validation**: Python type hints and runtime validation
   - Pros: Language-native, development-friendly
   - Cons: Less portable, no cross-language validation, runtime-only checking

## Implementation Requirements

- Create `gematria/ai-nouns.v1` JSON schema definition
- Implement schema validation in discovery and enrichment pipelines
- Update database tables to mirror schema structure
- Add CI validation job for schema compliance
- Create migration scripts for schema evolution

## Related ADRs

ADR-032 (bible_db SSOT roadmap)
