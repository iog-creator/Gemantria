# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3

"""

Phase-4 adapter (reuse-first): convert existing exports/** into a minimal

viewer-ready JSON bundle without changing upstream writers or the UI.



- If no exports exist, emits an empty, valid bundle and exits 0 (hermetic CI-friendly).

- Never writes to share/ in CI; writes to build/webui_bundle/ locally.

"""

import json, glob, pathlib, sys, os

OUTDIR = pathlib.Path("build/webui_bundle")
OUTDIR.mkdir(parents=True, exist_ok=True)

EDGE_STRONG = float(os.getenv("EDGE_STRONG", "0.90"))
EDGE_WEAK = float(os.getenv("EDGE_WEAK", "0.75"))
CANDIDATE_POLICY = os.getenv("CANDIDATE_POLICY", "cache")
SEED = int(os.getenv("PIPELINE_SEED", "4242"))

bundle = {
    "nodes": [],
    "edges": [],
    "meta": {
        "source": "exports/",
        "reuse_first": True,
        "thresholds": {
            "EDGE_STRONG": EDGE_STRONG,
            "EDGE_WEAK": EDGE_WEAK,
            "CANDIDATE_POLICY": CANDIDATE_POLICY,
        },
        "seed": SEED,
        "temporal": {
            "files": 0,
            "keys": [],
        },  # filled in below if any temporal-looking exports are present
    },
}

# Gather any exports we already produce

cands = glob.glob("exports/**/*.json*", recursive=True) + glob.glob(
    "exports/**/*.csv", recursive=True
)

if not cands:
    with open(OUTDIR / "bundle.json", "w", encoding="utf-8") as fh:
        json.dump(bundle, fh, ensure_ascii=False)

    print("[adapter] no exports found; wrote empty bundle")
    sys.exit(0)


def try_load_json(p):
    try:
        with open(p, encoding="utf-8") as fh:
            if p.endswith(".jsonl") or p.endswith(".ndjson"):
                lines = [json.loads(x) for x in fh.readlines()[:200]]  # head only

                return lines

            return json.load(fh)

    except Exception as e:
        print(f"[adapter] skip {p}: {e}")

        return None


# Heuristic mapping (reuse-first, non-destructive)

for p in cands:
    if p.endswith(".json") or p.endswith(".jsonl") or p.endswith(".ndjson"):
        obj = try_load_json(p)
        if obj is None:
            continue

        # Try to detect node/edge-like records

        if isinstance(obj, dict):
            rows = [obj]

        else:
            rows = obj if isinstance(obj, list) else []

        for r in rows:
            if not isinstance(r, dict):
                continue

            if {"concept_id", "lemma"}.issubset(r.keys()):
                bundle["nodes"].append(
                    {"id": r.get("concept_id"), "label": r.get("lemma"), "attrs": r}
                )

            elif {"src_concept_id", "dst_concept_id"}.issubset(r.keys()):
                bundle["edges"].append(
                    {
                        "source": r.get("src_concept_id"),
                        "target": r.get("dst_concept_id"),
                        "type": r.get("relation_type", "rel"),
                        "weight": r.get("weight", 0),
                    }
                )

# --- NEW: temporal facet (reuse-first heuristic; mirrors scripts/temporal expectations) ---
temporal_keys = {"ts", "timestamp", "date", "datetime", "period", "year", "month", "day"}
temporal_files, keys_seen = [], set()
for p in cands:
    obj = try_load_json(p)
    if obj is None:
        continue
    sample = obj[0] if isinstance(obj, list) and obj else (obj if isinstance(obj, dict) else None)
    if isinstance(sample, dict):
        ks = {k.lower() for k in sample.keys()}
        hit = temporal_keys & ks
        if hit:
            temporal_files.append(p)
            keys_seen |= hit

if temporal_files:
    bundle["meta"]["temporal"] = {"files": len(temporal_files), "keys": sorted(keys_seen)}


with open(OUTDIR / "bundle.json", "w", encoding="utf-8") as fh:
    json.dump(bundle, fh, ensure_ascii=False)

print(
    f"[adapter] wrote {OUTDIR / 'bundle.json'} with {len(bundle['nodes'])} nodes, {len(bundle['edges'])} edges"
)
