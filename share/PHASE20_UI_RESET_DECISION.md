# Phase 20 UI Reset Decision

**Decision:** Reset the Orchestrator Console UI layer and start fresh with v2.

## Context

Phase 20 formally reset the UI layer for the Orchestrator Console. The previous
shell-based approach was replaced with a new React+TypeScript application.

## Key Decisions

1. **New console v2 scaffold** at `webui/orchestrator-console-v2/`
2. **Three-pane layout**: left nav, conversation center, right status tiles
3. **Surface-driven architecture**: console reads from `share/` surfaces only
4. **Schema-governed**: `CONSOLE_SCHEMA.json` + `VIEW_MODEL.json` define all bindings

## Implementation

- Phase 20.2: Updated CONSOLE_SCHEMA.json and VIEW_MODEL.json
- Phase 20.3: Scaffolded console v2 React app
- Phase 20.6: Wired active prompts
- Phase 20.7: Applied styling

## Status

COMPLETE — Console v2 is the canonical orchestrator-facing UI.
