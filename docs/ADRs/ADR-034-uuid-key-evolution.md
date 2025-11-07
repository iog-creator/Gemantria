# ADR-034: UUID Key Evolution and FK Realignment

## Status

Proposed

## Context

Historical migrations created BIGINT PK/FK pairs; new tables use UUID, causing FK type mismatches.

## Decision

Adopt a staged plan: (1) add UUID side-by-side, backfill, (2) repoint FKs, (3) drop BIGINT later.

## Consequences

Zero-downtime path; consumers can cut over gradually. Makefile keeps whitelist until step (2) is green.
