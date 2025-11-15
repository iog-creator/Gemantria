# Knowledge Base Widget Contract (SSOT)

Canonical machine signal: `share/atlas/control_plane/kb_docs.head.json`

## Contract (props)

- docs: array of KB document items
  - id: string (UUID)
  - title: string
  - section: string (category, e.g., "general", "bible")
  - slug: string (URL-friendly identifier)
  - tags: array of strings
  - preview: string (first ~200 chars of content)
  - created_at: timestamp (ISO-8601)

- db_off: boolean (true if DB unavailable)

- ok: boolean (true if export succeeded)

- error: string|null (error message if export failed)

- generated_at: timestamp (ISO-8601)

- source: object
  - path: string (path to kb_docs.head.json)

## Adapter Rules

- Hermetic (file only, no DB calls)

- Fail-closed (offline-safe if missing/invalid)

- Read-only (downstream apps must not write to KB)

- File-based (no direct Postgres access from downstream apps)

## Usage

Downstream apps (StoryMaker, BibleScholar) should:

1. Use `agentpm.knowledge.adapter.load_kb_docs_widget_props()` to load KB docs
2. Handle `db_off: true` gracefully (show empty state or cached data)
3. Never query Postgres directly - all KB access goes through Gemantria exports

## Example

```python
from agentpm.knowledge.adapter import load_kb_docs_widget_props

props = load_kb_docs_widget_props()
if props["db_off"]:
    # Handle offline mode
    docs = []
else:
    docs = props["docs"]
    # Render docs in UI
```

