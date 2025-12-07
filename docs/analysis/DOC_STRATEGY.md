# DOC_STRATEGY.md — Gemantria Documentation Strategy & pmagent Control-Plane DMS

This document defines the three-layer model for documentation governance in Gemantria:
AGENTS.md (narrative SSOT), pmagent control-plane DMS (structured metadata SSOT), and filesystem (implementation detail).

## Architecture Clarification

pmagent is the governance and control-plane engine for the Gemantria project.
All documentation lifecycle, classification, metadata, and structural enforcement
are handled by pmagent's control-plane DMS (`control.doc_registry`).
Gemantria is the domain project being governed, not the system performing
the governance. AGENTS.md surfaces define the agent-facing worldview of both
Gemantria and pmagent; the pmagent control-plane DMS records that worldview in structured form.

## Three-Layer Model

### Layer 1: AGENTS.md (Narrative SSOT)

**Purpose:** Human and AI agent-readable maps of agents, tools, workflows, and key documentation surfaces.

**Hierarchy:**
- Root `AGENTS.md` is the **global agent registry** (`CANONICAL_GLOBAL`) and must never be archived or demoted.
- Subsystem-level `AGENTS.md` files (e.g., `pmagent/AGENTS.md`, `docs/AGENTS.md`) are local views that inherit from the global registry.

**Privileges:**
- Root `AGENTS.md`: `importance = 'critical'`, `enabled = true`, tags include `ssot`, `agent_framework`, `agent_framework_index`.
- Other `AGENTS.md`: `importance >= 'high'`, `enabled = true`, tags include `ssot`, `agent_framework`.
- No automated process may archive, disable, or downgrade AGENTS.md files.

**Truth Model:** AGENTS.md defines the semantic worldview; it is the narrative SSOT that describes what exists and how it works.

### Layer 2: pmagent control-plane DMS (Structured Metadata SSOT)

**Purpose:** Structured inventory and lifecycle metadata stored in Postgres `control.doc_registry`.

**Responsibilities:**
- Tracks which docs exist (`logical_name`, `repo_path`, `share_path`).
- Manages lifecycle (`enabled`, archive status).
- Stores metadata (`importance`, `tags`, `owner_component`).
- Provides structured queries for automation and analytics.

**Relationship to AGENTS.md:**
- The pmagent control-plane DMS **records and enforces** the semantics defined by AGENTS.md.
- DMS must reflect (not override) AGENTS.md definitions.
- DMS can only upgrade AGENTS metadata (unknown → low → medium → high → critical), never downgrade.

**Truth Model:** The pmagent control-plane DMS is the structured SSOT **after** AGENTS.md defines semantics. It provides machine-readable metadata for automation, but AGENTS.md remains the authoritative narrative.

### Layer 3: Filesystem (Implementation Detail)

**Purpose:** Where files actually live on disk.

**Relationship to DMS:**
- Filesystem locations must match `control.doc_registry.repo_path`.
- Filesystem is an implementation detail that must be kept in sync with the registry.
- If pmagent control-plane DMS and filesystem disagree, pmagent control-plane DMS is correct (filesystem should be updated to match).

**Truth Model:** The filesystem is the physical storage layer; it has no independent truth authority.

## SSOT Hierarchy Summary

```
1. AGENTS.md (human + AI agent worldview)
   ↓
2. pmagent control-plane DMS (control.doc_registry)
   ↓
3. Filesystem (repo structure)
```

**Key Principle:** AGENTS.md defines the world; the pmagent control-plane DMS records and enforces that definition; the filesystem implements it.

## pmagent's Role as Governance Engine

**pmagent responsibilities:**
- Populates the control-plane DMS via `scripts/governance/ingest_docs_to_db.py`.
- Enforces lifecycle rules (archive, cleanup, metadata updates).
- Validates alignment between AGENTS.md, pmagent control-plane DMS, and filesystem via guards.
- Provides structured queries and analytics over documentation metadata.

**Gemantria's role:**
- Gemantria is the **governed domain project**.
- Gemantria provides the documentation content (AGENTS.md, SSOT docs, runbooks, etc.).
- Gemantria's structure is **described** by AGENTS.md and **tracked** by pmagent's control-plane DMS.

**Boundary clarity:**
- pmagent = governance engine (control-plane, DMS, guards, automation).
- Gemantria = governed project (domain content, documentation, codebase).
- AGENTS.md = interface between product (Gemantria) and governance (pmagent).

## Enforcement & Guards

**Guard responsibilities (`scripts/guards/guard_reality_green.py`):**
- Verify AGENTS–pmagent control-plane DMS alignment.
- Check that AGENTS.md rows in DMS satisfy contract (importance, enabled, tags, no archive).
- Validate DMS lifecycle invariants.
- Ensure filesystem matches DMS `repo_path` values.

**Reality Green behavior:**
- STRICT mode: Fail if AGENTS rows are misclassified, disabled, or archived.
- STRICT mode: Fail if pmagent control-plane DMS and filesystem disagree on AGENTS presence.
- HINT mode: Report violations but allow continuation (for development/CI).

## Related Documents

- `docs/SSOT/DOC_STRATEGY.md` — Detailed lifecycle rules and archive policy.
- `AGENTS.md` (root) — Global agent registry and doc strategy overview.
- `pmagent/AGENTS.md` — pmagent package documentation and control-plane architecture.

This strategy ensures that pmagent (governance engine) and Gemantria (governed project) maintain clear boundaries, with AGENTS.md as the interface and pmagent control-plane DMS as the structured enforcement layer.
