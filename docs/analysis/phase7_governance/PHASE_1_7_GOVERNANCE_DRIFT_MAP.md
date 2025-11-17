# Phase 1–7 Unified Governance Drift Map  

> Branch: feat/phase7.governance.rebuild.20251116-085215  

> Scope: Full-system drift analysis (Phases 1–7)  

> Status: Authoritative SSOT for governance reconstruction



---



# EXECUTIVE SUMMARY



Across Phases 1–7, the system shows **structural drift**, **governance drift**, and **runtime drift**.



**Core Pipeline (0–5)** → *Fully Implemented*  

**Knowledge + Runtime (6–7)** → *Partially Implemented*  

**Governance SSOT Migration** → *Not Implemented*  



This document merges:  

- Global drift (Phase 1–7)  

- Governance drift (Phase 7)  



It becomes the **single SSOT** for guiding Phase-7 governance reconstruction.



---



# 1. GLOBAL DRIFT (PHASES 1–7)



## Phase 1 — Data Layer (Complete with minor gaps)

- DB loaders + Hebrew normalization complete  

- Two-DB safety implemented  

- **Pending**: Phase-1 Control Plane tasks (STRICT/HINT CI, tag lane wiring, Atlas link)



## Phase 2 — Pipeline Core (Complete)

- LangGraph orchestrator complete  

- Postgres checkpointer working  

- Math verifier added (bonus)



## Phase 3 — Exports & Badges (Complete)



## Phase 3A–3D — Control Plane (Implementation complete, governance wiring missing)

- Migration 040 landed  

- All `pmagent control` commands implemented  

- Compliance exports complete  

- **Pending (3 tasks):**

  1. STRICT/HINT CI lanes  

  2. Tag-lane guard wiring  

  3. Atlas compliance-webproof linkage



## Phase 4 — LM Insights (Complete)



## Phase 5 — LM Integration (Complete)



## Phase 6 — LM Studio Live + Knowledge Slice (⚠ Partial)

- 6A–6C complete (LM live usage, budgets, knowledge slice)

- **6D incomplete** (downstream app wiring)

- **6E partial** (governance/SSOT updates not enforced)



## Phase 7 — Runtime Bring-Up + Governance (⚠ Partial)

- 7A–7F complete  

- 7G complete  

- Governance reconstruction → **not implemented**  

- Snapshot drift → unresolved  

- UX polish → partial



---



# 2. GOVERNANCE DRIFT (MERGED FROM PHASE-7 MAP)



## 2.1 Rules SSOT Drift

**As-designed:**  

- Rules exist in RULES_INDEX + AGENTS.md  

- Intended future SSOT: Postgres



**As-implemented:**  

- Operational SSOT = `.cursor/rules/*.mdc`  

- DB contains only telemetry, not rule definitions  

- Docs not enforced → desync possible



**Impact:**  

- Governance not driven by DB  

- Rules cannot be versioned / enforced centrally  

- CI lanes cannot query rule metadata



---



## 2.2 Control-Plane Drift

**As-designed:**  

- Control-plane = governance backbone  

- Stores agent runs, violations, compliance, MCP



**As-implemented:**  

- Control-plane migrations exist  

- CI boosts data into exports  

- DB currently offline during bring-up  

- Missing governance tables:

  - control.rule_definition

  - control.rule_source

  - control.tv_definition

  - control.tag_definition

  - control.tag_binding



**Impact:**  

- Cannot ingest rules into DB  

- Cannot generate `.cursor/rules` from DB  

- Cannot enforce TVs/Tags in DB  

- Cannot unify STRICT/HINT enforcement



---



## 2.3 AGENTS.md Drift

**As-designed:**  

- Defines DSN safety, OPS contract, DB contract  

- Intended as high-level governance anchor



**As-implemented:**  

- Docs updated but not enforced  

- DSN centralization incomplete in runtime  

- Downstream apps bypass Knowledge Slice (Phase-6D drift)



**Impact:**  

- Runtime breaks AGENTS contract  

- Governance cannot assume DSN correctness  

- Apps bypass guardrails



---



## 2.4 TVs/Tags Drift

**As-designed:**  

- TVs (E06–E10+) for extraction + LM health  

- STRICT/HINT lanes  

- Tag-lane governance



**As-implemented:**  

- TVs exist  

- Tag lanes exist (tagproof v0.0.3)  

- CI does not expose TV coverage or tag binding  

- No central registry in DB  

- No Atlas dashboard



**Impact:**  

- TVs/tags are not discoverable  

- Cannot enforce or visualize governance  

- Cannot complete Phase-7 bring-up



---



# 3. CROSS-PHASE BLOCKERS



## Blocker 1 — Phase-1 Control Plane Pending Items

- STRICT/HINT CI lanes  

- Tag-lane wiring  

- Atlas compliance linking  



**Effect:**  

Prevents strict governance enforcement system-wide.



---



## Blocker 2 — Phase-6D Downstream App Wiring Incomplete

- Apps still query Postgres directly  

- Violates DSN safety + Phase-1 contracts  

- Blocks governance schema changes  

- Blocks ingestion scripts  

- Blocks `.cursor/rules` generation



---



## Blocker 3 — Phase-7 Governance SSOT Migration Not Implemented

- DB missing governance tables  

- No ingestion of RULES_INDEX/AGENTS  

- `.cursor/rules` still de facto SSOT  

- No rule-versioning  

- No TVs/Tags registry



---



# 4. TRUE CRITICAL PATH (PHASES 1–7)



## Step 1 — Finish Phase-1 Control Plane tasks

- STRICT/HINT CI lanes  

- Tag-lane guard wiring  

- Atlas linkage  

**(Must land before DB governance)**



## Step 2 — Fix Phase-6D Downstream App Wiring

- Implement StoryMaker useKnowledgeSlice()  

- Implement BibleScholar KB client  

- Shared API/CLI wrapper  

**(Must land before ingestion scripts)**



## Step 3 — Execute Phase-7 Governance SSOT Migration

- Create governance tables  

- Implement ingestion  

- Implement rule generation (DB → .cursor/rules)  

- Implement tag registry  

- Enforce AGENTS contract  

- STRICT/HINT DB-backed enforcement



**Only after these 3 steps can Phase-7 be completed.**



---



# 5. GOVERNANCE RECONSTRUCTION PLAN (PHASE-7)



## 5.1 Governance DB Schema (to be created)

- control.rule_definition  

- control.rule_source  

- control.guard_definition  

- control.guard_violation  

- control.tv_definition  

- control.tag_definition  

- control.tag_binding  



## 5.2 Ingestion Scripts

- ingest_rules_to_control.py  

- ingest_tv_tags_to_control.py  

- generate_cursor_rules_from_control.py  



## 5.3 Enforcement Guards

- DB↔docs↔cursor alignment  

- TV/tag completeness  

- STRICT/HINT enforcement  



---



# 6. FINAL STATE (WHAT "DONE" LOOKS LIKE)



- `.cursor/rules` generated from DB  

- RULES_INDEX + AGENTS → ingested  

- Knowledge Slice wired into apps  

- STRICT/HINT lanes active in CI  

- Tag-lane governance operational  

- Atlas compliance dashboard live  

- Governance is SSOT in Postgres  

- Phase-7 bring-up passes all TVs & tags  

- Phase-6D and Phase-1 tasks complete  

