# Pipeline Smoke (Phase-2, v6.2.3)

Run locally (no DB required):

```
MOCK_AI=1 PIPELINE_SEED=4242 make pipeline.smoke
```

Expected envelopes (examples):

- `extract.nouns.done` items≥3
- `compute.gematria.done` items match previous
- `aggregate.done` with `even`/`odd` counts
- `HINT[pipeline.seed]: 4242` present in envelopes
