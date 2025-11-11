# SENTINELS — What We Already Use (How to Run Them)

This project already uses **sentinels** to prevent drift:

## 1) DSN centralization (STRICT on tags)

- Script: `scripts/ci/guard_dsn_centralized.py`

- Local (HINT): `make guard.dsn.centralized`

- Tags (STRICT): enforced by `.github/workflows/dsn-guard-tags.yml`

## 2) Tagproof core export (RO DSN, tags only)

- Exporter: `scripts/exports/export_graph_core.py` (RO-on-tag policy)

- Workflow: `.github/workflows/tagproof-core-export.yml` (runs export + schema guard)

- Provide one of: `GEMATRIA_RO_DSN` **or** `ATLAS_DSN_RO`

## 3) Master Reference tracking

- Runner: `scripts/ops/master_ref_populate.py`

- Make targets: `docs.masterref.populate`, `docs.masterref.check`, `housekeeping.masterref`

## 4) SSOT Prompt & Always-Apply triad

- SSOT prompt: `docs/SSOT/GPT_SYSTEM_PROMPT.md`

- Triad refs: `AGENTS.md` and `RULES_INDEX.md` (050/051/052)

## 5) Atlas (browser hub / web UI)

- Either `docs/atlas/index.html` **or** `webui/graph`/**ui` exists to support the operator browser flow.

> **Operator TL;DR**

> - For local checks: `make guard.dsn.centralized` (HINT)

> - For release tags: DSN guard STRICT + tagproof export run automatically in CI

> - Add `GEMATRIA_RO_DSN` **or** `ATLAS_DSN_RO` repo secret for tagproof

