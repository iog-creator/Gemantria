#!/usr/bin/env python3
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CANDIDATE_DIRS = [
    "examples",
    "data/examples",
    "samples",
    "tests/fixtures",
    "logs/probes",
]
NAME_PATTERNS = [
    r".*golden.*\.jsonl?$",
    r".*approved.*\.jsonl?$",
    r"10[-_]?nouns.*\.jsonl?$",
    r".*genesis.*\.jsonl?$",
    r".*probe.*\.jsonl?$",
]
LOG_PATTERNS_IN_FILE = [
    r"APPROVED",
    r"approved",
    r"golden",
    r'"source"\s*:\s*"lm"',
]

def match(name: str) -> bool:
    for p in NAME_PATTERNS:
        if re.search(p, name, re.IGNORECASE):
            return True
    return False

def git_info(path: Path):
    try:
        # last commit touching the file
        out = subprocess.check_output(
            ["git", "log", "-n", "1", "--pretty=format:%h|%ad|%s", "--date=iso", "--", str(path)],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            h, d, s = out.split("|", 2)
            return {"commit": h, "date": d, "msg": s}
    except Exception:
        pass
    return None

def scan():
    repo = Path(".").resolve()
    rows = []
    for base in CANDIDATE_DIRS:
        p = (repo / base)
        if not p.exists(): continue
        for f in p.rglob("*.jsonl"):
            if not match(f.name) and not match(str(f)):
                continue
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds")
                # peek first 2 lines
                head = []
                with f.open("r", encoding="utf-8", errors="ignore") as fh:
                    for i, line in enumerate(fh):
                        if line.strip():
                            head.append(line.strip())
                        if len(head) >= 2: break
                # heuristic: does content look like our noun rows?
                looks_like_nouns = any(re.search(r'"noun"\s*:\s*', h) for h in head)
                # look for "approved/golden" markers inside file
                content_flag = False
                try:
                    txt = "\n".join(head)
                    for ptn in LOG_PATTERNS_IN_FILE:
                        if re.search(ptn, txt): content_flag = True; break
                except Exception:
                    pass
                gi = git_info(f)
                rows.append({
                    "path": str(f.relative_to(repo)),
                    "mtime": mtime,
                    "size_kb": round(f.stat().st_size/1024, 1),
                    "git": gi or {},
                    "looks_like_nouns": looks_like_nouns,
                    "head": head,
                    "content_flag": content_flag,
                })
            except Exception:
                continue
    # sort: golden/approved in name first, then newer mtime
    def sort_key(r):
        name = r["path"].lower()
        rank = 0
        if "golden" in name: rank -= 10
        if "approved" in name: rank -= 8
        if "genesis" in name: rank -= 4
        return (rank, r["mtime"])
    rows.sort(key=sort_key)
    return rows

def print_table(rows):
    if not rows:
        print("[scan] No candidate example files found.")
        return 2
    cols = ["#", "path", "mtime", "size_kb", "git_commit", "git_date", "git_msg", "looks_like_nouns", "content_flag"]
    widths = {c: len(c) for c in cols}
    def upd(v, c):
        widths[c] = max(widths[c], len(str(v)))
    for i, r in enumerate(rows, 1):
        upd(i, "#"); upd(r["path"], "path"); upd(r["mtime"], "mtime")
        upd(r["size_kb"], "size_kb")
        gi = r.get("git") or {}
        upd(gi.get("commit",""), "git_commit")
        upd(gi.get("date",""), "git_date")
        upd((gi.get("msg","")[:60] + "…") if gi.get("msg","") and len(gi["msg"])>60 else gi.get("msg",""), "git_msg")
        upd(str(r["looks_like_nouns"]), "looks_like_nouns")
        upd(str(r["content_flag"]), "content_flag")
    header = " | ".join(c.ljust(widths[c]) for c in cols)
    sep = "-+-".join("-"*widths[c] for c in cols)
    print(header); print(sep)
    for i, r in enumerate(rows, 1):
        gi = r.get("git") or {}
        row_vals = [
            str(i),
            r["path"],
            r["mtime"],
            str(r["size_kb"]),
            gi.get("commit",""),
            gi.get("date",""),
            (gi.get("msg","")[:60] + "…") if gi.get("msg","") and len(gi["msg"])>60 else gi.get("msg",""),
            str(r["looks_like_nouns"]),
            str(r["content_flag"]),
        ]
        print(" | ".join(row_vals[j].ljust(widths[cols[j]]) for j in range(len(row_vals))))
    print("\n[scan] Tip: to inspect a row's head lines, run:\n  sed -n '1,5p' <PATH>\n")
    return 0

if __name__ == "__main__":
    rc = print_table(scan())
    sys.exit(rc)
