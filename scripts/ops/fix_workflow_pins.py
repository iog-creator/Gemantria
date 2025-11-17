#!/usr/bin/env python3
"""
scripts/ops/fix_workflow_pins.py

Usage:
    python3 scripts/ops/fix_workflow_pins.py          # dry-run, show suspects and write evidence
    python3 scripts/ops/fix_workflow_pins.py --apply  # apply changes, commit, push, create PRs (requires gh auth)
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


ROOT = Path(".").resolve()
WF_DIR = ROOT / ".github" / "workflows"
EVID = ROOT / "evidence" / "workflow_fixes"


LONG_SHA_RE = re.compile(r"@([0-9a-f]{8,40})\b", re.IGNORECASE)
USES_RE = re.compile(r"uses:\s*([^\s@]+)@([0-9a-f]{8,40})", re.IGNORECASE)


def list_workflows() -> List[Path]:
    return sorted(WF_DIR.glob("*.yml"))


def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def safe_yaml_load(text: str, p: Path) -> Tuple[bool, str | None]:
    try:
        yaml.safe_load(text)
        return True, None
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def replace_peter_evans(text: str) -> Tuple[bool, str]:
    """
    Conservative replacement:
    - Replace peter-evans/create-or-update-comment@<sha> with @v3
    - Leave all other actions untouched (reported as suspects only)
    """
    new = re.sub(
        r"(peter-evans/create-or-update-comment)@([0-9a-f]{8,40})",
        r"\1@v3",
        text,
        flags=re.IGNORECASE,
    )
    changed = new != text
    return changed, new


def find_suspects(text: str) -> List[Dict[str, Any]]:
    suspects: List[Dict[str, Any]] = []
    for match in USES_RE.finditer(text):
        full_action = match.group(1)
        sha = match.group(2)
        suspects.append({"action": full_action, "sha": sha})
    return suspects


def run_cmd(cmd: str, cwd: Path | None = None) -> Tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        shell=True,
        cwd=str(cwd) if cwd is not None else None,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def create_pr(branch: str, title: str, body: str) -> Tuple[bool, str]:
    cmd = (
        "gh pr create "
        "--repo iog-creator/Gemantria "
        f'--title "{title}" '
        f'--body "{body}" '
        "--base main "
        f"--head {branch} "
        "--json url"
    )
    rc, out, err = run_cmd(cmd)
    if rc != 0:
        return False, err or out
    try:
        url = json.loads(out).get("url")  # type: ignore[assignment]
    except Exception:  # noqa: BLE001
        url = out.strip()
    return True, str(url)


def main() -> int:
    apply_mode = "--apply" in sys.argv

    EVID.mkdir(parents=True, exist_ok=True)

    workflows = list_workflows()
    if not workflows:
        print("No workflow files found in .github/workflows")
        return 0

    summary: List[Dict[str, Any]] = []

    for wf in workflows:
        text = load_text(wf)
        ok_yaml_before, yaml_err_before = safe_yaml_load(text, wf)
        suspects = find_suspects(text)
        changed = False

        before_snippet = text.splitlines()[:200]

        # Auto-fix only peter-evans pins
        fixed, new_text = replace_peter_evans(text)
        if fixed:
            changed = True

        # Validate YAML after changes (or re-validate original if unchanged)
        if changed:
            ok_yaml_after, yaml_err_after = safe_yaml_load(new_text, wf)
        else:
            ok_yaml_after, yaml_err_after = ok_yaml_before, yaml_err_before

        summary.append(
            {
                "path": str(wf),
                "ok_before": ok_yaml_before,
                "yaml_err_before": yaml_err_before,
                "suspects": suspects,
                "auto_fixed": changed,
                "ok_after": ok_yaml_after,
                "yaml_err_after": yaml_err_after,
            }
        )

        if not changed:
            continue

        # Write before/after evidence snippets
        before_file = EVID / f"before_{wf.name}.txt"
        after_file = EVID / f"after_{wf.name}.txt"
        before_file.write_text("\n".join(before_snippet), encoding="utf-8")
        after_file.write_text("\n".join(new_text.splitlines()[:200]), encoding="utf-8")

        print(f"[AUTO] Fixed {wf} (peter-evans pin). Valid YAML after: {ok_yaml_after}")

        if not apply_mode:
            print("  (dry-run) To apply, run with --apply")
            continue

        # In apply mode, create a dedicated branch, commit, push, and open a PR
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        branch = f"fix/workflow-{wf.stem}-{ts}"

        rc, out, err = run_cmd(f"git checkout -b {branch}")
        if rc != 0:
            print(f"  WARN: git checkout -b failed for {branch}: {err or out}")
            continue

        wf.write_text(new_text, encoding="utf-8")
        run_cmd(f"git add {wf}")
        rc, out, err = run_cmd(f'git commit -m "chore(ci): fix workflow {wf.name} (peter-evans pin -> @v3)"')
        if rc != 0:
            print(f"  WARN: git commit failed for {wf}: {err or out}")
            continue

        rc, out, err = run_cmd(f"git push --set-upstream origin {branch}")
        if rc != 0:
            print(f"  WARN: git push failed for {branch}: {err or out}")
            continue

        title = f"chore(ci): fix workflow {wf.name} (pin create-or-update-comment -> @v3)"
        body = (
            "Auto-generated fix: replaced removed long-SHA pin for "
            "peter-evans/create-or-update-comment with stable @v3 and validated YAML.\n\n"
            "See evidence in evidence/workflow_fixes/."
        )
        ok, url_or_err = create_pr(branch, title, body)
        if ok:
            print("  PR created:", url_or_err)
        else:
            print("  PR creation failed:", url_or_err)

    # Write summary JSON
    sumfile = EVID / "fix_workflow_pins_summary.json"
    sumfile.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("WROTE", sumfile)
    print("Summary printed; check evidence/workflow_fixes for details.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
