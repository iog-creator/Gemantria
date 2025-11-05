# ADR-029: Schema Normalization & Staging Infrastructure

## Status

Accepted

## Date

2025-11-04

## Related PRs

#016 (policy/enforcement), #017 (SSOT analytics)

## Rules

029 (ADR coverage), 037 (Data persistence), 038 (Export smoke gates)

## Context

Recent Genesis pipeline corruption revealed systemic issues with data integrity. Relations had NULL destination IDs, timestamps in relation_type fields, and misaligned column data. Without staging and validation, future column swaps or missing fields could silently corrupt production data.

## Decision

Introduce staging schema layer with strict constraints and fail-closed validation:

- Staging tables (`staging.*_norm`) with NOT NULL and CHECK constraints
- JSON export normalization (`scripts/normalize_exports.py`) to standardize field names
- Runtime insertion guards (`scripts/guard_relations_insert.py`) for pre-commit validation
- Atomic promotion from staging to production with foreign key enforcement

## Consequences

- Fail-closed protection prevents corrupted data from reaching production
- Atomic promotion ensures data consistency during upgrades
- Slight performance overhead from validation steps (acceptable for data quality)
- Forces early detection of schema/data mismatches in development

## Implementation

- `scripts/normalize_exports.py`: Maps variant field names to canonical format
- `scripts/guard_relations_insert.py`: Pre-insertion validation of endpoints
- Makefile targets: `schemas.normalize`, `exports.guard`
- SQL staging scripts with strict constraints and atomic promotion

## Verification

- Genesis data corruption detected and quarantined
- Staging integrity queries return zero bad/orphan rows
- Production promotion succeeds with proper FK relationships
- Future pipelines route through staging validation

## Links

- Related PRs: #016 (policy/enforcement), #017 (SSOT analytics)
- Guards & Staging: `scripts/normalize_exports.py`, `scripts/guard_relations_insert.py`
