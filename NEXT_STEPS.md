<!-- Handoff updated: 2025-11-13T14:36:36.654197 -->
# PLAN-073 M1 — Implementation Notes (E01–E05)

- E01: Ensure Knowledge MCP schema files/tables exist (read-only lane). Provide minimal seed or describe via guard.

- E02: Add RO-DSN guard + redaction proof (echo target + guard JSON).

- E03: Envelope ingest path (file→row), hermetic-friendly (no external deps).

- E04: Minimal query roundtrip over MCP tables (deterministic output).

- E05: Proof snapshot written under share/ (json + txt pointers), linked from Atlas if present.
