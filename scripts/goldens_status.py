#!/usr/bin/env python3
import subprocess
from datetime import datetime
from pathlib import Path

ROOTS = [Path("examples/archive"), Path("examples/enrichment")]


def last_touch(p: Path):
    try:
        out = subprocess.check_output(
            [
                "git",
                "log",
                "-n",
                "1",
                "--pretty=format:%h|%ad|%s",
                "--date=iso",
                "--",
                str(p),
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if out:
            h, d, s = out.split("|", 2)
            return h, d, s
    except Exception:
        pass
    return "", "", ""


def main():
    rows = []
    for base in ROOTS:
        if not base.exists():
            continue
        for f in base.rglob("*.json*"):
            st = f.stat()
            h, d, s = last_touch(f)
            rows.append(
                {
                    "path": str(f),
                    "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(
                        timespec="seconds"
                    ),
                    "kb": round(st.st_size / 1024, 1),
                    "commit": h,
                    "date": d,
                    "msg": s,
                }
            )
    if not rows:
        print("[goldens.status] no golden files found under examples/")
        return 2
    print("path | mtime | size_kb | git_commit | git_date | git_msg")
    print("-" * 96)
    for r in sorted(rows, key=lambda x: x["path"]):
        print(
            f"{r['path']} | {r['mtime']} | {r['kb']} | {r['commit']} | {r['date']} | {r['msg']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
