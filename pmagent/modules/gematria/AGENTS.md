# AGENTS.md — pmagent/modules/gematria

## Directory Purpose

Skeleton home for the AgentPM Gematria module: pure numerics and Bible-specific
helpers extracted from the existing Gemantria.v2 pipeline into the AgentPM OS.

This module is intentionally light on dependencies. It should not depend on
web UI code, LM governance, or control-plane internals.

## Status

- **Phase-6G**: Skeleton only — module layout, stubs, and minimal tests.
- Implementation of real numerics will be done in later phases.

## Responsibilities (future)

- Core Gematria systems (e.g., Mispar Hechrachi).
- Hebrew (and optional Greek) normalization and letter mapping.
- Bible reference helpers (OSIS parsing).
- Verification helpers for gematria correctness.
- Noun/extraction adapters to bible_db and AgentPM control-plane.

## Dependencies

- Standard library only in the skeleton phase.
- Future phases may depend on:
  - bible_db / extraction agents
  - AgentPM control-plane adapters

## Tests

- `pmagent/modules/gematria/tests/test_core.py`
- `pmagent/modules/gematria/tests/test_hebrew.py`

## Next Steps

- Port real numerics from the current Gemantria.v2 numerics pipeline.
- Wire ingestion and verification to bible_db and extraction agents.
- Expand tests to cover real numerics and edge cases.

