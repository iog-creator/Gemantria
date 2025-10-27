# Gemantria

[![CI](https://img.shields.io/github/actions/workflow/status/iog-creator/Gemantria/ci.yml?branch=main&label=CI)](https://github.com/iog-creator/Gemantria/actions)
![License](https://img.shields.io/badge/license-Personal%20Use%20Only-red)
![Phase](https://img.shields.io/badge/status-Phase%209-brightgreen)

An evaluation-driven pipeline for semantic networks over Hebrew biblical text, with calibrated edge strengths, quality badges, and audit/anomaly surfacing.

---

## TL;DR

- **Phase-9 live**: advanced calibration, quality trend badges, edge audit & anomaly badges.
- **Governance baked-in**: AlwaysApply rules, mandatory PR/NEXT_STEPS templates, and uniform `HINT:` lines in CI logs.
- **No green, no merge**: CI must pass. Duplicate Makefile targets guarded in smoke.

---

## Current Status (Oct 26, 2025)

- ✅ **024c** — Makefile duplicate-target guard landed (`targets.check.dupes`)
- ✅ **043** — Repo-native governance (rules 039–041 + NEXT_STEPS.md)
- ✅ **045** — PR & NEXT_STEPS templates (must cite **Rules/Agents/Docs/SSOT**)
- ✅ **046** — Emitted Hints discipline (`scripts/hint.sh`; required sections)
- ✅ **025** — Advanced calibration + quality trend badges
- ✅ **026** — Edge audit + anomaly badges
- 🔜 Next — Ongoing eval enhancements per master plan

See `docs/SSOT/MASTER_PLAN.md`, `docs/SSOT/RULES_INDEX.md`.

---

## Features

- **Advanced calibration**
  Otsu-like 2-threshold optimization across blended edge signals → `share/eval/calibration_adv.json`
- **Quality trend badges**
  Historical quality tracking with sparkline SVG → `share/eval/badges/quality_trend.svg`
- **Edge audit & anomaly badges**
  Z-score + IQR detection with colored SVG badge → `share/eval/badges/anomaly.svg`
- **Deterministic eval packaging**
  Makefile-driven eval flow + share mirror

---

## Quickstart

```bash
# 0) Dev sanity (fast path)
make -s ops.verify    # ends with [ops.verify] OK

# 1) Generate evaluation artifacts
make -s eval.package  # runs calibration/trend/audit + mirrors share/

# 2) Inspect outputs
ls -1 share/eval
cat share/eval/calibration_adv.json
```

> DB bootstrap is automatic in CI via `scripts/ci/ensure_db_then_migrate.sh` (creates DB, applies migrations, enables `vector`).

---

## Key Make Targets

* `ops.verify` — fast integrity smoke; no heavy deps
* `eval.graph.calibrate.adv` — writes `share/eval/calibration_adv.json`
* `eval.quality.trend` — updates `share/eval/quality_history.jsonl` & badge
* `eval.edge.audit` — writes `share/eval/edge_audit.json`
* `eval.anomaly.badge` — writes `share/eval/badges/anomaly.svg`
* `eval.package` — orchestrates all eval steps + share sync
* `targets.check.dupes` — CI smoke guard for duplicate Makefile targets

---

## Governance & Workflow

**AlwaysApply rules (repo-native)**

* `039-execution-contract.mdc` — GPT-5 orchestrates via PRs; Cursor executes commands
* `040-ci-triage-playbook.mdc` — surgical CI fixes only; no scope drift
* `041-pr-merge-policy.mdc` — no green, no merge; squash; delete branch

**Templates (required)**

* `.github/pull_request_template.md` — PRs must cite:

  * **Rules** (by ID), **Agents** (AGENTS.md anchors)
  * **Docs touched** (paths), **SSOT links** (RULES_INDEX / MASTER_PLAN)
  * **Emitted Hints** (key `HINT:` lines you expect in CI logs)
* `.cursor/templates/NEXT_STEPS.template.md` — runbooks with scope, steps, failure policy

**Emitted Hints discipline**

* Uniform helper: `scripts/hint.sh` → prints `HINT: <message>`
* Used in verify bootstrap and eval scripts to make CI logs greppable
* PRs & runbooks must include an **Emitted Hints** section

**Share hygiene**

* `share/SHARE_MANIFEST.json` present; `make share.sync` mirrors docs to `/share`
* CI fails if mirror is inconsistent

---

## Contribution Model

* Use the PR template; keep scope **surgical**.
* Provide evidence tails (decisive OK lines, or last ~200 lines on failure).
* **Do not** modify CI/governance unless explicitly ordered in the runbook.
* If CI fails: apply the minimal fix within the PR scope (see `040-ci-triage-playbook.mdc`).

---

## License

This project is licensed for **Personal Use Only**.
Commercial use requires a separate agreement. See `LICENSE` for terms and contact.

Badges and documentation reflect these terms (red "Personal Use Only" license badge).

---

## References

* **Agents:** `AGENTS.md`
* **Rules Index:** `docs/SSOT/RULES_INDEX.md`
* **Master Plan:** `docs/SSOT/MASTER_PLAN.md`
* **SSOT Primer:** `docs/SSOT/REFERENCES.md`

---

## Appendix: Useful Hints

Examples you'll see in CI logs:

```
HINT: verify: database bootstrap OK
HINT: eval: running advanced calibration
HINT: eval: writing quality trend badge
HINT: eval: auditing edges for anomalies
```

Use them to jump straight to relevant job log sections during triage.
