# Gemantria Layered Architecture — Version 1 (SSOT)

**Status:** Conceptual baseline  
**Audience:** Orchestrator, PM, OA, Cursor, future UIs  
**Goal:** Describe the *conceptual* layers of the system so all tools and agents share the same mental model.

---

## 1. High-Level Stack

```text
┌─────────────────────── Layer 1: Orchestrator & UI ───────────────────────┐
│ - Orchestrator (user) via chat                                          │
│ - Orchestrator Assistant (OA)                                           │
│ - PM chat (this), Cursor OPS chat                                       │
│ - Future Conductor Console UI (chat + status tiles + icons)             │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────── Layer 2: Intelligence API / pmagent ─────────────────┐
│ pmagent CLI + "intelligence API"                                         │
│ - Normalizes tasks: PLAN, OPS, STATUS, EXPORT, RAG, DASHBOARD, etc.      │
│ - Enforces contracts (PM, EXECUTION, webui-contract, DOC_CONTROL_PANEL)  │
│ - Routes work to tools, scripts, DB, LM Studio, dashboards               │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────── Layer 3: Agent Spine & Guarded Tools ──────────────┐
│ Agents & modules (from AGENTS.md + kb_registry)                          │
│ - Scanner / Ingest: governance ingest, fragment classifier               │
│ - Memory: DMS adapter (registry, hints, ledger, share exports)           │
│ - Path Manager: Guarded Tool Calls, envelope + hints, Option A→B flows   │
│ - Dreaming: sandbox runs, what-if / forecast simulations (future)        │
│ - Breadcrumbs: evidence/repo/*, PHASE*_SNAPSHOT.json, purge logs         │
│ Guard Layer                                                               │
│ - reality.green STRICT                                                    │
│ - Guarded Tool Calls (STRICT/HINT modes, violation subsets)              │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────── Layer 4: Knowledge & Retrieval Engine ───────────────┐
│ "Living Truth" / Retrieval Stack                                         │
│ - Dynamic embedding selector (Postgres+pgvector; 1024d, etc.)            │
│ - Hybrid retriever: vector + SQL + keyword + phase-aware filters         │
│ - DSPy-style pipelines (planned)                                         │
│ - LM Studio connector (Qwen* models)                                     │
│ Robust JSON envelope                                                      │
│ - Envelope everywhere; schema-checked tool calls                          │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────── Layer 5: Analytics, GOLD & Compliance ───────────────┐
│ GOLD / Governance Analytics                                              │
│ - Control-plane views over doc_registry, hints, violations, phases       │
│ - Compliance dashboards (Phase 2 / Phase 3)                              │
│ - RAG quality / forecast accuracy metrics                                │
│ Compliance & Ledger                                                      │
│ - Guard violation subsets                                                │
│ - Ledger snapshots, PHASE*_AUDIT_SNAPSHOT.json                           │
│ - Phase 16 reports, purge logs, DB recon reports                         │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────── Layer 6: Data & Storage ─────────────────────────┐
│ Postgres (control schema)                                                │
│ - doc_registry, doc_version, doc_sync_state, hint_registry, embeddings   │
│ - compliance materialized views                                          │
│ File System                                                              │
│ - docs/SSOT (phase plans, contracts, designs)                            │
│ - share/ (exports, snapshots, PM_BOOTSTRAP_STATE.json, SSOT_SURFACE_V17) │
│ - archive/phase16_legacy (frozen historical evidence)                    │
│ LM Studio / Local models                                                 │
│ - Qwen stacks for RAG, Bible Scholar, PM helper                          │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────── Layer 7: Outputs & Handoffs ───────────────────────┐
│ - Final analyses, dashboards, forecasts                                  │
│ - New SSOT docs (PHASE*, COMPASS, plans)                                 │
│ - PM bootstrap state (PM_BOOTSTRAP_STATE.json)                           │
│ - Orchestrator status JSON (future: ORCHESTRATOR_STATUS_vX.json)         │
│ - Handoffs to new chats / new PM instances                               │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Layer-by-Layer Details

### 2.1 Layer 1 — Orchestrator & UI

**What lives here now**

* Orchestrator (user) in ChatGPT
* PM in PM chat
* Cursor in OPS chat
* Orchestrator Assistant (OA) as research / architecture helper

**Planned**

* Conductor Console UI:

  * Single chat input
  * Minimal icon bar (archive, db, vector, attach, status)
  * Shows status/choices as "Option A vs Option B" instead of raw debug.

This layer **never** touches DB or files directly. It talks to Layer 2.

---

### 2.2 Layer 2 — Intelligence API / pmagent

**Core idea:** all non-trivial work flows through **pmagent** as the "intelligence API".

Responsibilities:

* Normalize user/PM requests into categories:

  * PLAN, OPS, STATUS, EXPORT, RAG_QUERY, DASHBOARD_REFRESH, etc.
* Enforce contracts:

  * PM contract
  * EXECUTION_CONTRACT
  * webui-contract
  * DOC_CONTROL_PANEL_CONTRACT
* Route to:

  * scripts/
  * pmagent subcommands
  * DB queries
  * LM Studio calls
  * dashboard exporters

---

### 2.3 Layer 3 — Agent Spine & Guarded Tools

The internal cast of agents (from AGENTS.md + kb_registry) and the guard system around them.

**Roles**

* **Scanner / Ingest**
  Governance ingest scripts, doc fragment classifier, embeddings ingester.
* **Memory**
  DMS adapter to Postgres `control` schema (registry, hints, ledger, share exports).
* **Path Manager**
  Guarded Tool Call planner; interprets envelopes + hints; chooses tools/sequence.
* **Dreaming** (future)
  Sandboxed "what-if" runs for forecasts or design options.
* **Breadcrumbs**
  Writes evidence and logs: `evidence/repo/*`, `PHASE*_AUDIT_SNAPSHOT.json`, purge logs, DB recon reports.

**Guards**

* **reality.green STRICT** — global gate for "system ready" status.
* **Guarded Tool Calls** — envelopes + hints + violation subsets (STRICT/HINT modes).

---

### 2.4 Layer 4 — Knowledge & Retrieval Engine

The "Living Truth" retrieval stack.

Components:

* **Dynamic Embedding Selector**
  Uses Postgres+pgvector; chooses dims/models per task.
* **Hybrid Retriever**
  Vector + SQL + keyword + phase/importance filters.
* **DSPy-style Pipelines (planned)**
  Programmatic LM pipelines for RAG and PM helpers.
* **LM Studio Connector**
  Connects to local Qwen models through LM Studio endpoints.
* **Robust JSON Envelope**
  Every LM/tool call is wrapped in a schema-checked envelope (parse + retry + validate).

---

### 2.5 Layer 5 — Analytics, GOLD & Compliance

* **GOLD / Governance Analytics**

  * Views over doc_registry, hint_registry, violations, phases.
  * RAG quality & forecast accuracy (future).
* **Compliance Engine**

  * Enforces required violation subset; STRICT/HINT toggles.
* **Ledger & Audit**

  * ledger entries for key SSOT docs.
  * Phase artifacts like:

    * `PHASE*_AUDIT_SNAPSHOT.json`
    * `PHASE16_CLASSIFICATION_REPORT.json`
    * `PHASE16_PURGE_EXECUTION_LOG.json`
    * `PHASE16_DB_RECON_REPORT.json`

---

### 2.6 Layer 6 — Data & Storage

* **Postgres (control schema)**

  * `doc_registry`, `doc_version`, `doc_sync_state`, `hint_registry`, embeddings.
  * Compliance views / MVs.
* **File System**

  * `docs/SSOT` — phase plans, contracts, designs.
  * `share/` — exports, snapshots, `PM_BOOTSTRAP_STATE.json`, `SSOT_SURFACE_V17.json`.
  * `archive/phase16_legacy` — frozen historical evidence after Phase 16 purge.
* **LM Studio / Local Models**

  * Local models exposed via LM Studio.

---

### 2.7 Layer 7 — Outputs & Handoffs

Artifacts and external views:

* Analyses, dashboards, forecasts.
* New SSOT docs (PHASE*, COMPASS, plans).
* `share/PM_BOOTSTRAP_STATE.json` (new PM brain).
* Future: `share/ORCHESTRATOR_STATUS_vX.json` for the Conductor Console.
* Human-readable chat handoffs derived from bootstrap + surfaces.

---

## 3. How a New PM Instance Should Use This

1. Load `share/PM_BOOTSTRAP_STATE.json`.
2. Use this document as the conceptual map:

   * Which layer is this task touching?
   * Which SSOT docs are relevant?
   * Which agents/tools are involved?
3. Route all work through pmagent / Guarded Tool Calls.
4. Keep `reality.green` STRICT and the DMS as the ultimate truth.

---

## 4. Glossary (Short)

* **SSOT** — Single Source Of Truth.
* **DMS** — Document Management System (Postgres control schema + registry).
* **pmagent** — CLI / API that coordinates tools, DB, and LM.
* **Guarded Tool Call** — Tool invocation wrapped in a schema + hints, checked by guards.
* **Surface** — JSON summary of current world state (e.g. `SSOT_SURFACE_V17.json`).
* **Bootstrap State** — Minimal JSON (`PM_BOOTSTRAP_STATE.json`) a new PM chat needs to come online correctly.
