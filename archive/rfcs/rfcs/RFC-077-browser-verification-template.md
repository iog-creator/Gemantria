# RFC-077: Mandatory Browser Verification Template (Rule-051 + Rule-067)

- **Author:** PM (GPT-5 Thinking)

- **Date:** 2025-11-11

- **Status:** Proposed (fast-track evidence-first)

- **Related:** Rule-051 (Cursor Insight), Rule-062 (Env), Rule-067 (Atlas Webproof), GPT_SYSTEM_PROMPT.md

## Summary

Standardize and mandate a **Browser Verification** section in every OPS block when visual/web artifacts are touched. This prevents missed UI checks and aligns local OPS with CI tagproof.

## Motivation

We observed regressions (e.g., Mermaid error banners) when browser verification was optional or ad-hoc. A canonical template ensures consistent checks and evidence.

## Proposal

1. Replace the existing Browser Verification prose in `docs/SSOT/GPT_SYSTEM_PROMPT.md` with a **MANDATORY TEMPLATE** containing:

   - When to apply (conditions list)

   - Rule refs: 051/062/067

   - Local server start, navigation, screenshots

   - Webproof hook (STRICT_WEBPROOF=1)

   - Evidence placeholders `[[IMAGE]]`

2. Mark Rule-067 as Always-Apply for `docs/atlas/*` edits in `RULES_INDEX.md`.

## Acceptance Criteria

- `GPT_SYSTEM_PROMPT.md` includes the **BROWSER VERIFICATION (Rule-051 + Rule-067) — MANDATORY TEMPLATE** section verbatim.

- Grep proofs show the header and key commands are present.

- `atlas_webproof.sh` executes cleanly; screenshots generated.

- Viewer + MCP guards remain green.

## QA Checklist

- [ ] Prompt guard passes (sections detected)

- [ ] Webproof green, no Mermaid error banners

- [ ] CI tagproof references STRICT_WEBPROOF

- [ ] Evidence images printed via `[[IMAGE]]` lines

