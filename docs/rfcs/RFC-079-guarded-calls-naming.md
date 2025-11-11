# RFC-079: Guarded Tool Calls — Naming & Idempotent Migrations (P0)

- **Author:** PM (GPT-5 Thinking)

- **Date:** 2025-11-12

- **Status:** Proposed (fast-track; evidence-first)

- **Related:** RFC-078 (MCP Knowledge DB), Rule-050/051/052, Rule-062

## Summary

Standardize names and make migrations idempotent for the Guarded Tool Calls P0 scaffold:

- **DB tables (prefix):** `mcp_` (e.g., `mcp_tool_catalog`, `mcp_agent_run`)

- **MVs (prefix):** `mv_mcp_` (e.g., `mv_mcp_compliance_7d`)

- **Columns:** `created_at`, `updated_at` (WHERE applicable); `status` not `state`

- **JSON Schema `$id`:** `gemantria://v1/<domain>/...` with `title` set; `additionalProperties: false` at top-level

## Motivation

Consistent names reduce surprises and drift between docs, guards, and adapters. Idempotent migrations protect re-runs and mixed states in dev/CI.

## Proposal

1. Add an idempotent migration that **renames** legacy P0 tables/MVs to standardized names if needed and **adds** missing columns w/ `IF NOT EXISTS`.

2. Normalize JSON Schema `$id` to a canonical `gemantria://v1/...` prefix and add missing `title` fields.

3. Add a **schema-naming guard** and Makefile hook.

## Acceptance Criteria

- Guard script passes on the repo: all `$id` patterns match, titles exist, top-level `additionalProperties` set.

- SQL migration is re-runnable without error.

- Greps show standardized names present.

## QA Checklist

- [ ] Ruff green

- [ ] Guard passes locally (no DB access required)

- [ ] PR includes evidence bundle
