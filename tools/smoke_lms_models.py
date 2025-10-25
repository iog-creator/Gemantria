import glob
import os
import re
import sys

import requests

PORTS = {"embed": 9994, "llm": 9991, "critic": 9993}
OK = {"llm": re.compile(r"Q4_K_M", re.I), "critic": re.compile(r"Q4_K_(S|M)", re.I)}
ROOTS = [
    os.path.expanduser("~/Library/Application Support/LM Studio/models"),
    os.path.expandvars(r"%APPDATA%\\LM Studio\\models"),
    os.path.expanduser("~/.cache/lm-studio/models"),
]


def active(port):
    r = requests.get(f"http://127.0.0.1:{port}/v1/models", timeout=5)
    r.raise_for_status()
    return [m["id"] for m in r.json().get("data", [])]


def quant_for(mid):
    for root in ROOTS:
        for p in glob.glob(root + "/**/*.gguf", recursive=True):
            if any(s and s.lower() in p.lower() for s in mid.split("/")):
                m = re.search(r"(Q[0-9]_(?:K_[MS]|0))\.gguf$", p, re.I)
                return (m.group(1).upper() if m else "UNKNOWN", p)
    return ("UNKNOWN", None)


fail = False
for phase, port in PORTS.items():
    try:
        ids = active(port)
    except Exception as e:
        print(f"[FAIL] :{port} unreachable: {e}")
        sys.exit(1)
    if len(ids) != 1:
        print(f"[FAIL] :{port} must have exactly one model, got {ids}")
        sys.exit(1)
    q, path = quant_for(ids[0])
    print(f"[OK] {phase}: id={ids[0]} quant={q} path={path or '<n/a>'}")
    if phase in OK and q != "UNKNOWN" and not OK[phase].search(q):
        print(f"[FAIL] {phase} quant {q} not allowed")
        sys.exit(1)
print("[OK] model audit passed")
