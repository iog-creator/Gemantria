# Console Kernel Panel Spec (Phase 26.5)

## Purpose

Provide the Orchestrator with a single, trustworthy view of:

* current_phase
* branch
* mode (NORMAL vs DEGRADED)
* failing guards
* recommended behavior

## Data Source

Primary data source:

* `pmagent handoff status-handoff --json`

Fields consumed:

* `ok`
* `kernel.current_phase`
* `kernel.branch`
* `mode` (if present) or derived from `health`
* `health.reality_green`
* `health.failed_checks`
* `recommended_behavior.pm`
* `recommended_behavior.oa`
* `recommended_behavior.ops`

## Behavior

* Panel auto-refreshes on a fixed interval (e.g., 30–60s) or on user action.
* If `ok=false` or JSON is invalid:
  * Show a prominent error banner.
* If mode is DEGRADED:
  * Render a red/warning state.
  * Show a clear message: "Normal work blocked; remediation only."
* If mode is NORMAL:
  * Render a green/normal state.
  * Show summary of phase + branch.

## Layout (Conceptual)

* Header:
  * "Kernel Status"
  * Phase + Branch
* Body:
  * Mode badge (NORMAL/DEGRADED)
  * List of failing checks (if any)
  * Compact block of recommended behaviors for:
    * PM
    * OA
    * OPS

Implementation details must comply with:

* docs/SSOT/webui-contract.md
* docs/SSOT/ORCHESTRATOR_REALITY.md
