#!/usr/bin/env python3
"""Generate Mermaid diagrams from Atlas telemetry (read-only via DSN shim).

STRICT mode: Queries metrics_log and checkpointer_state via dsn_atlas().
HINT mode: Emits lightweight placeholders for hermetic CI.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import datetime as dt
from typing import Tuple, Dict, Any, List

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "atlas"
DOCS.mkdir(parents=True, exist_ok=True)

STRICT = os.getenv("STRICT_ATLAS_DSN") == "1"
WINDOW = os.getenv("ATLAS_WINDOW", "24h")


def now_iso() -> str:
    """RFC3339 timestamp (UTC, no microseconds)."""
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_kpis_json(payload: Dict[str, Any]) -> None:
    """Write KPIs JSON file for UI consumption."""
    (DOCS / "_kpis.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _hint_write(window: str):
    """Hermetic/HINT mode: emit lightweight placeholders so the browser UI renders."""
    _write_kpis_json(
        {
            "mode": "HINT",
            "window": window,
            "ok": True,
            "success": 42,
            "error": 3,
            "generated": now_iso(),
        }
    )
    (DOCS / "execution_live.mmd").write_text(
        "%% generated (HINT) " + now_iso() + "\n"
        "flowchart TD\n"
        "  Ingest-->Normalize-->Enrich-->Persist\n"
        "  Persist-->Index\n"
        '  click Ingest "../evidence/atlas_proof_dsn.html" "Proof DSN"\n'
    )
    (DOCS / "pipeline_flow_historical.mmd").write_text(
        "%% generated (HINT) " + now_iso() + "\n"
        "gantt\n"
        "  dateFormat  YYYY-MM-DD\n"
        f"  title Pipeline ({window})\n"
        "  section ETL\n"
        "  Ingest     :done, des1, 2025-11-04, 1d\n"
        "  Normalize  :done, des2, 2025-11-05, 1d\n"
        "  Enrich     :active, des3, 2025-11-06, 2d\n"
        "  Persist    :         des4, 2025-11-08, 1d\n"
    )
    (DOCS / "dependencies.mmd").write_text(
        "%% generated (HINT) " + now_iso() + "\n"
        "flowchart LR\n"
        "  A[Reader]-->B[Parser]\n"
        "  B-->C[Scorer]\n"
        "  C-->D[Writer]\n"
    )
    (DOCS / "kpis.mmd").write_text(
        f'%% generated (HINT) {now_iso()}\npie title {window} Outcomes\n  "success" : 42\n  "error"   : 3\n'
    )


def _strict_write(conn, window: str):
    """STRICT mode: query DB and generate real Mermaid from telemetry."""
    # pick window expression
    win_expr = {
        "24h": "interval '24 hours'",
        "7d": "interval '7 days'",
        "30d": "interval '30 days'",
    }[window]
    with conn.cursor() as cur:
        # 1) execution_live: nodes seen in window by start->end flows
        cur.execute(
            f"""
            with recent as (
              select distinct node_name, status, started_at, finished_at
              from metrics_log
              where started_at >= now() - {win_expr}
            )
            select distinct node_name
            from recent
            order by 1
        """
        )
        nodes = [r[0] for r in cur.fetchall()]
        # naive linearization for now; later: use real deps if available
        lines = ["%% generated (STRICT) " + now_iso(), "flowchart TD"]
        for i, n in enumerate(nodes):
            if i == 0:
                continue
            a = nodes[i - 1].replace('"', "")
            b = n.replace('"', "")
            lines.append(f'  "{a}" --> "{b}"')
        # Make first node clickable to DSN proof (browser evidence)
        if nodes:
            first_node = nodes[0].replace('"', "")
            lines.append(f'  click "{first_node}" "../evidence/atlas_proof_dsn.html" "Proof DSN"')
        if len(nodes) < 2:
            lines.append('  "Pipeline" --> "No recent nodes"')
        (DOCS / "execution_live.mmd").write_text("\n".join(lines) + "\n")

        # 2) pipeline_flow_historical: simple Gantt by day counts
        cur.execute(
            f"""
          select date_trunc('day', started_at)::date d, count(*) c
          from metrics_log
          where started_at >= now() - {win_expr}
          group by 1 order by 1
        """
        )
        rows = cur.fetchall()
        g = [
            "%% generated (STRICT) " + now_iso(),
            "gantt",
            "  dateFormat  YYYY-MM-DD",
            f"  title Pipeline ({window})",
            "  section Runs",
        ]
        for d, c in rows:
            g.append(f"  Runs_{d} :done, {d}, 1d")
        (DOCS / "pipeline_flow_historical.mmd").write_text("\n".join(g) + "\n")

        # 3) dependencies: TRUE DAG with error-rate coloring
        # Expected tables:
        #   checkpointer_state(parent_node, child_node)
        #   metrics_log(node_name, status, started_at)
        # We color edge A->B by the error rate of executions of node B in the window.
        dep_lines: List[str] = ["%% generated (STRICT) " + now_iso(), "flowchart LR"]
        class_defs = [
            "classDef err-low  stroke:#999,stroke-width:1px;",
            "classDef err-med  stroke:#E3A008,stroke-width:2px;",
            "classDef err-high stroke:#D64545,stroke-width:3px;",
        ]
        try:
            # Pull unique edges
            cur.execute(
                """
              select distinct parent_node, child_node
              from checkpointer_state
              where parent_node is not null and child_node is not null
              limit 2000
            """
            )
            edges: List[Tuple[str, str]] = [(a or "∅", b or "∅") for a, b in cur.fetchall()]
            # Pull error stats for child nodes in window
            cur.execute(
                f"""
              with w as (
                select node_name, status
                from metrics_log
                where started_at >= now() - {win_expr}
              )
              select node_name,
                     sum(case when status='error'   then 1 else 0 end)::int as err,
                     sum(case when status='success' then 1 else 0 end)::int as ok
              from w
              group by 1
            """
            )
            counts: Dict[str, Tuple[int, int]] = {
                r[0]: (int(r[1]), int(r[2])) for r in cur.fetchall()
            }

            # Helper: choose class by error rate
            def edge_class(child: str) -> str:
                err, ok = counts.get(child, (0, 0))
                total = err + ok
                rate = (err / total) if total else 0.0
                if rate >= 0.20:
                    return "err-high"
                if rate >= 0.05:
                    return "err-med"
                return "err-low"

            # Emit edges + per-edge class assignment
            seen = set()
            for a, b in edges:
                a = a.replace('"', "")
                b = b.replace('"', "")
                key = (a, b)
                if key in seen:
                    continue
                seen.add(key)
                dep_lines.append(f'  "{a}" --> "{b}":::${{CLASS:{b}}}')
            # Replace placeholders with concrete class names
            out: List[str] = []
            for line in dep_lines:
                if ":::${CLASS:" in line:
                    child = line.split("${CLASS:")[1].split("}")[0]
                    out.append(line.replace(f":::${{CLASS:{child}}}", f":::{edge_class(child)}"))
                else:
                    out.append(line)
            out.extend(class_defs)
        except Exception:
            out = dep_lines + ['  "Deps" --> "No data"'] + class_defs
        (DOCS / "dependencies.mmd").write_text("\n".join(out) + "\n")

        # 4) kpis: successes vs errors in window
        cur.execute(
            f"""
          select status, count(*) from metrics_log
          where started_at >= now() - {win_expr}
          group by 1
        """
        )
        stats = dict(cur.fetchall())
        succ = int(stats.get("ok", 0))
        err = int(stats.get("error", 0))
        _write_kpis_json(
            {
                "mode": "STRICT",
                "window": window,
                "ok": True,
                "success": succ,
                "error": err,
                "generated": now_iso(),
            }
        )
        pie = [
            "%% generated (STRICT) " + now_iso(),
            f"pie title {window} Outcomes",
            f'  "success" : {succ}',
            f'  "error"   : {err}',
        ]
        (DOCS / "kpis.mmd").write_text("\n".join(pie) + "\n")


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser()
    p.add_argument("--window", choices=["24h", "7d", "30d"], default=WINDOW)
    return p.parse_args()


def main():
    """Main entry point: DSN centralized; never touch env here directly."""
    args = _parse_args()
    try:
        from gemantria.dsn import dsn_atlas

        dsn = dsn_atlas()
    except Exception:
        dsn = ""
    if not dsn or not STRICT:
        _hint_write(args.window)
        print(json.dumps({"mode": "HINT", "ok": True, "window": args.window}))
        return 0
    try:
        import psycopg

        with psycopg.connect(dsn) as conn:
            _strict_write(conn, args.window)
        print(json.dumps({"mode": "STRICT", "ok": True, "window": args.window}))
        return 0
    except Exception as e:
        # Never print DSN; safe error
        _hint_write(args.window)
        print(
            json.dumps(
                {
                    "mode": "HINT",
                    "ok": True,
                    "window": args.window,
                    "note": "fallback: " + e.__class__.__name__,
                }
            )
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
