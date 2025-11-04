#!/usr/bin/env python3
"""Temporal analytics and forecasting per ADR-025."""

import json
import numpy as np
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

ENVELOPE_PATH = "share/exports/envelope.json"
TEMPORAL_PATH = "share/exports/temporal_patterns.json"
FORECAST_PATH = "share/exports/forecast.json"

try:
    from statsmodels.tsa.arima.model import ARIMA
    STATS_MODELS_AVAILABLE = True
except ImportError:
    STATS_MODELS_AVAILABLE = False
    print("Warning: statsmodels not available, using simple forecasting")


def load_envelope():
    """Load the current envelope data."""
    if not os.path.exists(ENVELOPE_PATH):
        raise FileNotFoundError(f"Envelope not found at {ENVELOPE_PATH}")
    with open(ENVELOPE_PATH, "r") as f:
        return json.load(f)


def temporal_analysis(nodes, window=10):
    """Perform temporal pattern analysis on node sequence."""
    if not nodes:
        return {"rolling_mean": [], "change_points": [], "metadata": {"series_length": 0}}

    # Extract values (assuming nodes have sequential order and gematria values)
    values = []
    for node in nodes:
        if isinstance(node, dict) and "value" in node:
            values.append(node["value"])
        elif isinstance(node, (int, float)):
            values.append(node)

    if not values:
        return {"rolling_mean": [], "change_points": [], "metadata": {"series_length": 0}}

    values = np.array(values)

    # Rolling window computations
    if len(values) >= window:
        rolling_mean = np.convolve(values, np.ones(window)/window, mode='valid')
    else:
        rolling_mean = [np.mean(values)] * len(values)

    # Simple change point detection (threshold-based)
    change_points = []
    if len(values) > 1:
        std_dev = np.std(values)
        threshold = std_dev * 2  # 2-sigma threshold
        for i in range(1, len(values)):
            if abs(values[i] - values[i-1]) > threshold:
                change_points.append(i)

    # Series metadata
    metadata = {
        "series_length": len(values),
        "window_size": window,
        "volatility": float(np.std(values)) if len(values) > 1 else 0,
        "trend_slope": float(np.polyfit(range(len(values)), values, 1)[0]) if len(values) > 1 else 0
    }

    return {
        "rolling_mean": rolling_mean.tolist(),
        "change_points": change_points,
        "metadata": metadata
    }


def forecast_series(series, horizon=5):
    """Generate forecasts for time series."""
    if not series or len(series) < 3:
        return {"forecast": [], "rmse": 0, "model": "insufficient_data"}

    series = np.array(series)

    if STATS_MODELS_AVAILABLE and len(series) >= 5:
        try:
            # ARIMA forecasting
            model = ARIMA(series, order=(1, 1, 0))
            fit = model.fit()
            forecast = fit.forecast(steps=horizon)

            # Calculate RMSE on fitted values
            fitted = fit.fittedvalues
            if len(fitted) > 0:
                rmse = float(np.sqrt(np.mean((series[len(series)-len(fitted):] - fitted)**2)))
            else:
                rmse = 0

            return {
                "forecast": forecast.tolist(),
                "rmse": rmse,
                "model": "ARIMA",
                "confidence_intervals": []  # Could add prediction intervals
            }
        except Exception as e:
            print(f"ARIMA forecasting failed: {e}, falling back to simple methods")

    # Fallback: Simple moving average
    if len(series) >= 3:
        ma_forecast = [np.mean(series[-3:])] * horizon
        rmse = float(np.std(series))  # Simple error estimate
    else:
        ma_forecast = [series[-1]] * horizon
        rmse = 0

    return {
        "forecast": ma_forecast,
        "rmse": rmse,
        "model": "simple_moving_average"
    }


def save_exports(analysis, forecast):
    """Save temporal analysis and forecast results."""
    # Ensure output directories exist
    os.makedirs(os.path.dirname(TEMPORAL_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(FORECAST_PATH), exist_ok=True)

    with open(TEMPORAL_PATH, "w") as f:
        json.dump(analysis, f, indent=2)

    with open(FORECAST_PATH, "w") as f:
        json.dump(forecast, f, indent=2)


def main():
    """Main execution for temporal analytics."""
    try:
        envelope = load_envelope()
        nodes = envelope.get("nodes", [])

        # Perform temporal analysis
        analysis = temporal_analysis(nodes)

        # Extract series for forecasting
        if nodes:
            series = [node.get("value", 0) if isinstance(node, dict) else node for node in nodes[:100]]  # Limit for performance
            forecast = forecast_series(series)
        else:
            forecast = {"forecast": [], "rmse": 0, "model": "no_data"}

        # Save results
        save_exports(analysis, forecast)

        print("✓ Temporal analytics complete: patterns and forecast exported")
        print(f"  - Patterns: {TEMPORAL_PATH}")
        print(f"  - Forecast: {FORECAST_PATH}")

    except Exception as e:
        print(f"✗ Temporal analytics failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
