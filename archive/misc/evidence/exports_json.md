# Exports JSON ✅

**What this proves (for the orchestrator):** Checks that our exported JSON files are well-formed and complete.

**Status:** GREEN

**Raw evidence:** `evidence/exports_guard.verdict.json`

**Excerpt:**

```json
{
  "schema": "guard.exports-json.v1",
  "generated_at": "2025-11-09T05:21:55Z",
  "strict": false,
  "files": {
    "graph_latest.scored.json": {
      "exists": true,
      "json_ok": true,
      "schema_ok": true,
      "error": null
    },
    "ai_nouns.json": {
      "exists": true,
      "json_ok": true,
      "schema_ok": true,
      "error": null
    },
    "graph_stats.json": {
      "exists": true,
      "json_ok": true,
      "schema_ok": true,
      "error": null
    },
    "graph_patterns.json": {
      "exists": true,
      "json_ok": true,
      "schema_ok": true,
      "error": null
    }
  },
  "ok": true
}
```

_Definitions:_ **Tag** = frozen proof snapshot · **Badge** = visual pass/fail marker · **Verdict** = the JSON file that says pass/fail.
