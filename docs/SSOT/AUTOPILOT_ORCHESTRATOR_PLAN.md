# Autopilot → pmagent Orchestrator Plan (v0)

## 1. Purpose

This document defines how the Orchestrator Shell's **Autopilot** input will
eventually talk to backend agents via `pmagent` under **Guarded Tool Calls**,
while preserving hermetic behavior and governance rules.

Version v0 is **planning only**:
- No runtime wiring is required.
- Autopilot UI remains **local-only** (client state only).
- This SSOT exists to guide a future phase.

---

## 2. Current State (v1)

- Autopilot is a text box on the Orchestrator Overview panel.
- Intents are stored in React local state (and optionally localStorage).
- No HTTP requests, DB queries, or pmagent calls are made.
- The Shell is fully hermetic and passes:
  - `make book.smoke`
  - `make eval.graph.calibrate.adv`
  - `make ci.exports.smoke`

This behavior MUST remain true until a future phase explicitly implements the
wiring described below.

---

## 3. Target Architecture (High Level)

### 3.1 Roles

- **Orchestrator Shell** (frontend)
  - Captures free-form intents from the operator.
  - Displays recent signals (DB/LM/System) and Autopilot history.

- **pmagent** (CLI / agent runner)
  - Provides structured commands for inspections, exports, and health checks.
  - Already integrated with guards and SSOT.

- **Guarded Tool Calls Layer**
  - Enforces which pmagent commands the Shell may request.
  - Ensures:
    - No uncontrolled shell access.
    - All calls are logged with receipts.
    - DSNs and secrets stay server-side.

### 3.2 Flow (Future)

1. Operator types an intent in Autopilot.
2. Shell sends the intent to a backend endpoint (TBD; not implemented in v1).
3. Backend:
   - Interprets the intent.
   - Maps it to one or more **allowed pmagent commands** (whitelisted).
   - Executes these commands via Guarded Tool Calls.
4. Results are written to:
   - Static JSON exports (e.g. new status / evidence files).
   - Optional short summaries returned to the Shell.
5. Shell refreshes from static JSON and shows updated status / summaries.

---

## 4. Guardrails & Allowed Actions

In the first wired version, Autopilot MAY only trigger:

- **Read-only or planning actions**, such as:
  - Health checks (DB/LM/system guards)
  - Export smokes / readiness checks
  - Documentation / SSOT summaries

Autopilot MUST NOT trigger:

- Destructive operations (file moves, deletes, DB migrations).
- Non-hermetic flows that assume live DB/LM for correctness without guards.

A future version of this SSOT will contain a specific allow-list of pmagent
commands and their arguments.

---

## 5. API Contract (Future)

This section reserves the shapes for a future HTTP API, without requiring the
server to exist yet.

### 5.1 Request

```json
{
  "intent_text": "Show me what my models and docs are doing.",
  "context": {
    "shell_version": "v1",
    "caller": "orchestrator-ui"
  }
}
```

### 5.2 Response (success)

```json
{
  "accepted": true,
  "plan_id": "autopilot-plan-1234",
  "summary": "Planned LM status check and docs inventory refresh.",
  "status": "planned"
}
```

### 5.3 Response (rejected)

```json
{
  "accepted": false,
  "reason": "Intent would require non-whitelisted pmagent commands."
}
```

No code should assume this API exists until the corresponding backend module
and guards are implemented.

---

## 6. Implementation Phasing

**Phase A (current)** — UI-only

* Keep Autopilot local-only.
* Improve copy to clarify no backend effect.

**Phase B (next)** — Backend stub + logging

* Implement a backend endpoint that:
  * Accepts intents.
  * Logs them with a generated `plan_id`.
  * ALWAYS responds with `accepted: false` or `status: "planned"` (no actions).
* Wire the Shell to call this endpoint **only in dev** behind a feature flag.

**Phase C** — Guarded pmagent integration

* Implement a Guarded Tool Calls adapter that:
  * Maps certain intents to **explicit pmagent invocations**.
  * Ensures all actions are:
    * Logged with receipts,
    * Limited to approved commands,
    * Reversible or non-destructive where possible.

**Phase D** — Evidence-driven dashboards

* Expose Autopilot plans and results in:
  * Atlas dashboards,
  * Orchestrator Shell panels (summary cards / history).

---

## 7. Testing Requirements

* Hermetic tests MUST still pass without DB/LM.
* Any future wiring must:
  * Skip or HINT in CI when backends are absent.
  * Never break Shell rendering due to backend outages.
* Autopilot backend failures must degrade gracefully:
  * The UI continues to accept intents locally.
  * Errors are surfaced as short, human messages.

---

## 8. Non-Goals (v0)

* No live-chat agent orchestration.
* No direct tool selection from the browser.
* No privileged pmagent commands invoked without Guarded Tool Calls.

This SSOT will be updated when backend wiring is implemented.
