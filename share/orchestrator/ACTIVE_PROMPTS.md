# Orchestrator Active Prompts

## High Priority

- Ensure pmagent, hints, envelopes, and DMS are using the **new share surfaces** exclusively.
- Validate Orchestrator Console v2 wiring via `make stress.smoke` and `python scripts/pm/check_console_v2.py`.

## Medium Priority

- Expand tool-calling scenarios for tiny models, ensuring they pick the right tools (pmagent, guards, exporters).
- Harden backup-before-housekeeping guard.

## Low Priority

- Refine console v2 styling and layout as needed.
- Add richer summaries to phase docs (18–23).
