#!/usr/bin/env python3
import json, os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"

def env_float(name, default):
    try: return float(os.environ.get(name, default))
    except Exception: return float(default)

def env_int(name, default):
    try: return int(os.environ.get(name, default))
    except Exception: return int(default)

def main() -> int:
    # thresholds
    max_missing_pct = env_float("Q_MAX_MISSING_RERANK_PCT", 0.0)
    min_strong_or_weak = env_int("Q_MIN_STRONG_OR_WEAK", 1)
    require_nonzero_eig = env_int("Q_REQUIRE_NONZERO_EIG", 1) != 0

    # load inputs
    graph = json.loads((EVAL/"graph_latest.json").read_text(encoding="utf-8"))
    centrality = json.loads((EVAL/"centrality.json").read_text(encoding="utf-8"))

    edges = graph.get("edges", [])
    n_edges = len(edges)
    missing = sum(1 for e in edges if e.get("rerank") in (None, ""))
    strong = sum(1 for e in edges if e.get("class") == "strong")
    weak   = sum(1 for e in edges if e.get("class") == "weak")
    other  = n_edges - strong - weak
    miss_pct = (100.0 * missing / n_edges) if n_edges else 0.0

    # eigenvector nonzero?
    eig_nonzero = any((v.get("eigenvector") or 0.0) > 0.0 for v in centrality.values())

    # report
    lines = []
    lines.append(f"edges={n_edges} strong={strong} weak={weak} other={other}")
    lines.append(f"missing_rerank={missing} ({miss_pct:.2f}%)")
    lines.append(f"eigenvector_nonzero={eig_nonzero}")
    lines.append(f"thresholds: max_missing_rerank_pct={max_missing_pct} min_strong_or_weak={min_strong_or_weak} require_nonzero_eig={require_nonzero_eig}")

    failed = False
    if miss_pct > max_missing_pct:
        lines.append("FAIL: missing_rerank_pct above threshold"); failed = True
    if (strong + weak) < min_strong_or_weak:
        lines.append("FAIL: not enough strong/weak edges"); failed = True
    if require_nonzero_eig and not eig_nonzero:
        lines.append("FAIL: eigenvector centrality all zero"); failed = True

    out = "\n".join(lines) + "\n"
    (EVAL/"quality_report.txt").write_text(out, encoding="utf-8")
    print(out, end="")

    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
