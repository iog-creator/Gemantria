# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

import numpy as np


def _cos(a, b):
    return float(np.dot(a, b))


def cluster_semantic_diversity(vecs):
    n = len(vecs)
    if n < 2:
        return 0.0
    s = c = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            s += _cos(vecs[i], vecs[j])
            c += 1
    return max(0.0, 1.0 - (s / max(c, 1)))


def density(n_nodes, n_edges):
    if n_nodes < 2:
        return 0.0
    return float(n_edges / (n_nodes * (n_nodes - 1) / 2))


def semantic_cohesion(v, cluster_vecs):
    return 0.0 if not cluster_vecs else float(np.mean([_cos(v, u) for u in cluster_vecs]))


def bridge_score(v, out_cluster_vecs):
    return 0.0 if not out_cluster_vecs else float(np.mean([_cos(v, u) for u in out_cluster_vecs]))


def diversity_local(neigh_vecs):
    n = len(neigh_vecs)
    if n < 2:
        return 0.0
    s = c = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            s += _cos(neigh_vecs[i], neigh_vecs[j])
            c += 1
    return max(0.0, 1.0 - (s / max(c, 1)))
