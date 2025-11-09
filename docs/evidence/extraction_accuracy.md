# Extraction accuracy ✅

**What this proves (for the orchestrator):** Quick accuracy check on sample cases to ensure extractors still behave.

**Status:** GREEN

**Raw evidence:** `evidence/guard_extraction_accuracy.json`

**Excerpt:**

```json
{
  "schema": "guard.extraction-accuracy.v1",
  "generated_at": "2025-11-09T04:32:14Z",
  "mode": "STRICT",
  "source": {
    "mode": "file_first",
    "input": "exports/graph_latest.scored.json"
  },
  "fixture_missing": false,
  "ok": true,
  "totals": {
    "cases": 0,
    "correct": 0
  },
  "details": []
}
```

_Definitions:_ **Tag** = frozen proof snapshot · **Badge** = visual pass/fail marker · **Verdict** = the JSON file that says pass/fail.
