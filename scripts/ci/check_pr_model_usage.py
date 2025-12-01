# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3

import re, subprocess

REQ = [r"Model:", r"Iterations:", r"Prompt \(last effective\):"]


def prnum():
    try:
        return subprocess.check_output(["gh", "pr", "view", "--json", "number", "--jq", ".number"], text=True).strip()
    except Exception:
        return ""


def main():
    n = prnum()
    if not n:
        print("[PRCHECK] No open PR for this branch; SKIP.")
        return 0
    body = subprocess.check_output(["gh", "pr", "view", n, "--json", "body", "--jq", ".body"], text=True)
    missing = [p for p in REQ if re.search(p, body) is None]
    if missing:
        print("[PRCHECK] FAIL: missing in 'Model Usage':", ", ".join(missing))
        print("Add them per .github/PULL_REQUEST_TEMPLATE.md")
        return 2
    print("[PRCHECK] OK: Model Usage present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
