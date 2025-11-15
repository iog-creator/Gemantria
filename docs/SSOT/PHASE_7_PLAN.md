# Phase-7 — Apps & Knowledge OS

**Status**: PLANNING (v0 stub)  
**Scope**: Turn infrastructure from Phases 1–6 into usable apps with pleasant, non-technical UX  
**Upstream Dependencies**: Phase-6 core complete (6A, 6B, 6C, 6J, 6M, 6O, 6P)

## Purpose

- Turn infrastructure from Phases 1–6 into usable apps:
  * BibleScholar
  * StoryMaker / World Bible
  * PM/OPS views
- Provide a pleasant, non-technical UX for interacting with:
  * BibleScholar reference slice (Phase-6P)
  * Knowledge slice exports
  * LM observability signals

## Scope (v0 stub)

### BibleScholar

Surface the reference slice in a CLI or simple UI, with:
- Answer + "how I built this" trace
- Ability to inspect context_used (verses, Gematria, docs)
- Simple question-answer interface

### StoryMaker

Define an analogous "reference slice" for narrative flows (planning only; implementation later).

### PM/OPS

Add at least one simple dashboard or view for:
- LM indicators (from Phase-4 exports)
- Knowledge slice inventory (what docs are available)
- Control-plane compliance metrics

## Dependencies

- Phase-1 control plane, guarded tool calls
- Phase-4 LM indicator exports
- Phase-6 DB + Gematria + similarity + reference slice

## Out-of-scope (for Phase-7 v0)

- Full production web UI
- Complex editor environments
- Multi-user authentication
- Real-time collaboration

## Next Steps

- Define concrete sub-episodes (E- numbers) for:
  * BibleScholar UX surfacing
  * StoryMaker reference slice design
  * Simple LM/knowledge dashboards
- Create detailed implementation plan with PR staging

