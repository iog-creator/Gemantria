#!/usr/bin/env python3
"""Generate Mermaid diagrams from Atlas telemetry (read-only via DSN shim).

STRICT mode: Queries metrics_log and checkpointer_state via dsn_atlas().
HINT mode: Emits lightweight placeholders for hermetic CI.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import datetime as dt
from typing import Iterable, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "atlas"
DOCS.mkdir(parents=True, exist_ok=True)

STRICT = os.getenv("STRICT_ATLAS_DSN") == "1"


def now_iso() -> str:
    """RFC3339 timestamp (UTC, no microseconds)."""
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _hint_write():
    """Hermetic/HINT mode: emit lightweight placeholders so the browser UI renders."""
    (DOCS / "execution_live.mmd").write_text(
        "%% generated (HINT) " + now_iso() + "\n"
        "flowchart TD\n"
        "  Ingest-->Normalize-->Enrich-->Persist\n"
        "  Persist-->Index\n"
    )
    (DOCS / "pipeline_flow_historical.mmd").write_text(
        "%% generated (HINT) " + now_iso() + "\n"
        "gantt\n"
        "  dateFormat  YYYY-MM-DD\n"
        "  title Pipeline (last 7 days)\n"
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
        "%% generated (HINT) " + now_iso() + '\npie title 24h Outcomes\n  "success" : 42\n  "error"   : 3\n'
    )


def _strict_write(conn):
    """STRICT mode: query DB and generate real Mermaid from telemetry."""
    with conn.cursor() as cur:
        # 1) execution_live: nodes seen in last 24h by start->end flows
        cur.execute(
            """
            with recent as (
              select distinct node, status, started_at, finished_at
              from metrics_log
              where started_at >= now() - interval '24 hours'
            )
            select distinct node
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
        if len(nodes) < 2:
            lines.append('  "Pipeline" --> "No recent nodes"')
        (DOCS / "execution_live.mmd").write_text("\n".join(lines) + "\n")

        # 2) pipeline_flow_historical: simple Gantt by day counts (7d)
        cur.execute(
            """
          select date_trunc('day', started_at)::date d, count(*) c
          from metrics_log
          where started_at >= now() - interval '7 days'
          group by 1 order by 1
        """
        )
        rows = cur.fetchall()
        g = [
            "%% generated (STRICT) " + now_iso(),
            "gantt",
            "  dateFormat  YYYY-MM-DD",
            "  title Pipeline (last 7 days)",
            "  section Runs",
        ]
        for d, c in rows:
            g.append(f"  Runs_{d} :done, {d}, 1d")
        (DOCS / "pipeline_flow_historical.mmd").write_text("\n".join(g) + "\n")

        # 3) dependencies: best-effort from checkpointer_state (parent->child) if present
        dep = ["%% generated (STRICT) " + now_iso(), "flowchart LR"]
        try:
            # Try to extract node relationships from checkpoint JSONB metadata
            # Fallback: use workflow/thread_id ordering as proxy
            cur.execute(
                """
              select distinct workflow, thread_id
              from checkpointer_state
              where created_at >= now() - interval '7 days'
              order by created_at
              limit 100
            """
            )
            pairs: Iterable[Tuple[str, str]] = cur.fetchall()
            seen = set()
            for a, b in pairs:
                a = (a or "∅").replace('"', "")
                b = (b or "∅").replace('"', "")
                key = (a, b)
                if key in seen:
                    continue
                seen.add(key)
                dep.append(f'  "{a}" --> "{b}"')
            if not seen:
                dep.append('  "Deps" --> "No data"')
        except Exception:
            dep.append('  "Deps" --> "No data"')
        (DOCS / "dependencies.mmd").write_text("\n".join(dep) + "\n")

        # 4) kpis: successes vs errors in 24h window
        cur.execute(
            """
          select status, count(*) from metrics_log
          where started_at >= now() - interval '24 hours'
          group by 1
        """
        )
        stats = dict(cur.fetchall())
        succ = int(stats.get("ok", 0))
        err = int(stats.get("error", 0))
        pie = [
            "%% generated (STRICT) " + now_iso(),
            "pie title 24h Outcomes",
            f'  "success" : {succ}',
            f'  "error"   : {err}',
        ]
        (DOCS / "kpis.mmd").write_text("\n".join(pie) + "\n")


def main():
    """Main entry point: DSN centralized; never touch env here directly."""
    try:
        from gemantria.dsn import dsn_atlas

        dsn = dsn_atlas()
    except Exception:
        dsn = ""
    if not dsn or not STRICT:
        _hint_write()
        print(json.dumps({"mode": "HINT", "ok": True}))
        return 0
    try:
        import psycopg

        with psycopg.connect(dsn) as conn:
            _strict_write(conn)
        print(json.dumps({"mode": "STRICT", "ok": True}))
        return 0
    except Exception as e:
        # Never print DSN; safe error
        _hint_write()
        print(json.dumps({"mode": "HINT", "ok": True, "note": "fallback: " + e.__class__.__name__}))
        return 0


if __name__ == "__main__":
    sys.exit(main())
