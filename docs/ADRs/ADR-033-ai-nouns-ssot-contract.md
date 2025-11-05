# ADR-033: AI Nouns SSOT Contract (v1)

**Status:** Accepted | **Date:** 2025-11-04 | **Related:** ADR-031 (analytics), ADR-032 (bible_db SSOT roadmap)

## Decision

Adopt `gemantria/ai-nouns.v1` as the single contract for AI-discovered nouns and enrichment inputs/exports.

All discovery/enrichment must write/read this schema; DB tables mirror the same fields.

## Consequences

- Deterministic export/guard; downstream UI/analytics read one envelope.
- `ai_noun_alignment` lets us map back to bible_db when/if desired without blocking AI flow.

## Verification

CI job `ai-nouns-ssot` exports and validates against the JSON Schema; PRs fail closed on drift.
