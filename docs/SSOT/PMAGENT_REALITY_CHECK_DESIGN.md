# pmagent reality.check — Design Document

## 1. Purpose (Plain English)

`pmagent reality.check` is a **single command** you (or a workflow) can run to answer:

> "Is my environment real and safe enough to run the rest of this system right now?"

It should:

* Validate **env + DSN + DB + control plane**.
* Validate **LM Studio / models**.
* Run a **minimal Phase-8 eval smoke**.
* Produce:
  * A **JSON verdict** the control plane can store.
  * A **short human summary** in the console.
* Exit:
  * `0` if everything is acceptable for the current mode (HINT vs STRICT),
  * non-zero if not.

It is *not* a full pipeline; it's the **gate** before pipelines.

---

## 2. Modes: HINT vs STRICT

We already have this idea in the governance contract:

* **HINT mode (hermetic)**:
  * Used on PRs and local dev.
  * Fail "soft": command exits 0 if critical infra (env/DSN + DB/control-plane) is OK, but collects hints about missing or non-critical pieces (e.g., LM offline, no sample data, missing exports).

* **STRICT mode (live-ready)**:
  * Used on tags / releases and local strict bringup.
  * Fail "hard": any serious mismatch (DSN, control-plane schema, LM config, or eval smokes) → non-zero exit, recorded as violation.
  * The `make bringup.live` target is the human-facing strict bringup gate and calls `pmagent reality-check check --mode strict --no-dashboards` before running `make bringup.001`.

`pmagent reality.check` should accept:

* `--mode hint` (default for local)
* `--mode strict` (for tags / release workflows)

---

## 3. What Checks It Actually Runs (Stack)

Reusing what we *already* do, but wrapped into one CLI call.

### Core Blocks

#### 1. Env & DSN

* Use `scripts/config/env.py` to load:
  * DB DSN (`get_rw_dsn()`, `get_ro_dsn()`, `get_bible_db_dsn()`),
  * LM provider settings (`INFERENCE_PROVIDER`, `OLLAMA_ENABLED`, `LM_STUDIO_ENABLED`),
  * Control-plane schema name(s),
  * Any special feature toggles.
* Check for obviously missing or contradictory env vars.
* Return structured `env_ok`, `dsn_ok`, and any hint messages.

**Implementation:** Reuse `scripts/config/env.py` helpers directly.

#### 2. DB & Control Plane

* Equivalent to:
  * `pmagent control status`
  * `pmagent control summary`
* Checks:
  * DB reachable?
  * Control schemas present?
  * Key tables present (`control.agent_run`, `control.capability_session`, `control.doc_fragment`, etc.)?
* Return `db_ok`, `control_ok`, plus detail.

**Implementation:** Reuse `scripts/control/control_status.py` (`compute_control_status()`) and `scripts/control/control_summary.py` (`compute_control_summary()`).

#### 3. LM & Models

* Equivalent to:
  * `pmagent health lm`
  * `pmagent lm status`
* Checks:
  * LM provider reachable (LM Studio / Ollama).
  * Configured model slots (main LLM, theology, embedding, reranker) exist.
* Return `lm_ok`, per-slot flags, and discovered model names.

**Implementation:** Reuse `scripts/guards/guard_lm_health.py` (`check_lm_health()`) and `agentpm/lm/lm_status.py` (`compute_lm_status()`).

#### 4. Exports & Atlas Indicators

* Read the same JSONs the Phase-8 dashboards and guards use:
  * `share/atlas/control_plane/lm_indicator.json`
  * `share/atlas/control_plane/compliance.head.json`
  * `share/atlas/control_plane/kb_docs.head.json` (if exists)
* Use the hermetic JSON loader (we already added) to:
  * Distinguish between: missing file, invalid JSON, "offline but safe", etc.
* Return `exports_ok`, and per-export statuses.

**Implementation:** Reuse hermetic JSON loaders from `scripts/db/control_lm_indicator_export.py`, `agentpm/control_plane/exports.py`, and similar patterns from `scripts/atlas/generate_compliance_summary.py`.

#### 5. Eval Smoke

* Call **exactly what we already wired**:
  * `make eval.smoke` or the underlying python functions.
  * Capture:
    * `eval_ok` flag,
    * any high-level messages (e.g., "graph stats empty but schema ok").

**Implementation:** Reuse `make eval.smoke` via subprocess, or call underlying functions directly:
  * `make ci.exports.smoke` → `scripts/ci/validate_exports.py`
  * `make eval.graph.calibrate.adv` → `scripts/eval/calibrate_advanced.py`

In **HINT mode**, failures in 4–5 (exports/eval) may produce hints but not non-zero exit.

In **STRICT mode**, all of the above must be true or we exit with error.

---

## 4. CLI UX

### Command Shape

```bash
pmagent reality-check check --mode hint
pmagent reality-check check --mode strict
```

**Note:** The command is `reality-check check` (not `reality.check`) because we already have a `reality-check` Typer app in `pmagent/cli.py`.

Optional flags:

* `--json-only` → print only JSON verdict to stdout.
* `--no-dashboards` → skip steps 4–5 if we only want infra baseline.

### Human Output (Example)

```text
[pmagent] reality.check (mode=HINT)

Env / DSN:        OK  (config/env.py loaded, DSN present)
DB / Control:     OK  (control schema=control, 76 tables validated)
LM / Models:      WARN (LM offline: theology model missing; embeddings ok)
Exports / Atlas:  OK  (lm_indicator, compliance.head, kb_docs.head loaded)
Eval smoke:       OK  (ci.exports.smoke + eval.graph.calibrate.adv)

Hints:
- LM: theology slot model not installed (Christian-Bible-Expert-v2.0-12B)

Result: HINT mode: **overall OK** (see JSON verdict for details)
```

---

## 5. JSON Verdict Shape

Something like:

```json
{
  "command": "reality.check",
  "mode": "HINT",
  "timestamp": "2025-11-17T03:21:00Z",
  "env": {
    "ok": true,
    "dsn_ok": true,
    "details": {}
  },
  "db": {
    "ok": true,
    "control_schema": "control",
    "tables_expected": 76,
    "tables_present": 76
  },
  "lm": {
    "ok": false,
    "provider": "lm_studio",
    "slots": {
      "main": { "configured": true, "present": true, "model": "granite4:tiny-h" },
      "theology": { "configured": true, "present": false, "model": "Christian-Bible-Expert-v2.0-12B" },
      "embedding": { "configured": true, "present": true, "model": "granite-embedding:278m" },
      "reranker": { "configured": false, "present": false }
    }
  },
  "exports": {
    "ok": true,
    "lm_indicator": { "ok": true, "status": "offline" },
    "compliance_head": { "ok": true },
    "kb_docs_head": { "ok": true }
  },
  "eval_smoke": {
    "ok": true,
    "targets": ["ci.exports.smoke", "eval.graph.calibrate.adv"]
  },
  "hints": [
    "LM theology slot model Christian-Bible-Expert-v2.0-12B is not installed."
  ],
  "overall_ok": true
}
```

This is what we'd insert into:

* `control.agent_run` row (as `result_json`), and/or
* a dedicated `reality_check` table if we want historical runs.

---

## 6. Internal Flow in `pmagent reality.check`

Rough pseudocode-style design:

```python
def reality_check(mode: Literal["HINT", "STRICT"] = "HINT") -> Verdict:
    session = start_capability_session("reality.check", mode=mode)  # Optional: if DB available

    env_result = check_env_and_dsn()
    db_result = check_db_and_control()
    lm_result = check_lm_health()
    exports_result = check_control_plane_exports()
    eval_result = run_eval_smoke()

    hints: list[str] = []
    hard_fail = False

    # HINT vs STRICT logic
    if not env_result.ok or not db_result.ok:
        hard_fail = True
        hints.append("Env/DSN or DB/control-plane baseline failed.")

    if mode == "STRICT":
        if not lm_result.ok:
            hard_fail = True
            hints.append("LM config or models not OK in STRICT mode.")
        if not exports_result.ok or not eval_result.ok:
            hard_fail = True
            hints.append("Exports or eval smoke failed in STRICT mode.")
    else:
        # HINT mode: record hints but allow overall_ok=True if core infra is up
        if not lm_result.ok:
            hints.append("LM not fully OK (see slots).")
        if not exports_result.ok:
            hints.append("Exports not fully OK (see exports block).")
        if not eval_result.ok:
            hints.append("Eval smoke failed; see eval_smoke block.")

    verdict = Verdict(
        command="reality.check",
        mode=mode,
        env=env_result,
        db=db_result,
        lm=lm_result,
        exports=exports_result,
        eval_smoke=eval_result,
        hints=hints,
        overall_ok=not hard_fail,
    )

    record_in_control_plane(session, verdict)  # Optional: if DB available
    print_human_summary(verdict)

    if hard_fail:
        sys.exit(1)
    else:
        sys.exit(0)
```

---

## 7. Implementation Plan

### Step 1: Create Module

Create `agentpm/reality/check.py` with:

* `check_env_and_dsn()` → uses `scripts/config/env.py`
* `check_db_and_control()` → uses `scripts/control/control_status.py` and `scripts/control/control_summary.py`
* `check_lm_health()` → uses `scripts/guards/guard_lm_health.py` and `agentpm/lm/lm_status.py`
* `check_control_plane_exports()` → uses hermetic JSON loaders
* `run_eval_smoke()` → calls `make eval.smoke` or underlying functions
* `reality_check(mode: str)` → orchestrates all checks and returns verdict
* `print_human_summary(verdict: dict)` → formats human-readable output

### Step 2: Add CLI Command

In `pmagent/cli.py`, add:

```python
@reality_app.command("check", help="Run comprehensive reality check (env + DB + LM + exports + eval)")
def reality_check_check(
    mode: str = typer.Option("hint", "--mode", help="Mode: hint (default) or strict"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    no_dashboards: bool = typer.Option(False, "--no-dashboards", help="Skip exports/eval checks"),
) -> None:
    """Run comprehensive reality check."""
    from agentpm.reality.check import reality_check, print_human_summary
    
    mode_upper = mode.upper()
    if mode_upper not in ("HINT", "STRICT"):
        print(f"ERROR: mode must be 'hint' or 'strict', got '{mode}'", file=sys.stderr)
        sys.exit(1)
    
    verdict = reality_check(mode=mode_upper, skip_dashboards=no_dashboards)
    
    if json_only:
        print(json.dumps(verdict, indent=2))
    else:
        print(json.dumps(verdict, indent=2))
        print_human_summary(verdict, file=sys.stderr)
    
    sys.exit(0 if verdict.get("overall_ok") else 1)
```

### Step 3: Optional Control Plane Recording

If DB is available, optionally record the verdict in `control.agent_run`:

```python
def record_in_control_plane(session_id: str | None, verdict: dict) -> None:
    """Record reality check verdict in control.agent_run if DB available."""
    if psycopg is None:
        return
    
    dsn = get_rw_dsn()
    if not dsn:
        return
    
    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO control.agent_run
                (project_id, session_id, tool, args_json, result_json, violations_json)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    1,  # project_id (hardcoded for now)
                    session_id,
                    "reality.check",
                    json.dumps({"mode": verdict.get("mode")}),
                    json.dumps(verdict),
                    json.dumps([]),  # violations_json
                ),
            )
            conn.commit()
    except Exception:
        pass  # Non-fatal: recording is optional
```

---

## 8. How It Fits Back into the Bigger Picture

Once `pmagent reality.check` exists and is logged:

* **Local dev**: you run it once and see a clean summary instead of remembering 5 different commands.
* **CI**:
  * PR workflows can call `pmagent reality-check check --mode hint` once, and rely on its verdict + DSN/LM/export checks.
  * Tag/release workflows can call `pmagent reality-check check --mode strict` as a hard gate.
* **Dashboards & Atlas**:
  * We can show a "Last reality.check" tile / timestamp in your orchestrator UI.
  * Atlas can surface the last-known environment posture.

This moves us closer to the Grok description where pmagent is a **single, governed entry point** for "is this system real enough to run?".

---

## 9. Testing Strategy

* **Unit tests**: Test each check function independently with mocked dependencies.
* **Integration tests**: Test full `reality_check()` with real DB/LM (when available) and hermetic fallbacks.
* **CI tests**: Run `pmagent reality-check check --mode hint` in CI to ensure it works hermetically.

---

## 10. Related Documentation

* `docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md` – Current vs intended state.
* `docs/runbooks/CONTROL_SUMMARY.md` – Control-plane summary usage.
* `docs/runbooks/SYSTEM_HEALTH.md` – System health checks.
* `docs/runbooks/LM_HEALTH.md` – LM health checks.
* `AGENTS.md` (root) – Agent framework and operational contracts.

---

**Last Updated:** 2025-11-17  
**Status:** Design document; ready for implementation.

