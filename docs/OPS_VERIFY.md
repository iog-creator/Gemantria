# Ops Verifier (Local-Only)

Determines whether the Phase-8 eval surfaces are wired correctly.

## Usage
```bash
make ops.verify
```

## What it checks

* `Makefile` contains `eval.report` and `ci.eval.report` targets
* `eval/manifest.yml` exists and reports a `version: …` value
* `docs/PHASE8_EVAL.md` exists and header starts with `# Phase-8 Eval`
* `share/eval/` directory exists

## Output

Deterministic lines prefixed with `[ops.verify]`, ending in either:

* `[ops.verify] OK`
* `[ops.verify] DONE_WITH_FAILS`

> **Note:** This verifier is local-only. No CI or `make go` changes.
