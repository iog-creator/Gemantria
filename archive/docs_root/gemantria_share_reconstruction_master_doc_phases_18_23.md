# Gemantria — Share Reconstruction Master Doc (Phases 18–23)

> **Purpose:** This document is a *disaster-recovery blueprint* for rebuilding the entire `share/` surface after destructive housekeeping. Cursor should treat this as the **single source of instructions** for restoring:
>
> * Phase 18–23 share artifacts
> * Orchestrator & Orchestrator Assistant surfaces
> * Console v2 schema + view model
> * Core surfaces (`SSOT_SURFACE_V17.json`, `PM_BOOTSTRAP_STATE.json`)
> * Stress / smoke harness notes
>
> Style: **Summarized description + fenced code blocks** suitable for copy-paste. Where a file is normally auto-generated, this doc includes both:
>
> * A *minimal viable content template* and
> * The **command** Cursor should run to regenerate it from SSOT.

---

## 0. Global Rules for Reconstruction

1. **Do NOT run destructive housekeeping without a backup**
   * Before any operation that deletes/moves/overwrites files (especially in `share/`), create a snapshot:

     ```bash
     # Example backup pattern (to be implemented as a proper script/target later)
     mkdir -p evidence/backups/$(date +%Y%m%d_%H%M%S)
     cp -a share evidence/backups/$(date +%Y%m%d_%H%M%S)/share
     ```

2. **Rebuild first, then reintroduce any housekeeping**
   * Recreate all files and directories listed in this document **before** running `make share.sync`, `make housekeeping`, or any destructive script.

3. **After reconstruction, always run:**

   ```bash
   source .venv/bin/activate
   make reality.green STRICT=1
   make stress.smoke PHASE=23 MODE=HINT  # or equivalent, if target name changed
   ```

4. **This document is not SSOT**
   * SSOT remains: **Postgres DMS**, plus the canonical docs in `docs/SSOT/`.
   * This file is a **rebuild recipe** for the `share/` surface and console v2 wiring.

---

## 1. Target Directory Layout

Recreate the following structure under the repo root:

```text
share/
  SSOT_SURFACE_V17.json
  PM_BOOTSTRAP_STATE.json

  # Phase summaries
  PHASE18_INDEX.md
  PHASE18_AGENTS_SYNC_SUMMARY.json
  PHASE18_SHARE_EXPORTS_SUMMARY.json
  PHASE18_LEDGER_REPAIR_SUMMARY.json

  PHASE19_SHARE_HYGIENE_SUMMARY.json

  PHASE20_INDEX.md
  PHASE20_ORCHESTRATOR_UI_MODEL.md
  PHASE20_UI_RESET_DECISION.md

  PHASE21_INDEX.md
  PHASE21_CONSOLE_SERVE_PLAN.md

  PHASE22_INDEX.md
  PHASE22_OPERATOR_WORKFLOW.md

  PHASE23_INDEX.md
  PHASE23_STRESS_PLAN.md
  PHASE23_BASELINE_NOTE.md
  PHASE23_BOOTSTRAP_HARDENING_NOTE.md
  PHASE23_STRESS_SMOKE_NOTE.md
  PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.json
  PHASE23_FAILURE_INJECTION_NOTE.md

  # KB / registry snapshot
  kb_registry.json

  # Orchestrator & OA surfaces
  orchestrator/
    STATE.json
    NOTES.md
    DECISION_LOG.json
    RESEARCH_INDEX.md
    ACTIVE_PROMPTS.md
    CONSOLE_SCHEMA.json
    VIEW_MODEL.json

  orchestrator_assistant/
    STATE.json
    NOTES.md
    DECISION_LOG.json
    RESEARCH_INDEX.md
    ACTIVE_PROMPTS.md

  # Atlas exports for control-plane health
  atlas/
    control_plane/
      system_health.json
      lm_indicator.json

  # Docs-control exports
  exports/
    docs-control/
      canonical.json
      summary.json
```

> **Note:** Some of these (e.g. `kb_registry.json`, `canonical.json`, `summary.json`, `system_health.json`, `lm_indicator.json`) are typically generated from DB/DMS via existing scripts. This doc gives *minimal viable content* where needed, plus the commands to regenerate correctly.

---

## 2. Core Surfaces

### 2.1 `share/SSOT_SURFACE_V17.json`

**Purpose:** Human-readable snapshot of SSOT status: DB online, DMS health, doc registry stats, recent phases.

**Rebuild approach:**

* If there is a script that exports this from Postgres/DMS, use that as primary.
* If not, recreate a **minimal skeleton** and keep details high-level.

**Template (minimal skeleton):**

```jsonc
{
  "version": 17,
  "generated_by": "disaster-recovery-rebuild",
  "description": "High-level SSOT surface snapshot for Gemantria.",
  "db": {
    "status": "unknown",        // Replace with real status after checks
    "last_checked_at": null
  },
  "dms": {
    "doc_registry_count": 1091,  // as observed in prior phases
    "hint_registry_status": "unknown"
  },
  "phases": {
    "last_completed": 23,
    "notes": "Phases 18-23 rebuilt from recovery doc. See per-phase files in share/."
  }
}
```

Once DB connectivity is verified, you can later update this via whatever export script was used previously.

---

### 2.2 `share/PM_BOOTSTRAP_STATE.json`

**Purpose:** Snapshot of PM-facing governance & surfaces; tells the PM what phases exist, which docs are high-importance, and where the console v2 lives.

**Rebuild approach:**

* Minimal structure: meta + phases + webui.console_v2 section.
* Actual DMS-backed details can be refreshed later via `make pm.bootstrap.state` **after** scripts are restored and hardened.

**Template:**

```jsonc
{
  "meta": {
    "current_phase": "23",
    "last_completed_phase": "23",
    "generated_by": "disaster-recovery-rebuild",
    "notes": "Reconstructed from chat + recovery doc. Exact DMS counts may differ."
  },
  "phases": {
    "18": {
      "name": "Share Governance & Ledger Repair",
      "status": "complete",
      "artifacts": [
        "share/PHASE18_INDEX.md",
        "share/PHASE18_AGENTS_SYNC_SUMMARY.json",
        "share/PHASE18_SHARE_EXPORTS_SUMMARY.json",
        "share/PHASE18_LEDGER_REPAIR_SUMMARY.json"
      ]
    },
    "19": {
      "name": "Share Hygiene Cleanup",
      "status": "complete",
      "artifacts": [
        "share/PHASE19_SHARE_HYGIENE_SUMMARY.json"
      ]
    },
    "20": {
      "name": "Orchestrator Console v2 UI Reset & Design",
      "status": "complete",
      "artifacts": [
        "share/PHASE20_INDEX.md",
        "share/PHASE20_UI_RESET_DECISION.md",
        "share/PHASE20_ORCHESTRATOR_UI_MODEL.md"
      ]
    },
    "21": {
      "name": "Console v2 Serving & CI",
      "status": "complete",
      "artifacts": [
        "share/PHASE21_INDEX.md",
        "share/PHASE21_CONSOLE_SERVE_PLAN.md"
      ]
    },
    "22": {
      "name": "Operator Workflow & Console v2 Registration",
      "status": "complete",
      "artifacts": [
        "share/PHASE22_INDEX.md",
        "share/PHASE22_OPERATOR_WORKFLOW.md"
      ]
    },
    "23": {
      "name": "Stress Epoch & Guard Hardening",
      "status": "in_progress",
      "artifacts": [
        "share/PHASE23_INDEX.md",
        "share/PHASE23_STRESS_PLAN.md",
        "share/PHASE23_BASELINE_NOTE.md",
        "share/PHASE23_BOOTSTRAP_HARDENING_NOTE.md",
        "share/PHASE23_STRESS_SMOKE_NOTE.md",
        "share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.json",
        "share/PHASE23_FAILURE_INJECTION_NOTE.md"
      ]
    }
  },
  "webui": {
    "console_v2": {
      "source": "webui/orchestrator-console-v2/",
      "dev_server": "scripts/dev/serve_console_v2.py",
      "ci_check": "scripts/pm/check_console_v2.py",
      "schema": "share/orchestrator/CONSOLE_SCHEMA.json",
      "view_model": "share/orchestrator/VIEW_MODEL.json",
      "dev_url": "http://localhost:8080/console-v2/",
      "surfaces_consumed": [
        "share/SSOT_SURFACE_V17.json",
        "share/PM_BOOTSTRAP_STATE.json",
        "share/PHASE18_INDEX.md",
        "share/PHASE18_AGENTS_SYNC_SUMMARY.json",
        "share/PHASE18_SHARE_EXPORTS_SUMMARY.json",
        "share/PHASE18_LEDGER_REPAIR_SUMMARY.json",
        "share/PHASE19_SHARE_HYGIENE_SUMMARY.json",
        "share/PHASE20_UI_RESET_DECISION.md",
        "share/PHASE20_ORCHESTRATOR_UI_MODEL.md",
        "share/PHASE21_CONSOLE_SERVE_PLAN.md",
        "share/orchestrator/STATE.json",
        "share/orchestrator_assistant/STATE.json",
        "share/atlas/control_plane/system_health.json",
        "share/atlas/control_plane/lm_indicator.json",
        "share/exports/docs-control/canonical.json",
        "share/exports/docs-control/summary.json",
        "share/kb_registry.json"
      ]
    }
  }
}
```

> **After scripts are restored and hardened**, regenerate this via `make pm.bootstrap.state` and ensure the `webui.console_v2` section is preserved (as we previously did with the bootstrap patch script).

---

## 3. Orchestrator & Orchestrator Assistant Surfaces

These surfaces are consumed by the console v2 and used by PM/OA.

### 3.1 `share/orchestrator/STATE.json`

**Purpose:** Captures orchestrator’s role, preferences, and the key surfaces the console should watch.

**Template:**

```jsonc
{
  "version": 1,
  "role": "orchestrator",
  "description": "Top-level product owner view for Gemantria. This surface expresses the orchestrator's current focus, preferences, and key state for all agents.",
  "generated_by": "Phase 18.4 reconstruction",
  "branch": "feat/repo-governance-pr3-alignment-guard",
  "active_phase": "23",
  "last_completed_phase": "22",
  "decision_focus": [
    "Stabilization and governance of share/ and reality.green surfaces",
    "Design and behavior of the orchestrator console UI (v2)",
    "Tight integration of Orchestrator Assistant (OA), pmagent, and Cursor"
  ],
  "preferences": {
    "communication_style": "direct",
    "ops_visibility": "pm-only (OPS blocks for Cursor, summaries for Orchestrator)",
    "ui_principles": [
      "single chatbox as conductor console",
      "no implementation details or wiring shown to the orchestrator",
      "status and surfaces auto-refresh based on backend state"
    ]
  },
  "surfaces": {
    "pm_bootstrap_state": "share/PM_BOOTSTRAP_STATE.json",
    "ssot_surface": "share/SSOT_SURFACE_V17.json",
    "phase_index_18": "share/PHASE18_INDEX.md",
    "phase_index_19": "share/PHASE19_SHARE_HYGIENE_SUMMARY.json",
    "phase_index_20": "share/PHASE20_INDEX.md",
    "phase_index_21": "share/PHASE21_INDEX.md",
    "phase_index_22": "share/PHASE22_INDEX.md",
    "phase_index_23": "share/PHASE23_INDEX.md",
    "orchestrator_surface_root": "share/orchestrator/",
    "orchestrator_assistant_surface_root": "share/orchestrator_assistant/"
  }
}
```

---

### 3.2 `share/orchestrator/NOTES.md`

**Purpose:** Freeform notes shared between Orchestrator and PM.

**Template:**

```markdown
# Orchestrator Notes Surface

This file is the primary freeform notes surface for the Orchestrator and PM.

## How to Use

- **Orchestrator**: Capture intent, constraints, and approvals here in human language.
- **PM**: Summarize key agreements, next phases, and what Cursor is currently doing.
- **Orchestrator Assistant (OA)**: When synthesizing research, add clearly labeled sections (e.g., "OA: Research summary on X").

## Conventions

- Use clear headings per topic or phase (e.g., "Phase 23 — Stress Epoch").
- When referencing evidence, include the path (e.g., `evidence/...` or `share/...`).
- Avoid implementation details; focus on **decisions** and **intent**.
```

---

### 3.3 `share/orchestrator/DECISION_LOG.json`

**Purpose:** Append-only record of orchestrator-level decisions.

```jsonc
{
  "version": 1,
  "role": "orchestrator",
  "description": "Append-only decision log for orchestrator-level choices, used by PM, OA, and Cursor.",
  "decisions": [
    {
      "id": "2025-12-04-ui-reset",
      "timestamp": "2025-12-04T00:00:00Z",
      "summary": "Reset only the UI layer, freeze legacy webui, introduce Orchestrator Console v2.",
      "phase": 20
    }
  ]
}
```

You can keep this minimal and expand over time.

---

### 3.4 `share/orchestrator/RESEARCH_INDEX.md`

**Purpose:** Pointers for the OA to quickly find governance, SSOT, and monitoring docs.

```markdown
# Orchestrator Research Index

This file is the starting point for the Orchestrator Assistant (OA).

## Core Governance

- `docs/SSOT/MASTER_PLAN.md`
- `docs/SSOT/RULES_INDEX.md`
- `docs/SSOT/SHARE_SURFACE_CONTRACT.md`
- `docs/SSOT/webui-contract.md`

## Key Surfaces

- `share/SSOT_SURFACE_V17.json`
- `share/PM_BOOTSTRAP_STATE.json`
- `share/PHASE20_UI_RESET_DECISION.md`
- `share/PHASE20_ORCHESTRATOR_UI_MODEL.md`
- `share/PHASE21_CONSOLE_SERVE_PLAN.md`
- `share/PHASE22_OPERATOR_WORKFLOW.md`
- `share/PHASE23_STRESS_PLAN.md`

## Monitoring & Health

- `share/atlas/control_plane/system_health.json`
- `share/atlas/control_plane/lm_indicator.json`
- `share/exports/docs-control/canonical.json`
- `share/exports/docs-control/summary.json`
```

---

### 3.5 `share/orchestrator/ACTIVE_PROMPTS.md`

**Purpose:** The "actionable prompts" lane used by console v2 to show what PM/OA/Cursor should be doing.

```markdown
# Orchestrator Active Prompts

## High Priority

- Ensure pmagent, hints, envelopes, and DMS are using the **new share surfaces** exclusively.
- Validate Orchestrator Console v2 wiring via `make stress.smoke` and `python scripts/pm/check_console_v2.py`.

## Medium Priority

- Expand tool-calling scenarios for tiny models, ensuring they pick the right tools (pmagent, guards, exporters).
- Harden backup-before-housekeeping guard.

## Low Priority

- Refine console v2 styling and layout as needed.
- Add richer summaries to phase docs (18–23).
```

---

### 3.6 Orchestrator Assistant Surfaces (`share/orchestrator_assistant/*`)

You can mirror the orchestrator structure with OA-specific content.

#### 3.6.1 `STATE.json`

```jsonc
{
  "version": 1,
  "role": "orchestrator_assistant",
  "description": "Research and analysis assistant for the Orchestrator and PM.",
  "primary_tasks": [
    "Perform Rule 070 gotchas checks before major phases.",
    "Propose phase plans and stress scenarios.",
    "Cross-check governance docs for drift (SHARE_SURFACE_CONTRACT, webui-contract, ADRs)."
  ],
  "truth_hierarchy": [
    "Postgres DMS (SSOT)",
    "docs/SSOT/*.md",
    "share/ surfaces",
    "pmagent/ outputs"
  ]
}
```

#### 3.6.2 `NOTES.md`

```markdown
# Orchestrator Assistant Notes

Use this file as a scratchpad for research.

- Record Rule 070 gotchas checks.
- Capture ADR and governance cross-references.
- Propose revised phase plans before PM approval.
```

#### 3.6.3 `DECISION_LOG.json`

```jsonc
{
  "version": 1,
  "role": "orchestrator_assistant",
  "description": "Log of OA proposals and analyses that influenced PM decisions.",
  "entries": []
}
```

#### 3.6.4 `RESEARCH_INDEX.md` and `ACTIVE_PROMPTS.md`

You can clone the orchestrator versions but tune the prompts to OA responsibilities (rule checks, ADR scans, etc.).

---

## 4. Console v2 Schema & View Model

These files live in `share/orchestrator/` and are consumed by `webui/orchestrator-console-v2/`.

### 4.1 `share/orchestrator/CONSOLE_SCHEMA.json`

**Purpose:** Declarative layout: regions, tiles, and modes for the console.

**Minimal reconstructed structure (simplified):**

```jsonc
{
  "version": 2,
  "regions": {
    "conversation": {
      "type": "center_pane",
      "description": "Chat + context + prompts"
    },
    "right_status": {
      "type": "status_pane",
      "tiles": [
        "system_status",
        "phase_governance",
        "docs_registry",
        "orchestrator_oa"
      ]
    },
    "left_nav": {
      "type": "nav_pane",
      "modes": ["overview", "docs", "temporal", "forecast", "graph"]
    }
  },
  "tiles": {
    "system_status": {
      "inputs": ["ssot_surface", "control_plane_exports"],
      "signals": ["db_health", "lm_indicator"]
    },
    "phase_governance": {
      "inputs": ["phase_index", "phase_summaries"],
      "signals": ["current_phase"]
    },
    "docs_registry": {
      "inputs": ["docs_control_exports", "kb_registry"],
      "signals": ["docs_state"]
    },
    "orchestrator_oa": {
      "inputs": ["orchestrator_state", "oa_state"],
      "signals": ["agents_ready"]
    }
  }
}
```

> If you still have the original file content in another backup, replace this with the exact schema. This skeleton is enough to keep the console build and tile loaders coherent.

---

### 4.2 `share/orchestrator/VIEW_MODEL.json`

**Purpose:** Maps logical data sources to concrete `share/` paths and associates them with UI regions.

**Reconstructed shape (simplified but aligned with prior description):**

```jsonc
{
  "version": 2,
  "data_sources": {
    "ssot_surface": {
      "path": "share/SSOT_SURFACE_V17.json",
      "type": "json",
      "used_by": ["system_status"]
    },
    "pm_bootstrap": {
      "path": "share/PM_BOOTSTRAP_STATE.json",
      "type": "json",
      "used_by": ["conversation"]
    },
    "phase_index": {
      "path": "share/PHASE23_INDEX.md",
      "type": "markdown",
      "used_by": ["conversation", "phase_governance"]
    },
    "phase_summaries": {
      "paths": [
        "share/PHASE18_AGENTS_SYNC_SUMMARY.json",
        "share/PHASE18_SHARE_EXPORTS_SUMMARY.json",
        "share/PHASE18_LEDGER_REPAIR_SUMMARY.json",
        "share/PHASE19_SHARE_HYGIENE_SUMMARY.json"
      ],
      "type": "json",
      "used_by": ["phase_governance"]
    },
    "ui_decision": {
      "path": "share/PHASE20_UI_RESET_DECISION.md",
      "type": "markdown",
      "used_by": ["conversation"]
    },
    "orchestrator_state": {
      "path": "share/orchestrator/STATE.json",
      "type": "json",
      "used_by": ["conversation", "orchestrator_oa"]
    },
    "oa_state": {
      "path": "share/orchestrator_assistant/STATE.json",
      "type": "json",
      "used_by": ["conversation", "orchestrator_oa"]
    },
    "orchestrator_prompts": {
      "path": "share/orchestrator/ACTIVE_PROMPTS.md",
      "type": "markdown",
      "used_by": ["conversation"]
    },
    "oa_prompts": {
      "path": "share/orchestrator_assistant/ACTIVE_PROMPTS.md",
      "type": "markdown",
      "used_by": ["conversation"]
    },
    "docs_control_exports": {
      "path": "share/exports/docs-control/",
      "type": "directory",
      "used_by": ["docs_registry"]
    },
    "control_plane_exports": {
      "path": "share/atlas/control_plane/",
      "type": "directory",
      "used_by": ["system_status"]
    },
    "kb_registry": {
      "path": "share/kb_registry.json",
      "type": "json",
      "used_by": ["docs_registry"]
    }
  },
  "bindings": {
    "conversation": [
      "pm_bootstrap",
      "phase_index",
      "phase_summaries",
      "ui_decision",
      "orchestrator_state",
      "oa_state",
      "orchestrator_prompts",
      "oa_prompts"
    ],
    "right_status": [
      "system_status",
      "phase_governance",
      "docs_registry",
      "orchestrator_oa"
    ],
    "left_nav": ["overview", "docs", "temporal", "forecast", "graph"]
  }
}
```

> After restoring the exact VIEW_MODEL.json from any backup or future phase, ensure paths still match the reconstructed `share/` tree.

---

## 5. Phase Docs (18–23)

For each phase, recreate a minimal but accurate summary doc in `share/PHASENN_*.md` or `.json`. These act as **human-readable history** and are already wired into PM and console surfaces.

Below are **templates**; you can adjust wording as needed.

### 5.1 Phase 18 — Share Governance & Ledger Repair

#### `share/PHASE18_INDEX.md`

```markdown
# Phase 18 — Share Governance & Ledger Repair

## 18.1 AGENTS Sync
- Ensured AGENTS.md files are in sync with code.

## 18.2 Share Exports
- Validated share exports against DMS and SSOT.

## 18.3 Share Contract & Index
- Introduced SHARE_SURFACE_CONTRACT.
- Created PHASE18 index and summaries.

## 18.3b Ledger Repair
- Fixed Makefile references (agentpm → pmagent) for state.sync/state.verify.
- Updated ledger hashes for 9 artifacts; ledger fully green.

## 18.4 Orchestrator Surfaces
- Created orchestrator and orchestrator_assistant surfaces under share/.
- Regenerated PM bootstrap and validated reality.green.
```

#### JSON summaries

`PHASE18_AGENTS_SYNC_SUMMARY.json`, `PHASE18_SHARE_EXPORTS_SUMMARY.json`, `PHASE18_LEDGER_REPAIR_SUMMARY.json` can be kept minimal:

```jsonc
{
  "phase": 18,
  "subphase": "agents_sync",
  "status": "complete",
  "notes": "AGENTS.md sync verified against scripts and webui modules."
}
```

(Adjust keys per your previous structure if you recall them; structure matters less than path stability for console v2.)

---

### 5.2 Phase 19 — Share Hygiene

`share/PHASE19_SHARE_HYGIENE_SUMMARY.json`:

```jsonc
{
  "phase": 19,
  "name": "Share Hygiene",
  "status": "complete",
  "actions": [
    "Archived obsolete planning docs to archive/share/.",
    "Deleted duplicate SSOT copies from share/.",
    "Validated remaining files against SHARE_SURFACE_CONTRACT (target count ~25)."
  ]
}
```

---

### 5.3 Phase 20 — UI Reset & Orchestrator Console v2

`share/PHASE20_UI_RESET_DECISION.md`:

```markdown
# Phase 20 — UI Reset Decision

## Key Decision

- Reset **only** the UI layer.
- Freeze existing `webui/*` as legacy UI v1 (orchestrator-shell, graph, dashboard).
- Introduce **Orchestrator Console v2** based on share/ surfaces.

## Data Sources

- `share/SSOT_SURFACE_V17.json`
- `share/PM_BOOTSTRAP_STATE.json`
- `share/orchestrator/*` and `share/orchestrator_assistant/*`
- `share/exports/docs-control/*.json`
- `share/atlas/control_plane/*.json`
```

`share/PHASE20_ORCHESTRATOR_UI_MODEL.md` can describe the three-region layout as previously done.

---

### 5.4 Phase 21 — Console Serving & CI

`share/PHASE21_INDEX.md`:

```markdown
# Phase 21 — Orchestrator Console v2 Data Serving & CI

## 21.0 Console Serve Plan
- Documented dev/prod serving strategy for console v2 and share/.

## 21.1 Dev Server
- Implemented `scripts/dev/serve_console_v2.py`.
- Serves `/console-v2/` and `/share/` on port 8080.

## 21.2 CI Check
- Implemented `scripts/pm/check_console_v2.py`.
- Validates VIEW_MODEL paths under share/ and runs `npm run build` as smoke test.
```

`share/PHASE21_CONSOLE_SERVE_PLAN.md` can keep the more detailed description you already had; if lost, a shorter version is still workable.

---

### 5.5 Phase 22 — Operator Workflow

`share/PHASE22_INDEX.md` and `share/PHASE22_OPERATOR_WORKFLOW.md` should capture that console v2 is now a first-class operator tool, with dev URL and expectations on how operators use it.

---

### 5.6 Phase 23 — Stress Epoch

`share/PHASE23_INDEX.md` (minimal):

```markdown
# Phase 23 — Stress Epoch & Guard Hardening

Subphases:
- 23.0: Stress plan docs
- 23.0a: Baseline checkpoint
- 23.0b: Bootstrap hardening
- 23.0c: AGENTS.md sync repair
- 23.1: stress.smoke harness
- 23.2: Failure injection (shadow-like behavior)
- 23.3: Tool-calling test vectors (planned)
```

For each of the Phase 23 docs (baseline note, bootstrap hardening note, stress smoke note, agents sync summary, failure injection note), you can recreate short narrative summaries similar to what you described in chat.

---

## 6. Exports & Atlas Surfaces

### 6.1 `share/atlas/control_plane/system_health.json` & `lm_indicator.json`

These are consumed by console v2 as part of **system_status** tile. If you don’t have the original structures, reconstruct minimal JSON with clear placeholders and later regenerate them from their original scripts.

```jsonc
{
  "status": "unknown",
  "note": "Recreated after share/ disaster; regenerate from control-plane health scripts when available."
}
```

### 6.2 `share/exports/docs-control/canonical.json` & `summary.json`

Similarly, these can be stubbed and later regenerated by the docs-control export pipeline.

```jsonc
{
  "status": "unknown",
  "note": "Docs-control export stub; regenerate via scripts/export_* once DB is online."
}
```

---

## 7. Recovery Procedure for Cursor

When Cursor uses this document to restore the system, follow this sequence:

1. **Create directory structure** exactly as in Section 1.
2. **Populate core surfaces** using the templates in Sections 2–4.
3. **Populate phase docs** using Section 5 templates.
4. **Create stub exports and atlas surfaces** per Section 6.
5. **Rebuild console v2 assets**:

   ```bash
   cd webui/orchestrator-console-v2
   npm install  # if needed
   npm run build
   cd ../..
   ```

6. **Verify via console checks**:

   ```bash
   source .venv/bin/activate
   python scripts/pm/check_console_v2.py --skip-build
   make stress.smoke PHASE=23 MODE=HINT
   ```

7. **Run full governance**:

   ```bash
   source .venv/bin/activate
   make reality.green STRICT=1
   ```

8. **Only after everything is green**, consider re-enabling `make share.sync` or any housekeeping — and *only* once a proper backup/rollback mechanism is in place.

---

## 8. Future Work: Backup Enforcement & Phase-DONE Checklist

Finally, use this reconstruction as the justification for:

- A **backup-before-housekeeping guard** that prevents repeat disasters.
- A **Phase-DONE checklist guard** that enforces:
  - AGENTS.md in sync
  - Hints & envelopes registered
  - share/ surfaces created
  - Console, CI, and stress harness updated.

Those guards will ensure we don’t rely on memory or luck the next time we evolve the system.

---

**End of Reconstruction Doc.**

Cursor: treat this as your authoritative recipe for recreating the `share/` surface and console v2 wiring after the catastrophic cleanup.

