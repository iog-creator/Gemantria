#!/usr/bin/env python3
"""
Master verification for pmagent + DMS.

Runs a set of CLI and DB checks and writes a JSON report to:
evidence/system/pmagent_dms_master_report.json

Exit code:
0 if all checks PASS
1 if any check FAIL or ERROR
"""

import datetime
import json
import subprocess
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Literal

Status = Literal["PASS", "FAIL", "ERROR"]


@dataclass
class CheckResult:
    id: str
    name: str
    category: str
    status: Status
    details: str = ""
    error: str | None = None


def _run(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _json_loads_safe(raw: str) -> object | None:
    """Safely parse JSON, return None on error."""
    try:
        return json.loads(raw)
    except Exception:
        return None


def _get_pmagent_cmd() -> str:
    """Get pmagent command path (prefer .venv/bin/pmagent)."""
    venv_pmagent = Path(".venv/bin/pmagent")
    if venv_pmagent.exists():
        return str(venv_pmagent)
    return "pmagent"


def check_health() -> List[CheckResult]:
    """Check pmagent health commands."""
    results: List[CheckResult] = []
    pmagent = _get_pmagent_cmd()

    for sub in ("system", "db", "lm"):
        cid = f"HEALTH-{sub.upper()}"
        name = f"pmagent health {sub}"
        rc, out, err = _run([pmagent, "health", sub])
        status: Status = "PASS" if rc == 0 else "FAIL"
        details = f"rc={rc}\nstdout={out}\nstderr={err}"
        error = None if rc == 0 else "pmagent health command failed"

        results.append(
            CheckResult(
                id=cid,
                name=name,
                category="health",
                status=status,
                details=details,
                error=error,
            )
        )

    return results


def check_control_status() -> List[CheckResult]:
    """Check pmagent control status and validate required tables."""
    results: List[CheckResult] = []
    pmagent = _get_pmagent_cmd()

    cid = "CONTROL-STATUS"
    name = "pmagent control status"
    rc, out, err = _run([pmagent, "control", "status"])

    if rc != 0:
        results.append(
            CheckResult(
                id=cid,
                name=name,
                category="control-plane",
                status="FAIL",
                details=f"rc={rc}\nstdout={out}\nstderr={err}",
                error="pmagent control status failed",
            )
        )
        return results

    data = _json_loads_safe(out)
    if not isinstance(data, dict):
        results.append(
            CheckResult(
                id=cid,
                name=name,
                category="control-plane",
                status="FAIL",
                details=f"rc={rc}\nstdout={out}\nstderr={err}",
                error="control status did not return JSON object",
            )
        )
        return results

    ok = data.get("ok")
    mode = data.get("mode")
    tables = data.get("tables", {})

    required_tables = [
        "control.agent_run",
        "control.agent_run_cli",
        "control.kb_document",
        "control.doc_registry",
        "control.doc_version",
    ]

    missing_tables = [t for t in required_tables if t not in tables or not tables[t].get("present")]

    if ok is True and mode == "ready" and not missing_tables:
        status: Status = "PASS"
        error = None
    else:
        status = "FAIL"
        problems = []
        if ok is not True:
            problems.append("ok != true")
        if mode != "ready":
            problems.append(f"mode={mode!r}")
        if missing_tables:
            problems.append(f"missing_tables={missing_tables}")
        error = "; ".join(problems)

    details = f"rc={rc}\nstdout={out}\nstderr={err}"
    results.append(
        CheckResult(
            id=cid,
            name=name,
            category="control-plane",
            status=status,
            details=details,
            error=error,
        )
    )

    return results


def check_kb_and_docs() -> List[CheckResult]:
    """Verify KB registry + status + docs search.

    This assumes that pm.share.artifacts or seed_registry.py has already
    created a kb registry. If not, this will fail and highlight the gap.
    """
    results: List[CheckResult] = []
    pmagent = _get_pmagent_cmd()

    # 1) Seed registry first
    cid_seed = "DMS-KB-SEED"
    name_seed = "seed_registry.py"
    seed_script = Path("scripts/kb/seed_registry.py")
    if seed_script.exists():
        rc_seed, out_seed, err_seed = _run([".venv/bin/python", "scripts/kb/seed_registry.py"])
        status_seed: Status = "PASS" if rc_seed == 0 else "FAIL"
        results.append(
            CheckResult(
                id=cid_seed,
                name=name_seed,
                category="kb",
                status=status_seed,
                details=f"rc={rc_seed}\nstdout={out_seed}\nstderr={err_seed}",
                error=None if rc_seed == 0 else "seed_registry.py failed",
            )
        )
    else:
        results.append(
            CheckResult(
                id=cid_seed,
                name=name_seed,
                category="kb",
                status="ERROR",
                details="scripts/kb/seed_registry.py not found",
                error="seed_registry.py script missing",
            )
        )

    # 2) pmagent kb registry list --json-only
    cid_list = "DMS-KB-REGISTRY"
    name_list = "pmagent kb registry list --json-only"
    rc, out, err = _run([pmagent, "kb", "registry", "list", "--json-only"])

    if rc != 0:
        results.append(
            CheckResult(
                id=cid_list,
                name=name_list,
                category="kb",
                status="FAIL",
                details=f"rc={rc}\nstdout={out}\nstderr={err}",
                error="kb registry list failed",
            )
        )
    else:
        data = _json_loads_safe(out)
        if not isinstance(data, dict) or "documents" not in data:
            results.append(
                CheckResult(
                    id=cid_list,
                    name=name_list,
                    category="kb",
                    status="FAIL",
                    details=f"rc={rc}\nstdout={out}\nstderr={err}",
                    error="kb registry JSON missing 'documents'",
                )
            )
        else:
            docs = data.get("documents") or []
            # Require at least some known IDs
            required_ids = {
                "ssot-master-plan",
                "ssot-pmagent-current-vs-intended",
            }

            present_ids = {d.get("id") for d in docs if isinstance(d, dict)}
            missing_ids = sorted(required_ids - present_ids)

            if missing_ids:
                status: Status = "FAIL"
                error = f"kb registry missing docs: {missing_ids}"
            elif len(docs) == 0:
                status = "FAIL"
                error = "kb registry has zero documents"
            else:
                status = "PASS"
                error = None

            details = f"rc={rc}\ncount={len(docs)}\nstdout={out}\nstderr={err}"
            results.append(
                CheckResult(
                    id=cid_list,
                    name=name_list,
                    category="kb",
                    status=status,
                    details=details,
                    error=error,
                )
            )

    # 3) pmagent status kb
    cid_status = "DMS-KB-STATUS"
    name_status = "pmagent status kb"
    rc, out, err = _run([pmagent, "status", "kb"])
    status: Status = "PASS" if rc == 0 else "FAIL"
    results.append(
        CheckResult(
            id=cid_status,
            name=name_status,
            category="kb",
            status=status,
            details=f"rc={rc}\nstdout={out}\nstderr={err}",
            error=None if rc == 0 else "pmagent status kb failed",
        )
    )

    # 4) pmagent docs search "governance"
    cid_search = "DMS-DOCS-SEARCH"
    name_search = 'pmagent docs search "governance"'
    rc, out, err = _run([pmagent, "docs", "search", "governance", "--json-only"])

    if rc != 0:
        results.append(
            CheckResult(
                id=cid_search,
                name=name_search,
                category="dms",
                status="FAIL",
                details=f"rc={rc}\nstdout={out}\nstderr={err}",
                error="pmagent docs search failed",
            )
        )
    else:
        data = _json_loads_safe(out)
        hits = []
        if isinstance(data, dict):
            hits = data.get("results") or data.get("matches") or []
        has_hits = isinstance(hits, list) and len(hits) > 0
        status = "PASS" if has_hits else "FAIL"
        err_msg = None if has_hits else "no search results for 'governance'"
        results.append(
            CheckResult(
                id=cid_search,
                name=name_search,
                category="dms",
                status=status,
                details=f"rc={rc}\nstdout={out}\nstderr={err}",
                error=err_msg,
            )
        )

    return results


def check_ai_tracking() -> List[CheckResult]:
    """Verify that at least one recent pmagent CLI run is tracked in control.agent_run_cli.

    NOTE: This uses psql against the 'gematria' DB and will fail if DSN/psql
    is misconfigured. That is a real gap, not a test bug.
    """
    results: List[CheckResult] = []
    pmagent = _get_pmagent_cmd()

    # Trigger a CLI run we expect to be tracked
    trigger_id = "AI-TRACK-TRIGGER"
    name_trigger = "pmagent health system (for tracking)"
    rc, out, err = _run([pmagent, "health", "system"])
    status: Status = "PASS" if rc == 0 else "FAIL"
    results.append(
        CheckResult(
            id=trigger_id,
            name=name_trigger,
            category="control-plane",
            status=status,
            details=f"rc={rc}\nstdout={out}\nstderr={err}",
            error=None if rc == 0 else "pmagent health system failed",
        )
    )

    # Now query agent_run_cli via psql
    cid = "AI-TRACK-AGENT-RUN-CLI"
    name = "control.agent_run_cli recent entries"
    psql_cmd = [
        "psql",
        "-d",
        "gematria",
        "-At",
        "-c",
        "SELECT command, status, created_at FROM control.agent_run_cli ORDER BY created_at DESC LIMIT 10",
    ]
    rc2, out2, err2 = _run(psql_cmd)

    if rc2 != 0:
        results.append(
            CheckResult(
                id=cid,
                name=name,
                category="control-plane",
                status="FAIL",
                details=f"rc={rc2}\nstdout={out2}\nstderr={err2}",
                error="psql query for agent_run_cli failed",
            )
        )
        return results

    lines = [ln.strip() for ln in out2.splitlines() if ln.strip()]
    has_any = len(lines) > 0
    has_system_health = any("system.health" in ln for ln in lines)

    if not has_any:
        status2: Status = "FAIL"
        error2 = "no rows in control.agent_run_cli"
    elif not has_system_health:
        status2 = "FAIL"
        error2 = "no recent system.health entry in agent_run_cli"
    else:
        status2 = "PASS"
        error2 = None

    details2 = f"rc={rc2}\nrows={len(lines)}\nstdout={out2}\nstderr={err2}"
    results.append(
        CheckResult(
            id=cid,
            name=name,
            category="control-plane",
            status=status2,
            details=details2,
            error=error2,
        )
    )

    return results


def check_repo_guard() -> List[CheckResult]:
    """Check pmagent repo guard-branch behavior on the current branch.

    This does not enforce a specific branch name; it just verifies:
      - If command exits 0, we treat that as "safe to work"
      - If command exits 1, we treat that as "protected branch"
    Either is acceptable as long as it is consistent and non-crashing.
    """
    results: List[CheckResult] = []
    pmagent = _get_pmagent_cmd()

    cid = "REPO-GUARD-BRANCH"
    name = "pmagent repo guard-branch"
    rc, out, err = _run([pmagent, "repo", "guard-branch"])

    if rc not in (0, 1):
        status: Status = "FAIL"
        error = f"unexpected exit code {rc}, expected 0 or 1"
    else:
        status = "PASS"
        error = None

    details = f"rc={rc}\nstdout={out}\nstderr={err}"
    results.append(
        CheckResult(
            id=cid,
            name=name,
            category="repo",
            status=status,
            details=details,
            error=error,
        )
    )

    return results


def main() -> int:
    """Run all checks and write report."""
    all_results: List[CheckResult] = []

    # Ordered so failures early are easier to interpret
    all_results.extend(check_health())
    all_results.extend(check_control_status())
    all_results.extend(check_kb_and_docs())
    all_results.extend(check_ai_tracking())
    all_results.extend(check_repo_guard())

    report = {
        "run_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "results": [asdict(r) for r in all_results],
    }

    out_dir = Path("evidence/system")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "pmagent_dms_master_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Simple summary
    total = len(all_results)
    failed = [r for r in all_results if r.status in ("FAIL", "ERROR")]
    print(f"[MASTER] Completed {total} checks. {len(failed)} failed.")
    print(f"[MASTER] Report written to: {report_path}")

    if failed:
        print("[MASTER] Some checks failed. See report for details.")
        return 1

    print("[MASTER] All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
