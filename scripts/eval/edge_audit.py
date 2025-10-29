#!/usr/bin/env python3
"""
Edge Audit Script - Detect outliers in edge strengths using z-score and IQR methods.

This script analyzes the semantic network edges for anomalous strength values that may
indicate data quality issues or network problems. It uses both statistical methods
to identify potential outliers for manual review.
"""

import json
import pathlib
import statistics as st
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
GRAPH = EVAL / "graph_latest.json"
OUT = EVAL / "edge_audit.json"


def emit_hint(msg: str) -> None:
    """Emit a standardized hint for CI visibility."""
    print(f"HINT: {msg}")


def compute_zscore_outliers(
    values: list[float], threshold: float = 3.0
) -> dict[str, Any]:
    """
    Detect outliers using z-score method.

    Args:
        values: List of numeric values to analyze
        threshold: Z-score threshold (default 3.0 = 99.7% confidence)

    Returns:
        Dict with outlier statistics and flagged values
    """
    if len(values) < 2:
        return {
            "n_outliers": 0,
            "outliers": [],
            "method": "zscore",
            "threshold": threshold,
        }

    mean_val = st.fmean(values)
    stdev = st.pstdev(values)

    if stdev == 0:
        return {
            "n_outliers": 0,
            "outliers": [],
            "method": "zscore",
            "threshold": threshold,
        }

    outliers = []
    for i, val in enumerate(values):
        zscore = abs(val - mean_val) / stdev
        if zscore > threshold:
            outliers.append(
                {
                    "index": i,
                    "value": val,
                    "zscore": round(zscore, 3),
                    "deviation": round(val - mean_val, 6),
                }
            )

    return {
        "n_outliers": len(outliers),
        "outliers": outliers,
        "method": "zscore",
        "threshold": threshold,
        "mean": round(mean_val, 6),
        "stdev": round(stdev, 6),
    }


def compute_iqr_outliers(
    values: list[float], multiplier: float = 1.5
) -> dict[str, Any]:
    """
    Detect outliers using IQR (Interquartile Range) method.

    Args:
        values: List of numeric values to analyze
        multiplier: IQR multiplier (default 1.5 = standard outlier detection)

    Returns:
        Dict with outlier statistics and flagged values
    """
    if len(values) < 4:
        return {
            "n_outliers": 0,
            "outliers": [],
            "method": "iqr",
            "multiplier": multiplier,
        }

    sorted_vals = sorted(values)
    n = len(sorted_vals)

    # Calculate quartiles
    q1_idx = int(n * 0.25)
    q3_idx = int(n * 0.75)

    q1 = sorted_vals[q1_idx]
    q3 = sorted_vals[q3_idx]
    iqr = q3 - q1

    lower_bound = q1 - (multiplier * iqr)
    upper_bound = q3 + (multiplier * iqr)

    outliers = []
    for i, val in enumerate(values):
        if val < lower_bound or val > upper_bound:
            outliers.append(
                {
                    "index": i,
                    "value": val,
                    "bound": "lower" if val < lower_bound else "upper",
                    "threshold": round(
                        lower_bound if val < lower_bound else upper_bound, 6
                    ),
                    "deviation": round(
                        val - (lower_bound if val < lower_bound else upper_bound), 6
                    ),
                }
            )

    return {
        "n_outliers": len(outliers),
        "outliers": outliers,
        "method": "iqr",
        "multiplier": multiplier,
        "q1": round(q1, 6),
        "q3": round(q3, 6),
        "iqr": round(iqr, 6),
        "lower_bound": round(lower_bound, 6),
        "upper_bound": round(upper_bound, 6),
    }


def main() -> int:
    """Main audit function."""
    emit_hint("eval: auditing edges for anomalies")

    if not GRAPH.exists():
        print("[edge_audit] missing graph file")
        return 2

    # Load graph data
    data = json.loads(GRAPH.read_text(encoding="utf-8"))
    edges = data.get("edges", [])

    if not edges:
        print("[edge_audit] no edges found in graph")
        return 2

    # Extract edge strengths
    strengths = []
    for edge in edges:
        strength = edge.get("strength")
        if strength is not None:
            try:
                strengths.append(float(strength))
            except (ValueError, TypeError):
                continue

    if not strengths:
        print("[edge_audit] no valid edge strengths found")
        return 2

    # Perform outlier detection
    zscore_result = compute_zscore_outliers(strengths)
    iqr_result = compute_iqr_outliers(strengths)

    # Combine results
    audit_result = {
        "metadata": {
            "total_edges": len(edges),
            "valid_strengths": len(strengths),
            "strength_range": {
                "min": round(min(strengths), 6),
                "max": round(max(strengths), 6),
                "mean": round(st.fmean(strengths), 6),
                "median": round(st.median(strengths), 6),
            },
        },
        "zscore_analysis": zscore_result,
        "iqr_analysis": iqr_result,
        "summary": {
            "total_anomalous": zscore_result["n_outliers"] + iqr_result["n_outliers"],
            "zscore_anomalies": zscore_result["n_outliers"],
            "iqr_anomalies": iqr_result["n_outliers"],
            "anomaly_rate_percent": round(
                (
                    (zscore_result["n_outliers"] + iqr_result["n_outliers"])
                    / len(strengths)
                )
                * 100,
                2,
            ),
        },
    }

    # Write results
    OUT.write_text(json.dumps(audit_result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[edge_audit] wrote {OUT.relative_to(ROOT)}")

    # Summary output for CI
    total_anomalous = audit_result["summary"]["total_anomalous"]
    anomaly_rate = audit_result["summary"]["anomaly_rate_percent"]

    if total_anomalous > 0:
        print(
            f"[edge_audit] found {total_anomalous} anomalous edges ({anomaly_rate}% of total)"
        )
        print(f"[edge_audit] z-score anomalies: {zscore_result['n_outliers']}")
        print(f"[edge_audit] IQR anomalies: {iqr_result['n_outliers']}")
    else:
        print("[edge_audit] no anomalous edges detected")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
