# Phase-9 — Table Mappings & Field Caps (Plan Only)

Status: plan-only. No DB/network in CI. Local profiles only.

## Entities

- node(id, label, type?, attrs?) → caps: label 120, type 40
- edge(src, dst, rel_type, weight?) → caps: rel_type 40; weight [0..1]
- verse_ref(book, chapter, verse) → normalized "Book 1:1" string

## Normalization

- strip non-canonical identifiers; normalize verse refs
- truncate strings to caps; reject oversized rows (deterministic)

## Envelopes

- metrics envelope (existing) remains the SSOT for quick checks
- future: ingestion envelope (TBD), local-only, schema-documented

## Next

- P9-J: stub mappers (pure functions) + unit tests (no DB); docs-first
