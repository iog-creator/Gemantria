# Rerank Calibration — Local Smoke

Run advanced calibration to verify rerank blend contracts:

```bash
make eval.graph.calibrate.adv
```

Acceptance:

* `share/eval/calibration_adv.json` created/updated
* Edge strength = α*cosine + (1-α)*rerank_score (α=0.5 default)
* Blend tolerance < 0.005 (configurable via BLEND_TOL)
* No unhandled exceptions

Notes:

* Local-only; CI runs hermetic validation without network
* Artifacts uploaded as CI artifacts (no share writes)
* Rule-045 enforces SSOT blend contract validation
