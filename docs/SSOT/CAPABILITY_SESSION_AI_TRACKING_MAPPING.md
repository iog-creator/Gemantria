# Capability Session → AI Tracking Mapping (Design)

**Status:** Design-only; no writes implemented yet  
**Purpose:** Define how `capability_session` envelopes (from `pmagent plan reality-loop`) would map into AI tracking tables  
**Related:** `agentpm/plan/next.py` (reality-loop), `agentpm/control_plane.py` (agent_run_cli), `migrations/051_control_agent_run_cli.sql`

## Overview

This document defines the **future contract** for persisting `capability_session` envelopes (created by `pmagent plan reality-loop`) into AI tracking tables. The mapping is **design-only** at this stage; no database writes are implemented. A hermetic validator (`agentpm/reality/capability_envelope_validator.py`) checks envelopes against this contract without writing to the database.

## Capability Session Envelope Structure

A `capability_session` envelope (from `evidence/pmagent/capability_session-*.json`) has the following structure:

```json
{
  "type": "capability_session",
  "version": "1.0",
  "id": "NEXT_STEPS:1",
  "title": "Task title from NEXT_STEPS",
  "source": "NEXT_STEPS",
  "plan": {
    "current_focus": "Phase description",
    "next_milestone": "Milestone description",
    "raw_line": "- Task line from NEXT_STEPS.md",
    "dry_run_command": "make book.go"  // optional
  },
  "posture": {
    "mode": "live" | "hermetic",
    "reality": {
      "overall_ok": true | false,
      "components": {...}
    },
    "status": {
      "level": "OK" | "WARN" | "ERROR",
      "headline": "Status summary",
      "details": "..."
    }
  },
  "available": true
}
```

## Mapping to `control.agent_run_cli`

**Target Table:** `control.agent_run_cli` (see `migrations/051_control_agent_run_cli.sql`)

**Schema:**
- `id` (uuid) - Generated UUID for the run
- `created_at` (timestamptz) - Timestamp from envelope filename or `now()`
- `updated_at` (timestamptz) - Same as `created_at` initially
- `command` (text) - **Mapped from:** `plan.dry_run_command` if present, else `"plan.reality-loop"` (the command that created the envelope)
- `status` (text) - **Mapped from:** `"started"` (envelope represents planned work, not executed)
- `request_json` (jsonb) - **Mapped from:** Full envelope structure (entire `capability_session` dict)
- `response_json` (jsonb) - `null` (envelope is intent/preview, not execution result)
- `error_text` (text) - `null` (envelope is intent/preview, not execution result)

**Derived Fields:**
- `command`: If `plan.dry_run_command` exists and is non-empty, use that string. Otherwise, use `"plan.reality-loop"`.
- `request_json`: Store the entire envelope as JSONB for full context:
  ```json
  {
    "envelope_type": "capability_session",
    "envelope_version": "1.0",
    "envelope_id": "NEXT_STEPS:1",
    "title": "...",
    "source": "NEXT_STEPS",
    "plan": {...},
    "posture": {...},
    "available": true
  }
  ```

## Mapping to `public.ai_interactions` (Optional)

**Target Table:** `public.ai_interactions` (legacy/alternative tracking)

**Note:** This mapping is **optional** and may not be used. If implemented:

- `session_id` - Generated UUID (different from envelope `id`)
- `interaction_type` - `"plan.reality-loop"` or `"plan.capability_session"`
- `user_query` - `plan.raw_line` or `title`
- `ai_response` - `null` (envelope is intent, not AI response)
- `tools_used` - `["pmagent", "plan", "reality-loop"]`
- `context_provided` - `plan` dict (current_focus, next_milestone, dry_run_command)
- `execution_time_ms` - `null` (not executed)
- `success` - `true` (envelope creation succeeded)
- `error_details` - `null`
- `created_at` - Timestamp from envelope filename

## Validation Contract

The hermetic validator (`agentpm/reality/capability_envelope_validator.py`) checks:

**Required Fields:**
- `type` must be `"capability_session"`
- `version` must be `"1.0"`
- `id` must be present and non-empty
- `title` must be present and non-empty
- `source` must be present (typically `"NEXT_STEPS"`)
- `plan` must be present with:
  - `current_focus` (string or null)
  - `next_milestone` (string or null)
  - `raw_line` (string or null)
- `posture` must be present with:
  - `mode` (`"live"` or `"hermetic"`)

**Optional Fields (with validation if present):**
- `plan.dry_run_command` - If present, must be a non-empty string
- `posture.reality.overall_ok` - If `posture.mode == "live"`, should be present (bool)
- `posture.status.level` - If `posture.mode == "live"`, should be present (string)
- `posture.status.headline` - If `posture.mode == "live"`, should be present (string)

**Derived Tracking Fields (computed, not stored in envelope):**
- `derived_tracking.command` - Command string for `control.agent_run_cli.command`
- `derived_tracking.request_json` - Full envelope structure for `control.agent_run_cli.request_json`
- `derived_tracking.timestamp` - RFC3339 timestamp from filename or file mtime

## Writer Path (Future)

**Status:** Implemented but gated; default OFF

**Gating:** Controlled by `PMAGENT_TRACK_SESSIONS=1` environment variable or explicit opt-in flag (e.g., `--track-session` in CLI). Default behavior is **no DB writes** (hermetic).

**Writer Helper:** `agentpm/reality/capability_envelope_writer.py`

**Function:** `maybe_persist_capability_session(envelope: dict[str, Any], *, tracking_enabled: bool) -> dict[str, Any]`

**Behavior:**
- If `tracking_enabled=False`: Returns `{"written": False, "mode": "disabled"}` (no DB calls)
- If DB unavailable (DSN missing or connection fails): Returns `{"written": False, "mode": "db_off"}` (graceful no-op)
- If DB available and tracking enabled: Calls `agentpm.control_plane.create_agent_run()` to insert a row

**Mapping to `control.agent_run_cli`:**
- `command`: Uses `plan.dry_run_command` if present and non-empty, else `"plan.reality-loop"`
- `status`: `"started"` (envelope represents planned work, not executed)
- `request_json`: Full envelope structure (entire `capability_session` dict)
- `response_json`: `null` (envelope is intent/preview, not execution result)
- `error_text`: `null` (envelope is intent/preview, not execution result)

**Integration Point:** `validate_and_optionally_persist()` in `agentpm/reality/capability_envelope_validator.py`
- First runs `validate_capability_envelope()` (hermetic validation)
- If validation fails OR `tracking_enabled=False`: Returns validation result only (no DB calls)
- If validation passes AND `tracking_enabled=True`: Calls `maybe_persist_capability_session()` and merges result under `"tracking"` key

**DB-Off Behavior:**
- All DB failures are caught and returned as structured results (no exceptions raised)
- Returns `{"written": False, "mode": "db_off"}` or `{"written": False, "mode": "error", "error": "..."}` on failure
- No side effects when DB is unavailable (hermetic behavior)

## Implementation Status

**Current State:**
- ✅ Envelope structure defined (`agentpm/plan/next.py`)
- ✅ Hermetic validator implemented (`agentpm/reality/capability_envelope_validator.py`)
- ✅ CLI validation commands (`pmagent reality validate-capability-envelope`, `validate-capability-history`)
- ✅ **Gated writer path implemented** (`agentpm/reality/capability_envelope_writer.py`)
- ✅ Integration helper (`validate_and_optionally_persist()`)
- ✅ Tests proving clean DB-off behavior
- ❌ **CLI wiring NOT implemented** (library-only; no default behavior change)

**Future Implementation:**
- CLI flag `--track-session` for `pmagent plan reality-loop` (opt-in, default OFF)
- Will call `validate_and_optionally_persist()` when flag is set
- Must maintain identical behavior when tracking is disabled (no DB calls)

## Related Documentation

- `agentpm/plan/AGENTS.md` - Planning shell (reality-loop + history)
- `agentpm/control_plane.py` - `create_agent_run()` helper (future writer)
- `migrations/051_control_agent_run_cli.sql` - Target table schema
- `agentpm/AGENTS.md` - AI tracking tables overview

