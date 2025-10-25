# Phase-8 Eval (Local Manifest → Report)

Local-only evaluation flow. No CI gates or `make go` changes.

## Usage
1. Edit tasks in `eval/manifest.yml`
2. Run:
   ```bash
   make eval.report
```

3. Artifacts:

   * `share/eval/report.json`
   * `share/eval/report.md`

### Temporal history (local-only)
Run:
```bash
make eval.history
```

Artifacts:

* `share/eval/history.json` — per-export metrics + summary
* `share/eval/history.md` — human-readable trend table and OK badge

Notes:

* Files matched: `exports/graph_*.json`
* Sorting prefers timestamp in filename; minimal fallback
* Checks: nonzero nodes/edges, strength fraction in [0.30, 0.95] ≥ 0.70, embedding_dim==1024 when present

## Notes

* Deterministic and fast; suited for PR evidence.
* Do **not** wire into CI until stabilized.
* Governance: 037/038 unchanged; share drift remains read-only in CI.
