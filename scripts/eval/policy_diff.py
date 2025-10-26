#!/usr/bin/env python3
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "share" / "eval" / "policy_diff.md"


def _run(cmd: list[str]) -> tuple[int, str, str]:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def _summary(path: pathlib.Path) -> tuple[int, int]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        s = doc.get("summary", {})
        return int(s.get("ok_count", 0)), int(s.get("fail_count", 0))
    except Exception:
        return 0, 0


def main() -> int:
    print("[eval.policydiff] starting")
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # strict
    code, so, se = _run(["make", "eval.profile.strict"])
    ok_strict, fail_strict = _summary(ROOT / "share" / "eval" / "report.json")

    # dev
    code, so, se = _run(["make", "eval.profile.dev"])
    ok_dev, fail_dev = _summary(ROOT / "share" / "eval" / "report.json")

    lines = []
    lines.append("# Gemantria Policy Delta")
    lines.append("")
    lines.append(f"*strict:* ok={ok_strict} fail={fail_strict}")
    lines.append(f"*dev:*    ok={ok_dev} fail={fail_dev}")
    lines.append("")
    if fail_strict > fail_dev:
        lines.append(
            "**Observation:** Dev profile masks some failures present under strict."
        )
    elif fail_strict == fail_dev:
        lines.append("**Observation:** Profiles produce identical pass/fail counts.")
    else:
        lines.append(
            "**Observation:** Dev profile surfaced more failures (unexpected)."
        )
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[eval.policydiff] wrote {OUT.relative_to(ROOT)}")
    print("[eval.policydiff] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
