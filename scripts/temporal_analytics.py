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

    return {
        "schema": "temporal-patterns.v1",
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "window_size": window_size,
        "total_nodes": len(nodes),
        "rolling_statistics": rolling_stats,
        "trends": trends,
        "summary": {
            "avg_window_gematria": sum(s["mean_gematria"] for s in rolling_stats) / len(rolling_stats)
            if rolling_stats
            else 0,
            "max_trend_change": max(abs(t["gematria_trend"]) for t in trends) if trends else 0,
            "trend_directions": {
                "increasing": len([t for t in trends if t["direction"] == "increasing"]),
                "decreasing": len([t for t in trends if t["direction"] == "decreasing"]),
            },
        },
    }


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
    rolling_stats = temporal_patterns.get("rolling_statistics", [])

    if len(rolling_stats) < 3:
        return {
            "schema": "pattern-forecast.v1",
            "error": "Insufficient data for forecasting (need at least 3 data points)",
            "forecast_steps": forecast_steps,
        }

    # Simple linear regression for forecasting
    positions = [s["position"] for s in rolling_stats]
    values = [s["mean_gematria"] for s in rolling_stats]

    # Calculate slope and intercept
    n = len(positions)
    sum_x = sum(positions)
    sum_y = sum(values)
    sum_xy = sum(x * y for x, y in zip(positions, values))
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
    for actual, predicted_pos in zip(values, positions):
        predicted = slope * predicted_pos + intercept
        residuals.append(actual - predicted)

    mse = sum(r**2 for r in residuals) / len(residuals) if residuals else 0
    rmse = mse**0.5 if mse >= 0 else 0

    return {
        "schema": "pattern-forecast.v1",
        "forecast_timestamp": datetime.utcnow().isoformat(),
        "model": "linear_regression",
        "training_points": len(rolling_stats),
        "slope": slope,
        "intercept": intercept,
        "forecast_steps": forecast_steps,
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
        "--forecast-only", action="store_true", help="Run forecasting only (requires existing patterns)"
    )

    args = parser.parse_args()

    try:
        if args.forecast_only:
            # Load existing temporal patterns and run forecasting only
            patterns_file = "exports/temporal_patterns.json"
            if not os.path.exists(patterns_file):
                print(
                    json.dumps(
                        {"success": False, "error": "temporal_patterns.json not found. Run analysis first."}, indent=2
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
