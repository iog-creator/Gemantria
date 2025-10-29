#!/usr/bin/env python3
import json
import pathlib
import subprocess
import os

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_OUTDIR = ROOT / "share" / "eval"
OUTDIR = ROOT / os.environ.get("EVAL_OUTDIR", str(DEFAULT_OUTDIR.relative_to(ROOT)))
OUT = OUTDIR / "policy_diff.md"


def _run(cmd: list[str], env: dict | None = None) -> tuple[int, str, str]:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout, r.stderr


def _summary(report_path: pathlib.Path) -> tuple[int, int]:
    if not report_path.exists():
        return 0, 0
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
        summary = data.get("summary", {})
        return summary.get("ok_count", 0), summary.get("fail_count", 0)
    except Exception:
        return 0, 0


def main():
    print("[eval.policydiff] starting")

    OUTDIR.mkdir(parents=True, exist_ok=True)

    # strict (ensure sub-make writes into our OUTDIR)
    env = dict(os.environ)
    env["EVAL_OUTDIR"] = str(OUTDIR.relative_to(ROOT))
    code, so, se = _run(["make", "eval.profile.strict"], env=env)
    if code != 0:
        print(f"[eval.policydiff] WARN eval.profile.strict failed: {se}")
    ok_strict, fail_strict = _summary(OUTDIR / "report.json")

    # dev
    code, so, se = _run(["make", "eval.profile.dev"], env=env)
    if code != 0:
        print(f"[eval.policydiff] WARN eval.profile.dev failed: {se}")
    ok_dev, fail_dev = _summary(OUTDIR / "report.json")

    # Generate diff
    diff_lines = [
        "# Policy Diff Report",
        "",
        f"Generated in {OUTDIR.relative_to(ROOT)}",
        "",
        "## Strict Profile",
        f"- OK: {ok_strict}",
        f"- FAIL: {fail_strict}",
        "",
        "## Dev Profile",
        f"- OK: {ok_dev}",
        f"- FAIL: {fail_dev}",
        "",
        "## Summary",
        f"Strict: {ok_strict}/{ok_strict + fail_strict} OK",
        f"Dev: {ok_dev}/{ok_dev + fail_dev} OK",
    ]

    OUT.write_text("\n".join(diff_lines), encoding="utf-8")
    print(f"[eval.policydiff] wrote {OUT.relative_to(ROOT)}")
    print("[eval.policydiff] done")


if __name__ == "__main__":
    main()
