# Feature Reunion & Repo Deprecation Backlog — Planning Doc

**Status:** Planning  
**Canonical Doc:** `docs/SSOT/FEATURE_REUNION_BACKLOG.md`  
**Date:** 2025-01-27

## 1. Mission

Identify existing but orphaned or under-integrated features in the Gemantria repository
and either:

- Bring them explicitly into the v2 architecture (feature reunion), or
- Quarantine them into `deprecated_archive/` when truly dead.

This backlog is informed by:

- Layer 4 code ingestion artifacts:
  - `share/code_fragments_classified.json`
  - `share/code_fragments_embedded.json`
- The Feature Catalog:
  - `evidence/repo_cleanup/feature_catalog_by_dir.json`
- SSOT docs and audits:
  - `MASTER_PLAN.md`, `LAYER4_CODE_INGESTION_PLAN.md`
  - Gemini/Governance analyses of legacy stacks.

No code is moved based on this document alone; this is a planning backlog.

## 2. Current Code Distribution (from Feature Catalog)

Source: `evidence/repo_cleanup/feature_catalog_by_dir.json` (3,749 fragments)

High-level distribution:

- `agentpm/` — core agent + PM framework (~38.6% of fragments)
- `scripts/` — operational scripts (~35.5%)
- `tests/` — test code (~14.6%)
- `src/` — additional source modules (~7.4%)
- `pmagent/` — pmagent CLI code (~1.6%)
- `tools/`, `archive/`, `genai-toolbox/`, `conftest.py`, `~` — smaller buckets

These buckets will be used to group candidates into:

- Integration candidates,
- Quarantine candidates,
- Needs-investigation items.

## 3. Integration Candidates (Draft Buckets)

These are code areas likely to contain valuable features to bring into the v2 architecture.

### 3.1 agentpm/

Role: Core orchestration and agent framework.

Backlog (examples, to be filled via further analysis):

- [ ] Catalog legacy or unused agents and determine which should be revived or removed.
- [ ] Identify any partial implementations of flows (e.g., unfinished orchestration logic) that should be completed under current phases.

### 3.2 scripts/

Role: Operational and governance scripts (ingestion, guards, ops tools).

Backlog:

- [ ] Identify scripts implementing legacy web/MCP or legacy pipelines that could be generalized or integrated into pmagent commands.
- [ ] Classify scripts into:
  - SSOT-backed ops,
  - Legacy helpers,
  - One-off experiments (likely quarantine candidates).

### 3.3 src/

Role: Additional source modules, potentially including legacy or alternate implementations (e.g., old UI flows, legacy math or language utilities).

Backlog:

- [ ] Enumerate modules under `src/` using DMS/doc_registry.
- [ ] Tag each module as:
  - Core architecture extension,
  - Legacy feature candidate (to be ported),
  - Quarantine candidate.

## 4. Quarantine Candidates (Draft Buckets)

These are areas likely to be truly legacy/deprecated once confirmed.

### 4.1 archive/

- Contains old test code and legacy support files (per prior audits).
- Expected action:
  - [ ] Confirm via DMS and feature catalog that `archive/` content is not referenced by current SSOT.
  - [ ] Move confirmed-dead content into `deprecated_archive/<date>/` via hygiene PR.

### 4.2 Misc Small Buckets

- `genai-toolbox/` — external dependency; generate Ruff exclusions, not moves.
- `conftest.py` at root — test harness; ensure it's properly associated with `tests/`.
- `~` (tilde) path entries — likely path parsing artifacts; investigate and correct.

Backlog:

- [ ] Verify which of these are real files vs path issues.
- [ ] Decide for each whether to:
  - Fix paths / config,
  - Quarantine,
  - Ignore as external.

## 5. Needs Investigation (Feature Reunion Focus)

This section will be populated as we cross-reference:

- Gemini's list of legacy but valuable features (e.g., old Flask/Jinja UI, MCP servers),
- DMS `doc_registry` and code fragments,
- Phase docs (especially Phase 14 and future phases 12–15).

Backlog:

- [ ] For each legacy feature Gemini identified (e.g., old web UI, MCP server), locate its code via DMS/code fragments and record:
  - repo_path,
  - current status (wired vs orphan),
  - potential target phase/layer for integration.
- [ ] Create dedicated SSOT docs or phase extensions for any features we decide to resurrect.

## 6. Relationship to Repo Deprecation Policy

This backlog works alongside `REPO_DEPRECATION_POLICY.md`:

- The Policy defines HOW quarantine must be done.
- This Backlog defines WHICH features should be:
  - Integrated,
  - Quarantined,
  - Investigated.

No quarantine PRs should proceed until both:

- Policy is agreed upon, and
- This backlog has identified the specific targets.

## 7. Next Steps

- [ ] Expand this backlog with concrete items based on:
  - Detailed inspection of `agentpm/`, `scripts/`, `src/`, and `archive/`,
  - DMS/code fragment queries,
  - Gemini's orphan-feature list.
- [ ] Register this document in DMS and export to `share/`.
- [ ] Use this backlog to seed NEXT_STEPS and planning lanes for:
  - Feature reunion PRs,
  - Repo hygiene/quarantine PRs.

