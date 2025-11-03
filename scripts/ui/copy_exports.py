#!/usr/bin/env python3

import argparse, shutil, sys, time, subprocess, pathlib


def version_tag():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return time.strftime("%Y%m%d%H%M%S")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="ui/out")
    ap.add_argument("--dst", default="webui/public")
    ap.add_argument("--version", default=None)
    a = ap.parse_args()
    v = a.version or version_tag()
    src = pathlib.Path(a.src)
    dst = pathlib.Path(a.dst)
    dst.mkdir(parents=True, exist_ok=True)
    mapping = {
        "temporal_strip.csv": f"temporal_strip-v{v}.csv",
        "temporal_summary.md": f"temporal_summary-v{v}.md",
    }
    wrote = []
    for s, d in mapping.items():
        p = src / s
        if not p.exists():
            print(f"[COPY] SKIP missing: {p}", file=sys.stderr)
            continue
        shutil.copy2(p, dst / d)
        wrote.append(d)
    if not wrote:
        print("[COPY] Nothing copied.", file=sys.stderr)
        return 0
    print("[COPY] Wrote:", *wrote)
    print("[COPY] Hint: serve with Cache-Control: max-age=31536000, immutable", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
