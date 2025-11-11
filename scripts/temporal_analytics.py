# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Phase-8 Temporal Analytics Implementation

Provides predictive temporal analytics with rolling windows and forecasting
capabilities per MASTER_PLAN.md Phase-8 requirements.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

from src.infra.env_loader import ensure_env_loaded

# Load environment
ensure_env_loaded()


def _iso_now():
    return datetime.now(datetime.timezone.utc).isoformat()


def _write_json(path, obj):
    import pathlib

    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def analyze_temporal_patterns(graph_data: Dict[str, Any], window_size: int = 10) -> Dict[str, Any]:
    """
    Analyze temporal patterns in concept network data.
    Implements Phase-8 rolling window analytics with trend detection.
    Args:
        graph_data: Graph data with nodes and edges
        window_size: Size of rolling analysis window
    Returns:
        Temporal analysis results
    """
    book = os.getenv("BOOK", "Genesis")
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    # Extract temporal features from nodes (assuming verse/chapter progression)
    temporal_features = []
    for node in nodes:
        # Extract position information (verse/chapter indices)
        position = 0
        if "position" in node:
            position = node["position"]
        elif "verse" in node and "chapter" in node:
            # Calculate approximate position
            position = node.get("chapter", 0) * 1000 + node.get("verse", 0)

        temporal_features.append(
            {
                "id": node["id"],
                "position": position,
                "gematria": node.get("gematria", 0),
                "class": node.get("class", "unknown"),
                "surface": node.get("surface", ""),
            }
        )

    # Sort by position for temporal analysis
    temporal_features.sort(key=lambda x: x["position"])

    # Calculate rolling statistics
    rolling_stats = []
    for i in range(len(temporal_features) - window_size + 1):
        window = temporal_features[i : i + window_size]

        # Calculate window statistics
        gematria_values = [f["gematria"] for f in window if f["gematria"] > 0]
        if gematria_values:
            stats = {
                "window_start": window[0]["position"],
                "window_end": window[-1]["position"],
                "mean_gematria": sum(gematria_values) / len(gematria_values),
                "max_gematria": max(gematria_values),
                "min_gematria": min(gematria_values),
                "gematria_range": max(gematria_values) - min(gematria_values),
                "node_count": len(window),
                "position": window[len(window) // 2]["position"],  # Center position
            }
            rolling_stats.append(stats)

    # Detect trends (simple slope calculation)
    trends = []
    for i in range(1, len(rolling_stats)):
        prev = rolling_stats[i - 1]
        curr = rolling_stats[i]

        trend = {
            "from_position": prev["position"],
            "to_position": curr["position"],
            "gematria_trend": curr["mean_gematria"] - prev["mean_gematria"],
            "range_trend": curr["gematria_range"] - prev["gematria_range"],
            "direction": "increasing" if curr["mean_gematria"] > prev["mean_gematria"] else "decreasing",
        }
        trends.append(trend)

    # Transform to temporal schema format
    temporal_patterns_list = []
    if rolling_stats:
        # Aggregate series for gematria mean over positions
        values = [s["mean_gematria"] for s in rolling_stats]
        # Note: detect_change_points would require pandas - disabled for now
        change_points = []
        temporal_pattern = {
            "series_id": "aggregate_gematria",
            "unit": "position",
            "window": window_size,
            "start_index": min([s["window_start"] for s in rolling_stats]) if rolling_stats else 0,
            "end_index": max([s["window_end"] for s in rolling_stats]) if rolling_stats else 0,
            "metric": "gematria",
            "values": values,
            "method": "rolling_mean",
            "book": book,
            "zscore_values": [],  # Could compute if needed
            "change_points": change_points,
            "seasonality": "none",  # Placeholder
            "metadata": {
                "total_nodes": len(nodes),
                "window_count": len(rolling_stats),
                "trend_summary": {
                    "increasing": len([t for t in trends if t["direction"] == "increasing"]),
                    "decreasing": len([t for t in trends if t["direction"] == "decreasing"]),
                    "max_change": max([abs(t["gematria_trend"]) for t in trends]) if trends else 0,
                },
            },
        }
        temporal_patterns_list.append(temporal_pattern)

    metadata = {
        "generated_at": _iso_now(),
        "analysis_parameters": {
            "default_unit": "position",
            "default_window": window_size,
            "min_series_length": 3,
        },
        "total_series": len(temporal_patterns_list),
        "books_analyzed": [book],
    }

    tp = {"temporal_patterns": temporal_patterns_list, "metadata": metadata}

    _write_json("share/exports/temporal_patterns.json", tp)
    return tp


def generate_forecast(temporal_patterns: Dict[str, Any], forecast_steps: int = 5) -> Dict[str, Any]:
    """
    Generate simple forecasting predictions based on temporal patterns.
    Implements Phase-8 forecasting baseline with naive extrapolation.
    Args:
        temporal_patterns: Output from analyze_temporal_patterns
        forecast_steps: Number of steps to forecast
    Returns:
        Forecast results with predictions and confidence intervals
    """
    rolling_stats = temporal_patterns.get(
        "rolling_statistics", []
    )  # Note: now it's patterns, but keep for compatibility

    if len(rolling_stats) < 3:
        fc = {
            "schema": "pattern-forecast.v1",
            "generated_at": _iso_now(),
            "forecast_steps": forecast_steps,
            "notes": "Insufficient data → placeholder forecast (schema not enforced)",
            "error": "Insufficient data for forecasting (need at least 3 data points)",
        }
    else:
        # Simple linear regression for forecasting
        positions = [s["position"] for s in rolling_stats]
        values = [s["mean_gematria"] for s in rolling_stats]

        # Calculate slope and intercept
        n = len(positions)
        sum_x = sum(positions)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(positions, values, strict=True))
        sum_xx = sum(x * x for x in positions)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n

        # Generate forecasts
        last_position = max(positions)
        position_step = (max(positions) - min(positions)) / len(positions) if len(positions) > 1 else 1

        forecasts = []
        for i in range(1, forecast_steps + 1):
            forecast_pos = last_position + (position_step * i)
            predicted_value = slope * forecast_pos + intercept

            # Simple confidence interval (placeholder - could be improved)
            confidence_range = abs(slope) * position_step * 0.5  # Rough estimate

            forecasts.append(
                {
                    "step": i,
                    "position": forecast_pos,
                    "predicted_gematria": predicted_value,
                    "confidence_lower": predicted_value - confidence_range,
                    "confidence_upper": predicted_value + confidence_range,
                    "confidence_interval": confidence_range * 2,
                }
            )

        # Calculate forecast quality metrics
        residuals = []
        for actual, predicted_pos in zip(values, positions, strict=True):
            predicted = slope * predicted_pos + intercept
            residuals.append(actual - predicted)

        mse = sum(r**2 for r in residuals) / len(residuals) if residuals else 0
        rmse = mse**0.5 if mse >= 0 else 0

        fc = {
            "schema": "pattern-forecast.v1",
            "generated_at": _iso_now(),
            "forecast_steps": forecast_steps,
            "model": "linear_regression",
            "training_points": len(rolling_stats),
            "slope": slope,
            "intercept": intercept,
            "forecasts": forecasts,
            "quality_metrics": {
                "mse": mse,
                "rmse": rmse,
                "r_squared": 1 - (sum(r**2 for r in residuals) / sum((y - sum_y / n) ** 2 for y in values))
                if values
                else 0,
            },
            "trend_direction": "increasing" if slope > 0 else "decreasing",
            "trend_strength": abs(slope),
        }

    _write_json("share/exports/pattern_forecast.json", fc)
    return fc


def run_phase8_analysis(book: str = "Genesis") -> Dict[str, Any]:
    """
    Run complete Phase-8 temporal analytics pipeline.

    Args:
        book: Book to analyze

    Returns:
        Complete Phase-8 analysis results
    """
    print(f"[Phase-8] Starting temporal analytics for {book}")

    # Load graph data
    graph_file = "exports/graph_latest.json"
    if not os.path.exists(graph_file):
        return {"success": False, "error": f"Graph data not found: {graph_file}", "book": book}

    with open(graph_file, encoding="utf-8") as f:
        graph_data = json.load(f)

    print(f"[Phase-8] Loaded graph with {len(graph_data.get('nodes', []))} nodes")

    # Run temporal pattern analysis
    temporal_patterns = analyze_temporal_patterns(graph_data, window_size=10)
    print(f"[Phase-8] Generated {len(temporal_patterns.get('rolling_statistics', []))} rolling statistics")

    # Generate forecasts
    forecast = generate_forecast(temporal_patterns, forecast_steps=5)
    print(f"[Phase-8] Generated {len(forecast.get('forecasts', []))} forecast steps")

    # Save results
    results = {
        "success": True,
        "book": book,
        "timestamp": datetime.utcnow().isoformat(),
        "temporal_patterns": temporal_patterns,
        "forecast": forecast,
    }

    # Write individual files for compatibility
    with open("exports/temporal_patterns.json", "w", encoding="utf-8") as f:
        json.dump(temporal_patterns, f, indent=2, ensure_ascii=False)

    with open("exports/pattern_forecast.json", "w", encoding="utf-8") as f:
        json.dump(forecast, f, indent=2, ensure_ascii=False)

    print("[Phase-8] Results saved to exports/temporal_patterns.json and exports/pattern_forecast.json")

    return results


def main():
    """CLI entry point for Phase-8 temporal analytics."""
    import argparse

    parser = argparse.ArgumentParser(description="Phase-8 Temporal Analytics")
    parser.add_argument("--book", default="Genesis", help="Book to analyze")
    parser.add_argument("--window-size", type=int, default=10, help="Rolling window size")
    parser.add_argument("--forecast-steps", type=int, default=5, help="Number of forecast steps")
    parser.add_argument(
        "--forecast-only",
        action="store_true",
        help="Run forecasting only (requires existing patterns)",
    )

    args = parser.parse_args()

    try:
        if args.forecast_only:
            # Load existing temporal patterns and run forecasting only
            patterns_file = "exports/temporal_patterns.json"
            if not os.path.exists(patterns_file):
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": "temporal_patterns.json not found. Run analysis first.",
                        },
                        indent=2,
                    )
                )
                sys.exit(1)

            with open(patterns_file, encoding="utf-8") as f:
                temporal_patterns = json.load(f)

            forecast = generate_forecast(temporal_patterns, args.forecast_steps)

            with open("exports/pattern_forecast.json", "w", encoding="utf-8") as f:
                json.dump(forecast, f, indent=2, ensure_ascii=False)

            results = {"success": True, "forecast": forecast}
        else:
            results = run_phase8_analysis(args.book)

        print(json.dumps(results, indent=2, default=str))
        sys.exit(0 if results["success"] else 1)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
