# AGENTS.md - webui/orchestrator-console-v2 Directory

## Directory Purpose

The `webui/orchestrator-console-v2/` directory contains the Orchestrator Console v2 React+TypeScript application, providing a kernel-aware dashboard for the Gemantria system.

## Key Components

### UI Components (src/components/)
- **App.tsx** - Root component with three-pane layout: LeftNav, ConversationPane, RightStatusPane
- **KernelHealthTile.tsx** (Phase 27.C) - Displays OA kernel state: branch/phase, reality_green badge, checks summary
- **OAWorkspacePanel.tsx** (Phase 27.C) - Displays OA workspace: active prompts, research index, decisions
- **RightStatusPane.tsx** - Status panel aggregating kernel health and system tiles
- **LeftNav.tsx** - Navigation sidebar with mode switching
- **ConversationPane.tsx** - Central pane for conversation context

### Data Layer (src/data/)
- **tileLoaders.ts** - Functions to load tile data from share/ surfaces
- **types.ts** - TypeScript interfaces for OAStateData, OAWorkspaceData, TileDataBundle
- **conversationContext.ts** - Loads conversation prompts from OA/orchestrator surfaces
- **loadData.ts** - Low-level JSON/text loaders

### Model Layer (src/model/)
- **consoleConfig.ts** - Types and loaders for CONSOLE_SCHEMA.json and VIEW_MODEL.json

## Data Sources (from VIEW_MODEL.json)

| Key | Path | Purpose |
|-----|------|---------|
| oa_state | share/orchestrator_assistant/STATE.json | OA kernel snapshot |
| ssot_surface | share/SSOT_SURFACE_V17.json | SSOT phase info |
| kb_registry | share/kb_registry.json | KB document registry |
| oa_prompts | share/orchestrator_assistant/ACTIVE_PROMPTS.md | OA focus |

## Development Guidelines

- Console v2 is a **read-only consumer** of kernel surfaces
- No new truth sources; all data flows from share/
- Use typed interfaces from types.ts for data handling
- Run `npm run build` before committing to verify TypeScript compilation

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
| Kernel wiring | Phase 27.B/C OA kernel snapshot |
| View model binding | Phase 20.4 data wiring |
