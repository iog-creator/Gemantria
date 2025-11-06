#!/usr/bin/env python3
"""
Operator Dashboard Report Generator

Creates a single JSON summary for humans + CI monitoring.
"""

import json
import glob
import os
import time
import hashlib


def latest(globpat):
    files = sorted(glob.glob(globpat))
    return files[-1] if files else None


def sha12(p):
    if not p or not os.path.exists(p):
        return None
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]


def read_json(p):
    return json.load(open(p)) if p and os.path.exists(p) else None


def main():
    now = int(time.time())

    graph_cur = latest("share/exports/graph_latest.json")
    graph_prev = "share/exports/graph_last_good.json" if os.path.exists("share/exports/graph_last_good.json") else None
    summ_latest = latest("share/evidence/*summary_*.json")

    cur = read_json(graph_cur) or {}
    prev = read_json(graph_prev) or {}
    summ = read_json(summ_latest) or {}

    # Extract graph stats
    nodes = cur.get("stats", {}).get("nodes") or (len(cur.get("nodes", [])) if "nodes" in cur else None)
    edges = cur.get("stats", {}).get("edges") or (len(cur.get("edges", [])) if "edges" in cur else None)
    pn = prev.get("stats", {}).get("nodes")
    pe = prev.get("stats", {}).get("edges")

    # Extract latency/token stats
    lat = {
        "p50_ms": summ.get("timing_p50_ms"),
        "p95_ms": summ.get("timing_p95_ms"),
        "p99_ms": summ.get("timing_p99_ms"),
        "tps": summ.get("tps"),
        "tokens_in": summ.get("tokens_in"),
        "tokens_out": summ.get("tokens_out"),
        "tokens_total": summ.get("tokens_total"),
    }

    models = summ.get("models_used", {})
    budget = (summ.get("budget") or {}).get("breach")

    report = {
        "ts": now,
        "artifacts": {
            "graph_latest": {"path": graph_cur, "sha256_12": sha12(graph_cur)} if graph_cur else None,
            "graph_last_good": {"path": graph_prev, "sha256_12": sha12(graph_prev)} if graph_prev else None,
            "summary_latest": summ_latest,
        },
        "graph": {
            "nodes": nodes,
            "edges": edges,
            "last_good_nodes": pn,
            "last_good_edges": pe,
            "delta_nodes": (None if pn is None or nodes is None else nodes - pn),
            "delta_edges": (None if pe is None or edges is None else edges - pe),
        },
        "latency_tokens": lat,
        "models_used": models,
        "run_flags": summ.get("run"),
        "budget_breach": budget,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
