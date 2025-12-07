# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path
from scripts.config.env import get_rw_dsn

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "share" / "eval" / "soft_checks"
OUT.mkdir(parents=True, exist_ok=True)
LOG = OUT / "soft_checks.log"

CMDS = [
    ("ruff", ["ruff", "check", ".", "--quiet"], "HINT: ruff.check"),
    ("mypy", ["mypy", "."], "HINT: mypy"),
    ("pytest", ["pytest", "-q"], "HINT: pytest"),
]


def run(cmd):
    from scripts.util.filter_stderr import filter_cursor_noise

    try:
        p = subprocess.run(cmd, text=True, capture_output=True)
        stderr_filtered = filter_cursor_noise(p.stderr)
        return p.returncode, p.stdout, stderr_filtered
    except FileNotFoundError:
        return 127, "", "missing: " + cmd[0]


results = []
for name, cmd, tag in CMDS:
    if shutil.which(cmd[0]) is None:
        print(tag + " skipped (tool not installed)")
        results.append({"tool": name, "rc": 127, "stdout": "", "stderr": "not installed"})
        continue
    rc, out, err = run(cmd)
    print(tag + " rc=" + str(rc))
    if out:
        print("HINT: " + name + ".out.head=\n" + "\n".join(out.splitlines()[:20]))
    if err:
        print("HINT: " + name + ".err.head=\n" + "\n".join(err.splitlines()[:20]))
    results.append({"tool": name, "rc": rc, "stdout": out[-4000:], "stderr": err[-4000:]})

LOG.write_text(json.dumps(results, indent=2), encoding="utf-8")
print("HINT: soft_checks.log saved at " + str(LOG))

if not get_rw_dsn():
    print("HINT: env.GEMATRIA_DSN missing - DB-related checks were not executed (soft)")

sys.exit(0)
