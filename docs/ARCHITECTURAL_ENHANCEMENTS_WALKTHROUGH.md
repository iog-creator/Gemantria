# Architectural Enhancements Walkthrough (Pre-Phase 13)

**Date:** 2025-11-26
**Status:** Complete

This document details the architectural enhancements implemented to harden the system before Phase 13 (Multi-language Support).

## Enhancement A: Schema-to-Docsite Automation

**Goal:** Enforce Rule 027 (Docs Sync Gate) by automatically generating documentation from SSOT JSON schemas.

### Implementation
- **Generator Script:** `scripts/generate_schema_docs.py` scans `docs/SSOT/*.schema.json` and generates `docs/SSOT/auto_schema_output.md`.
- **Governance Hook:** Patched `scripts/governance_housekeeping.py` to run the generator before artifact updates.
- **Registry Tracking:** Added `docs/SSOT/auto_schema_output.md` to `scripts/governance_tracker.py` to ensure it's tracked in the DMS.

### Verification
- Run `make housekeeping` -> Generates `docs/SSOT/auto_schema_output.md`.
- Run `pmagent kb registry list` -> Shows the file as tracked (status: unreviewed).

## Enhancement B: Tool-Driven Database Access

**Goal:** Enforce the BibleScholar Rule ("All biblical answers must come from `bible_db`") by providing structured LLM tools.

### Implementation
- **Tool Updates:** Modified `agentpm/tools/bible.py` to include:
  - `search_bible_verses(query, translation, limit)`
  - `lookup_lexicon_entry(strongs_id)`
- **Exports:** Updated `agentpm/tools/__init__.py` to export these tools.
- **Underlying Flows:** Wraps `agentpm.biblescholar.search_flow` and `agentpm.biblescholar.lexicon_flow`.

### Usage
LLMs can now call these tools to retrieve grounded data instead of generating it.

```python
from agentpm.tools import search_bible_verses, lookup_lexicon_entry

# Search
results = search_bible_verses("grace", limit=5)

# Lexicon
entry = lookup_lexicon_entry("H2617")
```

## Next Steps
- Proceed to Phase 13: Multi-language Support.
