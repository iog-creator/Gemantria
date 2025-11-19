# RFC-072: Document Management System & Extraction Agents SSOT

- **Author:** PM (via Cursor)
- **Date:** 2025-11-11
- **Status:** Accepted (Fast-Track, evidence-first)
- **Scope:** Cross-cutting infra (governance/docs SSOT) + Agent contracts (discovery/enrichment/extraction)

## Summary

Define a browser-first, guarded Document Management System (DMS) that treats docs as an SSOT surface (mirrored via `share/`), and formalize Extraction Agents handoffs so ai-nouns → enrichment → graph are schema-verified and evidence-linked.

## Motivation

We have strong schemas/guards, but the document system and extraction agents are uneven. This RFC standardizes:

- Docs SSOT navigation & guard hookups (governance.smoke awareness)
- Evidence pages & Atlas backlinks for operator UX
- Agent prompts + make targets as first-class, schema-verified handoffs

## Proposal

1. **DMS (Docs SSOT):**

   - Canonical index under `docs/SSOT/` + browser hub (`docs/atlas/index.html`) with evidence backlinks.
   - Guard: add prompt-format guard to `governance.smoke`; ensure `share.sync` mirrors curated docs (per `SHARE_MANIFEST.json`).
   - Add "Docs Presence" smoke: verify key SSOT docs exist and render (HINT on PRs; STRICT on tags).

2. **Extraction Agents (SSOT):**

   - Lock system+task prompts and outputs for `ai.nouns`, `ai.enrich`, `graph.build`.
   - Require JSON Schema passes for ai-nouns.v1, graph.v1 on every PR touching agents.
   - Emit per-stage evidence summaries (counts, refs) and COMPASS-friendly metrics.

3. **Posture:**

   - HINT-by-default; STRICT on tags behind repo vars.
   - No new secrets; DSN redacted in all evidence.

## Alternatives Considered

- Ad-hoc docs pages (drift risk)
- Agents without schema guards (breaks determinism)

## Acceptance Criteria

- `governance.smoke` runs the prompt-format guard.
- `share.sync` includes SSOT docs; no share drift.
- `guards.all` covers ai-nouns.v1 + graph.v1 on PRs that touch agents (HINT on PRs; STRICT on tags).
- Atlas pages contain backlink proof index; evidence pages present.

## QA Checklist

- [ ] ruff green
- [ ] guards.all green (HINT) on PR
- [ ] governance.smoke includes prompt-format guard
- [ ] Docs hub opens in Cursor Browser and shows Atlas/evidence links

## Links

- `AGENTS.md` (3-role DB contract, agent entries)
- `env_example.txt` (DSN knobs; HINT/STRICT flags)
- `SHARE_MANIFEST.json` (docs mirroring)
- Schemas: ai-nouns.v1, graph.v1, graph-stats, graph-patterns
