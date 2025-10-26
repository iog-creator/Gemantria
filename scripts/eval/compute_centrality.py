#!/usr/bin/env python3
import json, pathlib, sys
import networkx as nx

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
GRAPH = EVAL / "graph_latest.json"
CENT  = EVAL / "centrality.json"

def main() -> int:
    if not GRAPH.exists():
        print("[centrality] missing graph:", GRAPH.relative_to(ROOT)); return 2
    data = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    id_set = {n["id"] for n in nodes if "id" in n}
    G = nx.Graph()
    for n in nodes:
        nid = n.get("id")
        if nid: G.add_node(nid)
    for e in edges:
        a, b = e.get("src"), e.get("dst")
        if a in id_set and b in id_set:
            w = e.get("edge_strength") or e.get("cosine") or 0.0
            try: w = float(w)
            except Exception: w = 0.0
            G.add_edge(a, b, weight=max(0.0, min(1.0, w)))
    if G.number_of_nodes() == 0:
        print("[centrality] no nodes"); return 3
    deg = nx.degree_centrality(G)
    bet = nx.betweenness_centrality(G, weight="weight", normalized=True)
    try:
        eig = nx.eigenvector_centrality(G, weight="weight", max_iter=1000)
    except Exception:
        eig = {n: 0.0 for n in G.nodes()}
    out = {n: {
        "degree": float(deg.get(n, 0.0)),
        "betweenness": float(bet.get(n, 0.0)),
        "eigenvector": float(eig.get(n, 0.0)),
    } for n in id_set}
    CENT.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[centrality] wrote {CENT.relative_to(ROOT)}; nodes={len(out)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
