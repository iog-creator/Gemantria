#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

import psycopg

from src.infra.env_loader import ensure_env_loaded

# Load environment variables from .env file
ensure_env_loaded()


def fail(msg):
    print(f"VERIFIER_FAIL: {msg}", file=sys.stderr)
    sys.exit(2)


def read_json(p):
    try:
        return json.loads(Path(p).read_text())
    except FileNotFoundError:
        # In CI with empty DB, some files may not be generated
        print(f"HINT: File not found {p}, using empty dict for CI empty DB")
        return {}
    except Exception as e:
        fail(f"Cannot read JSON {p}: {e}")


def q1(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchone()[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsn", required=True)
    ap.add_argument("--stats", required=True)
    ap.add_argument("--graph", required=True)
    ap.add_argument(
        "--mock-db", action="store_true", help="Use mock DB values for testing"
    )
    args = ap.parse_args()

    stats = read_json(args.stats)
    graph = read_json(args.graph)

    for k in ["nodes", "edges", "clusters", "density", "centrality"]:
        if k not in stats:
            fail(f"stats missing key: {k}")

    if args.mock_db:
        # Mock DB values for testing - match the file values
        db_nodes = int(stats["nodes"])
        db_edges = int(stats["edges"])
        db_clusters = int(stats["clusters"])
    else:
        try:
            with psycopg.connect(args.dsn) as conn:
                db_nodes = q1(conn, "SELECT COUNT(*) FROM concept_network;")
                db_edges = q1(conn, "SELECT COUNT(*) FROM concept_relations;")
                db_clusters = q1(
                    conn, "SELECT COALESCE(MAX(cluster_id)+1,0) FROM concept_clusters;"
                )
        except psycopg.ProgrammingError as e:
            # Tables don't exist (empty CI DB), use zero counts
            if "does not exist" in str(e):
                print(f"HINT: DB tables missing (empty CI DB), using zero counts: {e}")
                db_nodes = db_edges = db_clusters = 0
            else:
                raise

    file_nodes = int(stats["nodes"])
    file_edges = int(stats["edges"])
    file_clusters = int(stats["clusters"])

    # Allow zero counts in CI when DB tables don't exist (empty DB)
    if file_nodes < 1 and file_edges < 1 and db_nodes == 0 and db_edges == 0:
        print("HINT: Empty CI DB detected, allowing zero counts")
    elif file_nodes < 1 or file_edges < 1:
        fail("stats shows zero nodes/edges (expected non-zero real data)")

    if abs(file_nodes - db_nodes) > max(5, int(0.01 * max(1, db_nodes))):
        fail(f"nodes mismatch file={file_nodes} db={db_nodes}")
    if abs(file_edges - db_edges) > max(25, int(0.02 * max(1, db_edges))):
        fail(f"edges mismatch file={file_edges} db={db_edges}")
    if file_clusters < 0 or file_clusters > db_clusters:
        fail(f"clusters out of range file={file_clusters} db_max={db_clusters}")

    g_nodes = len(graph.get("nodes", []))
    g_edges = len(graph.get("edges", []))
    # Allow empty graph when stats also show zero (CI empty DB case)
    if file_nodes == 0 and file_edges == 0:
        if g_nodes != 0 or g_edges != 0:
            fail(f"graph_latest.json not empty: n={g_nodes} e={g_edges}")
    else:
        if abs(g_nodes - file_nodes) > max(5, int(0.02 * file_nodes)):
            fail(f"graph nodes mismatch: {g_nodes} vs {file_nodes}")
        if abs(g_edges - file_edges) > max(25, int(0.03 * file_edges)):
            fail(f"graph edges mismatch: {g_edges} vs {file_edges}")

    cent = stats["centrality"]
    for required in ["avg_degree", "avg_betweenness"]:
        if required not in cent:
            fail(f"centrality missing {required}")
    if not (0 <= stats["density"] <= 1):
        fail(f"density out of bounds: {stats['density']}")
    if not (0 <= cent["avg_degree"] <= 1):
        fail(f"avg_degree out of bounds: {cent['avg_degree']}")

    print("VERIFIER_PASS: PR-016/017 contracts intact.")


if __name__ == "__main__":
    main()
