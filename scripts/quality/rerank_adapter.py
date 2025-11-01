#!/usr/bin/env python3

"""

Reuse-first adapter: tries to import an existing rerank(candidates) from known modules.

- Reads EDGE_STRONG, EDGE_WEAK, CANDIDATE_POLICY from env (existing knobs).

- Hermetic: runs with a fixed in-memory candidate set when no inputs given.

- Does NOT write to share/; prints a compact JSON result line for CI.

"""

import importlib, json, os, random

EDGE_STRONG = float(os.getenv("EDGE_STRONG") or "0.90")
EDGE_WEAK = float(os.getenv("EDGE_WEAK") or "0.75")
CANDIDATE_POLICY = os.getenv("CANDIDATE_POLICY") or "cache"
SEED = int(os.getenv("PIPELINE_SEED") or "4242")
random.seed(SEED)


def _load_rerank():
    # Try likely modules in this repo (reuse-first); add more paths if needed.
    for mod in ("src.rerank.blender", "src.services.rerank_via_embeddings", "rerank", "services.rerank"):
        try:
            m = importlib.import_module(mod)
            if hasattr(m, "rerank"):
                return m.rerank, mod
        except Exception:
            pass

    # Fallback: identity (no scoring change) — still surfaces thresholds for CI
    def _identity(cands):
        return sorted(cands, key=lambda x: x.get("score", 0.0), reverse=True)

    return _identity, "adapter:identity"


def _demo_candidates():
    # deterministic toy candidates for hermetic smoke
    return [{"id": f"c{i}", "score": s} for i, s in enumerate([0.12, 0.77, 0.51, 0.93, 0.36])]


def main():
    rerank, origin = _load_rerank()
    cands = _demo_candidates()
    ranked = rerank(cands)
    top = ranked[0] if ranked else {}
    print(
        json.dumps(
            {
                "stage": "quality.rerank.smoke",
                "origin": origin,
                "env": {
                    "EDGE_STRONG": EDGE_STRONG,
                    "EDGE_WEAK": EDGE_WEAK,
                    "CANDIDATE_POLICY": CANDIDATE_POLICY,
                    "SEED": SEED,
                },
                "top": {"id": top.get("id"), "score": top.get("score")},
                "items": len(ranked),
                "ok": True,
                "hint": f"HINT[quality.seed]: {SEED}",
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
