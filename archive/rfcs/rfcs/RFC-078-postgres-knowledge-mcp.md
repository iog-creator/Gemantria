# RFC-078: Postgres Knowledge MCP (Catalog-as-a-Service, DSN-first)

- **Author:** PM (GPT-5 Thinking)

- **Date:** 2025-11-11

- **Status:** Proposed

- **Related:** Rule-050/051/052, Rule-067, ADR-065 (Postgres SSOT), AGENTS.md (MCP/DSN), tagproof STRICT lane

## Summary

Define a **Postgres-backed Knowledge MCP** that exposes a curated **tool/catalog** for agents via DB views/APIs. Goal: **fewer choices, faster routing, deterministic evidence**, with RO-by-default on tags and STRICT gating.

## Motivation

Today, catalog knowledge is file-scattered. A DB-first MCP reduces "possibility overload," centralizes costs/limits/visibility, and enables **Atlas proofs** (counts, endpoints) and **guard_mcp_catalog_strict** to enforce contracts.

## Proposal

1) **Schema (RO-friendly)**  

   - `mcp.tools(name text primary key, desc text, tags text[], cost_est real, visibility text)`  

   - `mcp.endpoints(name text primary key, path text, method text, auth text, notes text)`  

   - `mcp.logs(ts timestamptz, agent text, action text, target text, ok bool)` (RW guarded; omit in STRICT RO)

2) **Views/Policies**  

   - `mcp.v_catalog` (JOINed, read-only) for CI/tagproof  

   - Row-level policies: RO on tags (STRICT); RW permitted locally behind `ENFORCE_STRICT=0`

3) **Adapters**  

   - Python: `scripts/mcp/catalog.py` using centralized DSN loaders only  

   - UI: Atlas "MCP Catalog" panel (counts + endpoints) wired to DB RO view

4) **Guards**  

   - Extend `guard_mcp_catalog_strict.py` to validate schema, counts, and "no write verbs" invariant

5) **Runbooks**  

   - `docs/runbooks/MCP_KNOWLEDGE_DB.md` (bring-up, RO vs RW, DSN proof lines)

## Scope

- In-scope: schema, adapters, guards, runbooks, Atlas proof surfaces

- Out-of-scope (this RFC): pipeline algorithm changes; LM Studio model swaps

## Acceptance Criteria

- [ ] Tagproof STRICT passes with **DB RO-only** (no writes); guard validates `mcp.v_catalog`

- [ ] Atlas MCP panel shows endpoints >= 3 with screenshots in `share/releases/*/webproof/`

- [ ] AGENTS.md updated: catalog routing steps + DSN loader usage (no `os.getenv` direct)

- [ ] `scripts.config.env` exposes `get_mcp_ro_dsn()` or reuse `get_ro_dsn()` equivalence

- [ ] Runbook added: `MCP_KNOWLEDGE_DB.md` with redacted DSN proof lines

- [ ] CI adds non-fatal HINT on main; STRICT on tags (fail-closed)

## QA Checklist

- [ ] ruff green; guards all green

- [ ] DSNs redacted in logs/artifacts

- [ ] No outbound network in CI; hermetic proofs only

- [ ] Evidence bundle includes `guard_mcp_catalog.*.json` + Atlas screenshots

## Links

- AGENTS.md (triad + DSN centralization)

- RULES_INDEX.md (Rule-067; atlas webproof)

- tagproof.yml (STRICT_WEBPROOF + DSN secrets)

