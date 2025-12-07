# RFC-081 — Unified UI & BibleScholar as Module

**Status:** Draft  
**Owner:** PM (ChatGPT) + Orchestrator (human)  
**Date:** 2025-11-15

## 1. Summary

This RFC defines the long-term unification plan for the Gemantria ecosystem:

- **Single core:** `Gemantria.v2` as the control-plane and orchestration OS.

- **Single UI:** a unified React/Tailwind web application (current `webui/graph` to be generalized).

- **BibleScholar as module:** BibleScholar becomes a backend/domain module inside Gemantria, not a separate UI framework.

- **StoryMaker & other projects:** treated as *donor* projects that contribute code/ideas into this unified framework, not separate long-lived apps.

The goal is to reduce complexity, eliminate duplicated UI stacks, and make the system approachable for medium-tech users while remaining AI-friendly.

## 2. Motivation

### 2.1 Fragmentation

We currently have or have had:

- `Gemantria.v2` — control-plane, exports, LM budgets, Knowledge Slice, and a partial web UI.

- BibleScholar projects — Flask/Jinja UIs plus domain logic.

- StoryMaker — React UI and flows.

- Additional experiments (e.g. SacredNumbers, gemantria_pipeline, gematria_langgraph_restored, RippleAGI).

This leads to:

- Multiple front-end stacks (React, Jinja, prototype UIs).

- Multiple patterns for reading the same exports (LM indicator, Knowledge Slice).

- Higher cognitive load for humans and AI agents.

- Difficulty delivering a coherent, pleasant user experience.

### 2.2 User intent

The orchestrator's original intent:

- Gemantria = numeric/control layer.

- BibleScholar = second layer that uses Gemantria's numbers and knowledge.

- Other projects = idea/code reservoirs for the main system, not separate products.

This RFC realigns the implementation with that intent.

## 3. Architecture Decisions

### 3.1 Single core OS: Gemantria.v2

- **Control-plane:** Postgres `control` schema, LM logs, LM budgets, Knowledge Slice, guarded tool calls.

- **Exports:** JSON exports under `share/atlas/control_plane/` used by all apps.

- **Governance:** RULES_INDEX, MASTER_PLAN, PLAN-* episodes remain here.

BibleScholar and StoryMaker logic will live as *modules* within this core, using existing patterns (e.g. `pmagent/…`).

### 3.2 Single UI: React/Tailwind web app

- The existing `webui/graph` React app will be generalized into a unified UI shell (eventually likely `apps/webui`).

- All visible features live here:

  - Graph and metrics panels.

  - Knowledge Slice panels.

  - StoryMaker flows.

  - BibleScholar tools & visualizations.

  - Future RAG/search, dashboards, and LM Studio-facing UX.

Styling and layout will be normalized using Tailwind and simple, reusable components.

### 3.3 BibleScholar as backend module

- BibleScholar becomes a Python module (e.g. `pmagent/biblescholar/` or similar).

- Responsibilities:

  - Bible-specific domain logic (passage selection, references, transformations).

  - Data access via Gemantria exports / control-plane, not direct DB from the UI.

- No separate front-end framework:

  - Existing Jinja/CSS panels are treated as reference implementations and will be **harvested** into React.

  - No new features will be added to legacy BibleScholar UIs after this RFC is accepted.

### 3.4 Other projects as donors

Projects such as:

- `BibleScholarProjectClean`

- `StoryMaker`

- `SacredNumbers`

- `gemantria_pipeline`, `gematria_langgraph_restored`

- `RippleAGI`, etc.

are treated as **donor projects**:

- We selectively port:

  - Algorithms

  - Data models

  - Prompt formats

  - UI ideas

- We do *not* attempt to maintain them as fully independent apps long-term.

## 4. Migration Phases (High-Level)

### Phase A — Intake & mapping

- Use `docs/SSOT/PROJECTS_INVENTORY.md` as a starting map.

- Create and fill:

  - `docs/SSOT/BIBLESCHOLAR_INTAKE.md`

  - `docs/SSOT/STORYMAKER_INTAKE.md`

- Identify:

  - Core BibleScholar domain modules to port.

  - StoryMaker components/pages that should be brought into the unified UI.

  - High-value logic from SacredNumbers/pipelines.

### Phase B — BibleScholar module in Gemantria

- Create an `pmagent/biblescholar/` (or equivalent) module.

- Port the identified BibleScholar domain logic.

- Add tests and minimal integration points.

- Keep it UI-agnostic.

### Phase C — Unified UI pages

- Generalize `webui/graph` into a named unified app (e.g. `apps/webui`).

- Add BibleScholar pages with:

  - Basic Bible reading.

  - First wave of BibleScholar-powered tools.

- Ensure LM indicator, Knowledge Slice, and future RAG contexts are visible where relevant.

### Phase D — Deprecate legacy UIs

- Mark legacy BibleScholar and other old UI shells as deprecated in their READMEs.

- Clearly state:

  - "Do not add new features here; use the unified UI in Gemantria.v2 instead."

- Keep them only for reference until their ideas are fully harvested.

## 5. Non-Goals

- This RFC does not attempt to:

  - Fully specify every React route or visual design detail.

  - Replace existing governance (PLAN-0xx) structures.

  - Define RAG prompts or detailed BibleScholar pipelines.

Those will be covered by follow-up PLAN episodes and possibly additional RFCs.

## 6. Open Questions

- Exact directory structure for the unified UI (`webui/graph` vs `apps/webui`).

- Final naming for the BibleScholar module package.

- How much of SacredNumbers and older pipelines should be ported vs. retired.

- Whether some donor projects should be archived after migration is complete.

## 7. Acceptance Criteria

This RFC is considered "Accepted" when:

- It is referenced from `RULES_INDEX.md` and `MASTER_PLAN.md`.

- BibleScholar and StoryMaker intake docs exist and are used in planning.

- New UI work (BibleScholar/StoryMaker features) targets the unified React app, not legacy UIs.

