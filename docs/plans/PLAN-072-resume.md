# PLAN-072 — Resume Docs Management System & Extraction Agents

**Context.** Guarded Tool Calls P0 execution (PLAN-080) is complete and v0.0.3 is finalized. This plan resumes work on the **Docs Management System & Extraction Agents** roadmap with focused milestones.

## Objectives

- **Milestone 1:** DMS guard fixes — ensure documentation management guards are hermetic and pass in CI.
- **Milestone 2:** Extraction agents correctness — verify extraction agents produce valid, schema-compliant outputs.
- **Milestone 3:** Visualization hooks — wire extraction outputs to visualization components.

## Deliverables

### Milestone 1: DMS Guard Fixes

- **Guard Validation:**
  - Review and fix any failing DMS-related guards in CI.
  - Ensure guards are hermetic (no network/DB dependencies in PR CI).
  - Update guard documentation if needed.

- **Acceptance:**
  - All DMS guards pass in PR CI.
  - Guards emit clear error messages when validation fails.
  - No external dependencies in guard execution.

### Milestone 2: Extraction Agents Correctness

- **Schema Validation:**
  - Verify extraction agents output conform to declared schemas.
  - Add schema validation tests for extraction outputs.
  - Fix any schema mismatches or missing fields.

- **Data Quality:**
  - Ensure extraction outputs are deterministic and reproducible.
  - Validate required fields are present and correctly typed.
  - Add unit tests for extraction agent outputs.

- **Acceptance:**
  - All extraction outputs validate against schemas.
  - Unit tests pass for extraction agent outputs.
  - No schema violations in CI.

### Milestone 3: Visualization Hooks

- **Integration:**
  - Wire extraction outputs to visualization components.
  - Ensure data flows correctly from extraction → visualization.
  - Add visual verification (browser tools) for rendered outputs.

- **Acceptance:**
  - Visualization components display extraction data correctly.
  - Browser verification screenshots confirm correct rendering.
  - No data loss or transformation errors in visualization pipeline.

## Acceptance Criteria

- **Overall:**
  - `ruff` green, `pytest -q` green.
  - All guards pass in PR CI (hermetic).
  - Extraction outputs are schema-compliant.
  - Visualization components render correctly (browser-verified).

- **Per Milestone:**
  - Milestone 1: DMS guards pass; documentation updated.
  - Milestone 2: Extraction outputs validate; unit tests pass.
  - Milestone 3: Visualization hooks work; browser verification screenshots present.

## Out-of-Scope

- New extraction algorithms or major refactoring.
- Backend infrastructure changes beyond guard fixes.
- New visualization frameworks or libraries.

## Plan-of-Record (three PRs, sequential)

- **PR-1: fix/dms-guards**
  - Fix DMS guard issues.
  - Ensure hermetic execution.
  - Update guard documentation.

- **PR-2: fix/extraction-agents-correctness**
  - Fix schema validation issues.
  - Add extraction output tests.
  - Verify deterministic outputs.

- **PR-3: feat/visualization-hooks**
  - Wire extraction → visualization.
  - Add browser verification.
  - Update visualization documentation.

## Evidence Bundle (per PR)

- ruff tail, pytest summary, guard JSONs, schema validation results, browser verification screenshots (PR-3).

