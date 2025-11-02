#!/usr/bin/env python3

"""

Attach thresholds metadata to aggregation (reuse-first).

- Reads EDGE_STRONG, EDGE_WEAK, CANDIDATE_POLICY from env.

- Writes build/aggregation_meta.json and prints a single JSON line for CI logs.

- Never touches share/; no network; OK if aggregation data absent.

"""

from __future__ import annotations

import os, json, pathlib, hashlib, time

EDGE_STRONG = float(os.getenv("EDGE_STRONG") or "0.90")

EDGE_WEAK = float(os.getenv("EDGE_WEAK") or "0.75")

CANDIDATE_POLICY = os.getenv("CANDIDATE_POLICY") or "cache"

SEED = int(os.getenv("PIPELINE_SEED") or "4242")

meta = {
    "stage": "aggregate.meta",
    "thresholds": {
        "EDGE_STRONG": EDGE_STRONG,
        "EDGE_WEAK": EDGE_WEAK,
        "CANDIDATE_POLICY": CANDIDATE_POLICY,
    },
    "seed": SEED,
    "ts": int(time.time()),
}

finger = f"{EDGE_STRONG}|{EDGE_WEAK}|{CANDIDATE_POLICY}|{SEED}"

meta["hint"] = "HINT[thresholds.sha]: " + hashlib.sha256(finger.encode()).hexdigest()[:12]

outdir = pathlib.Path("build")
outdir.mkdir(parents=True, exist_ok=True)

with open(outdir / "aggregation_meta.json", "w", encoding="utf-8") as fh:
    json.dump(meta, fh, ensure_ascii=False)

print(json.dumps(meta, ensure_ascii=False))
