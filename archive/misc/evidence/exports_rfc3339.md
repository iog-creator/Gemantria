# RFC3339 timestamps ✅

**What this proves (for the orchestrator):** Checks that all timestamps look like 2025-11-09T10:15:00Z (standard format).

**Status:** GREEN

**Raw evidence:** `evidence/exports_rfc3339.verdict.json`

**Excerpt:**

```json
{
  "schema": "guard.exports-rfc3339.v1",
  "generated_at": "2025-11-09T05:21:56+00:00",
  "strict": false,
  "files": {
    "graph_latest.scored.json": {
      "exists": true,
      "has_generated_at": true,
      "rfc3339_ok": true,
      "error": null
    },
    "ai_nouns.json": {
      "exists": true,
      "has_generated_at": true,
      "rfc3339_ok": true,
      "error": null
    },
    "graph_stats.json": {
      "exists": true,
      "has_generated_at": true,
      "rfc3339_ok": true,
      "error": null
    },
    "graph_patterns.json": {
      "exists": true,
      "has_generated_at": true,
      "rfc3339_ok": true,
      "error": null
    }
  },
  "ok": true
}
```

_Definitions:_ **Tag** = frozen proof snapshot · **Badge** = visual pass/fail marker · **Verdict** = the JSON file that says pass/fail.
