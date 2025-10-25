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

## Notes

* Deterministic and fast; suited for PR evidence.
* Do **not** wire into CI until stabilized.
* Governance: 037/038 unchanged; share drift remains read-only in CI.
