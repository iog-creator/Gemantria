# NEXT_STEPS — Phase-9 Advanced Calibration + Quality Trend (Active v1)

## References (REQUIRED)
- **Rules cited:** 039-execution-contract; 040-ci-triage; 041-pr-merge-policy
- **Agents referenced:** AGENTS.md#orchestrator; AGENTS.md#cursor
- **Docs touched:** scripts/eval/calibrate_advanced.py; scripts/eval/quality_trend.py; Makefile; share/eval/*
- **SSOT links:** docs/SSOT/RULES_INDEX.md; docs/SSOT/MASTER_PLAN.md

## Scope (only these files change)
- scripts/eval/calibrate_advanced.py
- scripts/eval/quality_trend.py
- Makefile (add eval targets)
- share/eval/calibration_adv.json
- share/eval/quality_history.jsonl
- share/eval/badges/quality_trend.svg

## Emitted Hints (REQUIRED)
- HINT lines this run will emit:
  - HINT: eval: running advanced calibration
  - HINT: eval: writing quality trend badge

## Steps
- [ ] Create advanced calibration script
      Evidence: `python scripts/eval/calibrate_advanced.py`
- [ ] Create quality trend analysis script
      Evidence: `python scripts/eval/quality_trend.py`
- [ ] Add Makefile targets for eval package
      Evidence: `make eval.graph.calibrate.adv eval.quality.trend`
- [ ] Generate initial calibration data
      Evidence: `make eval.package` creates share/eval/calibration_adv.json
- [ ] Verify HINT emissions in CI logs
      Evidence: grep "HINT: eval:" in CI output

## Failure Policy
- If a command fails: paste last 40 lines; STOP.

## Merge Sequence
- [ ] PR-025: feature/phase9-advanced-calibration-quality-trend-025
      Evidence: `gh pr checks 25 --watch --interval 20`
