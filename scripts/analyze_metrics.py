# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

import json
import os

import numpy as np

from src.graph.metrics import (
    bridge_score,
    cluster_semantic_diversity,
    density,
    diversity_local,
    semantic_cohesion,
)
from src.infra.db import get_gematria_rw
from src.infra.env_loader import ensure_env_loaded

# Load environment variables from .env file
ensure_env_loaded()

TOPK = int(os.getenv("METRICS_CLUSTER_TOPK", 5))
SAMPLE = int(os.getenv("METRICS_SAMPLE_SIZE", 200))


def fetch_embeddings(db):
    rows = list(
        db.execute(
            """
      SELECT n.concept_id, c.cluster_id, n.embedding
      FROM concept_network n
      JOIN concept_clusters c ON c.concept_id = n.concept_id
      WHERE n.embedding IS NOT NULL
    """
        )
    )
    return [(r[0], r[1], np.array(r[2], dtype=float)) for r in rows]


def fetch_edges(db):
    rows = list(db.execute("SELECT source_id, target_id FROM concept_relations"))
    adj = {}
    for s, t in rows:
        adj.setdefault(s, set()).add(t)
        adj.setdefault(t, set()).add(s)
    return adj


if __name__ == "__main__":
    db = get_gematria_rw()
    adj = fetch_edges(db)
    items = fetch_embeddings(db)

    by_cluster = {}
    for cid, cl, vec in items:
        by_cluster.setdefault(cl, []).append((cid, vec))

    # cluster metrics
    for cl, pairs in by_cluster.items():
        ids = [cid for cid, _ in pairs]
        vecs = [v for _, v in pairs]
        n = len(ids)
        e_within = next(
            iter(
                db.execute(
                    """
          SELECT COUNT(*) FROM concept_relations
          WHERE source_id = ANY(%s) AND target_id = ANY(%s)
        """,
                    (ids, ids),
                )
            )
        )[0]
        dens = density(n, e_within)
        sample = vecs if n <= SAMPLE else [vecs[i] for i in np.random.choice(n, SAMPLE, replace=False)]
        div = cluster_semantic_diversity(sample)
        # exemplars by mean cosine to cluster
        means = [(cid, float(np.mean([np.dot(v, u) for u in vecs]))) for cid, v in pairs]
        means.sort(key=lambda x: x[1], reverse=True)
        top = [cid for cid, _ in means[:TOPK]]
        db.execute(
            """
          INSERT INTO cluster_metrics (cluster_id,size,density,modularity,semantic_diversity,top_examples)
          VALUES (%s,%s,%s,NULL,%s,%s)
          ON CONFLICT (cluster_id) DO UPDATE SET
            size=EXCLUDED.size,density=EXCLUDED.density,
            semantic_diversity=EXCLUDED.semantic_diversity,top_examples=EXCLUDED.top_examples,
            updated_at=now()
        """,
            (cl, n, dens, div, top),
        )

    all_vec = {cid: vec for cid, cl, vec in items}

    # concept metrics
    for cid, cl, v in items:
        cluster_ids = [i for i, _ in by_cluster[cl]]
        out_ids = [i for i in all_vec if i not in cluster_ids][:300]
        coh = semantic_cohesion(v, [all_vec[i] for i in cluster_ids if i != cid])
        br = bridge_score(v, [all_vec[i] for i in out_ids])
        neigh = [all_vec[nid] for nid in adj.get(cid, []) if nid in all_vec]
        dloc = diversity_local(neigh)
        db.execute(
            """
          INSERT INTO concept_metrics (concept_id,cluster_id,semantic_cohesion,bridge_score,diversity_local)
          VALUES (%s,%s,%s,%s,%s)
          ON CONFLICT (concept_id) DO UPDATE SET
            cluster_id=EXCLUDED.cluster_id, semantic_cohesion=EXCLUDED.semantic_cohesion,
            bridge_score=EXCLUDED.bridge_score, diversity_local=EXCLUDED.diversity_local,
            updated_at=now()
        """,
            (cid, cl, coh, br, dloc),
        )

    print(json.dumps({"clusters": len(by_cluster), "concepts": len(items)}, indent=2))
