# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3

import argparse, json, os, pathlib, time, subprocess


def git_sha():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def fsize(p: str):
    q = pathlib.Path(p)
    return q.stat().st_size if q.exists() else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="var/ui/metrics.jsonl")
    ap.add_argument("--summary", default="webui/public/temporal_summary-*.md")
    ap.add_argument("--strip", default="webui/public/temporal_strip-*.csv")
    a = ap.parse_args()
    sha = git_sha()
    entry = {
        "ts": time.time(),
        "sha": sha,
        "summary_bytes": fsize(next_or("", a.summary)),
        "strip_bytes": fsize(next_or("", a.strip)),
    }
    pathlib.Path("var/ui").mkdir(parents=True, exist_ok=True)
    with open(a.log, "a") as fh:
        fh.write(json.dumps(entry) + "\n")
    print(entry)


def next_or(default, pattern):
    import glob

    matches = sorted(glob.glob(pattern), key=lambda p: os.path.getmtime(p)) if "*" in pattern else [pattern]
    return matches[-1] if matches else default


if __name__ == "__main__":
    main()
