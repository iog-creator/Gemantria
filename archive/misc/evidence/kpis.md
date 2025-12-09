# KPIs

[← Back to Atlas](../atlas/index.html)

**What this shows:** Key performance indicators

**Status:** LIVE (populated from database)

**Data excerpt:**

```json
{
  "active_runs": 141,
  "errors_24h": 0,
  "top_slowest": [
    {
      "node": "collect_nouns",
      "p90_ms": 103000.02290000003
    },
    {
      "node": "enrichment",
      "p90_ms": 11614.312
    },
    {
      "node": "planner",
      "p90_ms": 3782.5059999999994
    },
    {
      "node": "network_aggregator",
      "p90_ms": 2472.876000000001
    },
    {
      "node": "analysis_runner",
      "p90_ms": 54.97200000000001
    }
  ]
}
```

_Definitions:_ **PR** = proposal to merge change (fast checks) · **Tag** = frozen proof snapshot · **Badge** = visual pass/fail marker · **Verdict** = JSON pass/fail.