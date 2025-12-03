# AGENTS.md - pmagent/guarded Directory

## Directory Purpose

The `pmagent/guarded/` directory contains guarded components for the Gematria analysis pipeline.

## Key Components

### `autopilot_adapter.py`

**Purpose:** Guarded Tool Adapter for Autopilot Phase C. Maps Autopilot intents to safe pmagent commands using a strict whitelist approach.

**Key Function:**
- `map_intent_to_command(intent: str) -> str | None`: Maps an intent to a safe pmagent command, or returns None for unknown intents.

**Whitelist Mappings:**
- `"status"` → `"pmagent status explain"`
- `"health"` → `"pmagent health system"`
- `"plan"` → `"pmagent plan next"`

**Safety:**
- Only whitelisted intents are allowed
- Unknown intents return None (rejected)
- Case-insensitive matching
- Whitespace is stripped

## API Contracts

<!-- Add function/class signatures and contracts here -->

## Testing Strategy

<!-- Add testing approach and coverage requirements here -->

## Development Guidelines

<!-- Add coding standards and patterns specific to this directory here -->

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
<!-- Add ADR references here -->
