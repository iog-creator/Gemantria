from __future__ import annotations

import os

import psycopg
from fastapi import FastAPI, Response

PROM_EXPORTER_ENABLED = os.getenv("PROM_EXPORTER_ENABLED", "0") not in (
    "0",
    "false",
    "False",
)
PROM_EXPORTER_PORT = int(os.getenv("PROM_EXPORTER_PORT", "9108"))
DSN = os.getenv("GEMATRIA_DSN")

app = FastAPI(title="Gemantria Metrics Exporter")


def _fetch():
    if not DSN:
        return {}
    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT node, calls, avg_ms, p50_ms, p90_ms, p95_ms, p99_ms FROM v_node_latency_7d"
        )
        latency = cur.fetchall()
        cur.execute(
            "SELECT node, COALESCE(SUM(items_out),0) FROM v_node_throughput_24h GROUP BY node"
        )
        thr = dict(cur.fetchall())
        cur.execute("SELECT COALESCE(SUM(error_count),0) FROM v_recent_errors_7d")
        total_err = cur.fetchone()[0]
    return {"latency": latency, "throughput": thr, "total_errors": total_err}


@app.get("/metrics")
def metrics():
    data = _fetch()
    lines = []

    # Counters/Gauges following OpenMetrics text format
    lines.append("# HELP gemantria_total_errors_7d Total errors over the last 7 days.")
    lines.append("# TYPE gemantria_total_errors_7d gauge")
    lines.append(f"gemantria_total_errors_7d {data.get('total_errors',0)}")

    lines.append(
        "# HELP gemantria_node_items_out_24h Total items_out over the last 24 hours by node."
    )
    lines.append("# TYPE gemantria_node_items_out_24h counter")
    for node, total in data.get("throughput", {}).items():
        lines.append(f'gemantria_node_items_out_24h{{node="{node}"}} {int(total)}')

    lines.append(
        "# HELP gemantria_node_latency_ms_7d Latency statistics over the last 7 days by node."
    )
    lines.append("# TYPE gemantria_node_latency_ms_7d summary")
    for node, calls, avg_ms, p50, p90, p95, p99 in data.get("latency", []):
        lines.append(
            f'gemantria_node_latency_ms_7d_sum{{node="{node}"}} {avg_ms * max(calls,1)}'
        )
        lines.append(f'gemantria_node_latency_ms_7d_count{{node="{node}"}} {calls}')
        lines.append(
            f'gemantria_node_latency_ms_7d_quantile{{quantile="0.5",node="{node}"}} {p50}'
        )
        lines.append(
            f'gemantria_node_latency_ms_7d_quantile{{quantile="0.9",node="{node}"}} {p90}'
        )
        lines.append(
            f'gemantria_node_latency_ms_7d_quantile{{quantile="0.95",node="{node}"}} {p95}'
        )
        lines.append(
            f'gemantria_node_latency_ms_7d_quantile{{quantile="0.99",node="{node}"}} {p99}'
        )

    body = "\n".join(lines) + "\n"
    return Response(content=body, media_type="text/plain; version=0.0.4; charset=utf-8")


# Optional: local runner
if __name__ == "__main__" and PROM_EXPORTER_ENABLED:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PROM_EXPORTER_PORT)
