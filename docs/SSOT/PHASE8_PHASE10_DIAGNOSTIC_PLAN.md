# Phase 8 & 10 — Discovery & Diagnosis Plan (Pre-Mapping)

## Mandate

- Proceed with **Phase A (Discovery & Diagnosis)** for Phase 8 (temporal) and Phase 10 (correlation) analytics.
- Do **NOT** create final mapping docs until:
  - Phase 8 and Phase 10 produce non-empty outputs at least once.
  - Their JSON shapes are confirmed against `scripts/compass/scorer.py`.

## Tasks

1. Locate Phase 8/10 analytics scripts:
   - `find scripts -name "*correlation*" -o -name "*temporal*"`
   - `rg "correlation" scripts --files-with-matches -g "*.py"`
   - `rg "temporal" scripts --files-with-matches -g "*.py"`

2. Identify current outputs:
   - Confirm that `exports/graph_correlations.json` and `exports/temporal_patterns.json` exist but contain empty arrays (`[]`).
   - Verify their schemas against COMPASS expectations.

3. Determine root cause:
   - What inputs do Phase 8/10 expect (DB tables, graph exports, etc.)?
   - Were the prerequisite steps run?
   - Are thresholds or filters too strict (filtering everything out)?
   - Is logic broken (e.g., early returns, unhandled branches)?

4. Document findings in:
   - `docs/SSOT/PHASE8_PHASE10_DIAGNOSTIC.md`:
     - Current state (empty outputs).
     - Root cause (missing inputs vs broken logic vs thresholds).
     - Minimal fix required to produce non-empty data.

## Constraints

- Mapping docs:
  - `PHASE10_TO_ENVELOPE_MAPPING.md`
  - `PHASE8_TO_ENVELOPE_MAPPING.md`
- MUST NOT be finalized until Phase 8/10 produce real data.
