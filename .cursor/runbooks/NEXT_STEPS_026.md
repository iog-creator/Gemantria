# NEXT_STEPS — Edge audit & anomaly badges (026) (Active v1)

## References (REQUIRED)
- **Rules cited:** 039-execution-contract; 040-ci-triage-playbook; 041-pr-merge-policy
- **Agents referenced:** AGENTS.md#orchestrator; AGENTS.md#cursor
- **Docs touched:** scripts/eval/edge_audit.py; scripts/eval/anomaly_badge.py; Makefile; share/eval/*
- **SSOT links:** docs/SSOT/RULES_INDEX.md; docs/SSOT/MASTER_PLAN.md; docs/SSOT/REFERENCES.md

## Emitted Hints (REQUIRED)
- HINT: eval: auditing edges for anomalies
- HINT: eval: writing anomaly badge

## Scope (only these files change)
- scripts/eval/edge_audit.py (new)
- scripts/eval/anomaly_badge.py (new)
- Makefile (add eval.edge.audit, eval.anomaly.badge; wire into eval.package)
- share/eval/ outputs: edge_audit.json, badges/anomaly.svg
- .cursor/runbooks/NEXT_STEPS_026.md (this file)

## Steps
- [ ] Create scripts/eval/edge_audit.py (detect outliers by edge_strength z-score + IQR; produce share/eval/edge_audit.json)
      Evidence: `python3 scripts/eval/edge_audit.py && ls -l share/eval/edge_audit.json`
- [ ] Create scripts/eval/anomaly_badge.py (badge showing anomalous edge count; write share/eval/badges/anomaly.svg)
      Evidence: `python3 scripts/eval/anomaly_badge.py && ls -l share/eval/badges/anomaly.svg`
- [ ] Makefile: add targets eval.edge.audit & eval.anomaly.badge; include in eval.package
      Evidence: `rg -n 'eval.edge.audit|eval.anomaly.badge' Makefile`
- [ ] Fast checks: `time make -s ops.verify` → `[ops.verify] OK`
      Evidence: last 6 lines

## Failure Policy
- If any step fails: paste last 40 lines; STOP.

## Merge Sequence
- [ ] Open PR-026 (base=main). No merge without CI green.
