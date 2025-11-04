#!/usr/bin/env python3
"""
Gemantria Analytics API Server

Provides REST API endpoints for accessing correlation and pattern analytics data.
Serves the exported JSON files from the analytics pipeline for web UI consumption.

Usage:
    python -m src.services.api_server
    # Or: uvicorn src.services.api_server:app --host 0.0.0.0 --port 8000
"""

import json
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.infra.env_loader import ensure_env_loaded
from src.infra.structured_logger import get_logger

# Load environment variables
ensure_env_loaded()

# Initialize logger
LOG = get_logger("api_server")


# --- DTOs (public API surface) -------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    export_directory: str
    files: dict[str, dict[str, Any]]
    timestamp: float | None = None


class APIInfo(BaseModel):
    name: str
    version: str
    description: str
    endpoints: dict[str, str]


class FilteredResponse(BaseModel):
    data: list[dict[str, Any]]
    metadata: dict[str, Any]
    filtered_count: int
    applied_filters: dict[str, Any]


class NetworkResponse(BaseModel):
    center_concept: str
    connections: list[dict[str, Any]]
    network_stats: dict[str, Any]
    metadata: dict[str, Any]


# FastAPI app setup
app = FastAPI(
    title="Gemantria Analytics API",
    description="REST API for accessing gematria correlation and pattern analytics data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for web UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files from exports directory
export_dir = os.getenv("EXPORT_DIR", "exports")
if Path(export_dir).exists():
    app.mount("/exports", StaticFiles(directory=export_dir), name="exports")
    LOG.info(f"Mounted static files from {export_dir} at /exports")
else:
    LOG.warning(f"Export directory {export_dir} not found - static files not mounted")


def get_export_path(filename: str) -> Path:
    """Get the full path to an export file."""
    export_dir = os.getenv("EXPORT_DIR", "exports")
    return Path(export_dir) / filename


def load_json_file(filepath: Path) -> dict[str, Any]:
    """Load and parse a JSON file, returning empty dict on error."""
    try:
        if not filepath.exists():
            LOG.warning(f"Export file not found: {filepath}")
            return {}

        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        LOG.error(f"Error loading {filepath}: {e}")
        return {}


@app.get("/", response_model=APIInfo)
async def root() -> APIInfo:
    """Root endpoint with API information."""
    return APIInfo(
        name="Gemantria Analytics API",
        version="1.0.0",
        description="REST API for gematria correlation and pattern analytics",
        endpoints={
            "stats": "/api/v1/stats",
            "correlations": "/api/v1/correlations",
            "patterns": "/api/v1/patterns",
            "network": "/api/v1/network/{concept_id}",
            "health": "/health",
        },
    )


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    export_dir = Path(os.getenv("EXPORT_DIR", "exports"))

    # Check if export directory exists and has files
    files_status = {}
    expected_files = [
        "graph_stats.json",
        "graph_correlations.json",
        "graph_patterns.json",
        "temporal_patterns.json",
        "pattern_forecast.json",
    ]

    for filename in expected_files:
        filepath = export_dir / filename
        files_status[filename] = {
            "exists": filepath.exists(),
            "size": filepath.stat().st_size if filepath.exists() else 0,
            "mtime": filepath.stat().st_mtime if filepath.exists() else None,
        }

    return HealthResponse(
        status="healthy",
        export_directory=str(export_dir),
        files=files_status,
        timestamp=None,  # Could add last modified time
    )


@app.get("/api/v1/stats")
async def get_stats() -> JSONResponse:
    """Get comprehensive graph statistics."""
    filepath = get_export_path("graph_stats.json")
    data = load_json_file(filepath)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Statistics data not available. Run export pipeline first.",
        )

    return JSONResponse(content=data)


@app.get("/api/v1/correlations")
async def get_correlations(
    limit: int | None = Query(100, description="Maximum number of correlations to return"),
    min_strength: float | None = Query(0.0, description="Minimum correlation strength threshold"),
) -> JSONResponse:
    """Get concept correlation data."""
    filepath = get_export_path("graph_correlations.json")
    data = load_json_file(filepath)

    if not data or "correlations" not in data:
        raise HTTPException(
            status_code=404,
            detail="Correlation data not available. Run export pipeline first.",
        )

    correlations = data["correlations"]

    # Apply filters
    if min_strength > 0.0:
        correlations = [c for c in correlations if abs(c.get("correlation", 0)) >= min_strength]

    if limit and limit > 0:
        correlations = correlations[:limit]

    # Return filtered data with metadata
    return JSONResponse(
        content={
            "correlations": correlations,
            "metadata": {
                **data.get("metadata", {}),
                "filtered_count": len(correlations),
                "applied_filters": {"limit": limit, "min_strength": min_strength},
            },
        }
    )


@app.get("/api/v1/patterns")
async def get_patterns(
    limit: int | None = Query(50, description="Maximum number of patterns to return"),
    min_strength: float | None = Query(0.0, description="Minimum pattern strength threshold"),
    metric: str | None = Query(None, description="Filter by pattern metric"),
) -> JSONResponse:
    """Get cross-text pattern analysis data."""
    filepath = get_export_path("graph_patterns.json")
    data = load_json_file(filepath)

    if not data or "patterns" not in data:
        raise HTTPException(
            status_code=404,
            detail="Pattern data not available. Run export pipeline first.",
        )

    patterns = data["patterns"]

    # Apply filters
    if min_strength > 0.0:
        patterns = [p for p in patterns if p.get("pattern_strength", 0) >= min_strength]

    if metric:
        patterns = [p for p in patterns if p.get("metric", "") == metric]

    # Sort by strength (descending)
    patterns = sorted(patterns, key=lambda x: x.get("pattern_strength", 0), reverse=True)

    if limit and limit > 0:
        patterns = patterns[:limit]

    # Return filtered data with metadata
    return JSONResponse(
        content={
            "patterns": patterns,
            "metadata": {
                **data.get("metadata", {}),
                "filtered_count": len(patterns),
                "applied_filters": {
                    "limit": limit,
                    "min_strength": min_strength,
                    "metric": metric,
                },
            },
        }
    )


@app.get("/api/v1/network/{concept_id}")
async def get_concept_network(
    concept_id: str,
    depth: int | None = Query(1, description="Network depth to traverse"),
    max_connections: int | None = Query(20, description="Maximum connections to return"),
) -> JSONResponse:
    """Get network subgraph for a specific concept."""
    # Load correlation data to build network
    filepath = get_export_path("graph_correlations.json")
    correlation_data = load_json_file(filepath)

    if not correlation_data or "correlations" not in correlation_data:
        raise HTTPException(
            status_code=404,
            detail="Correlation data not available for network analysis.",
        )

    correlations = correlation_data["correlations"]

    # Find all connections for this concept
    connections = []
    seen_concepts = {concept_id}

    # Direct connections (depth 1)
    for corr in correlations:
        if corr.get("source") == concept_id:
            target = corr.get("target")
            if target not in seen_concepts:
                connections.append({"concept_id": target, "correlation": corr, "depth": 1})
                seen_concepts.add(target)
        elif corr.get("target") == concept_id:
            source = corr.get("source")
            if source not in seen_concepts:
                connections.append({"concept_id": source, "correlation": corr, "depth": 1})
                seen_concepts.add(source)

    # For depth > 1, we could implement BFS, but keeping it simple for now
    # In a full implementation, this would traverse the graph

    # Limit connections if specified
    if max_connections and len(connections) > max_connections:
        # Sort by correlation strength and take top N
        connections = sorted(
            connections,
            key=lambda x: abs(x["correlation"].get("correlation", 0)),
            reverse=True,
        )[:max_connections]

    return JSONResponse(
        content={
            "center_concept": concept_id,
            "connections": connections,
            "network_stats": {
                "total_connections": len(connections),
                "depth": depth,
                "max_connections_requested": max_connections,
            },
            "metadata": correlation_data.get("metadata", {}),
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for consistent error responses."""
    LOG.error(f"API Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url),
        },
    )


@app.get("/api/v1/temporal")
async def get_temporal_patterns(
    series_id: str = Query(None, description="Specific series ID to filter by"),
    unit: str = Query("chapter", description="Time unit: 'verse' or 'chapter'"),
    window: int = Query(5, min=1, description="Rolling window size"),
) -> JSONResponse:
    """
    Get temporal pattern data with optional filtering.

    - **series_id**: Filter to specific concept/cluster series
    - **unit**: Time unit for analysis (verse/chapter)
    - **window**: Rolling window size for pattern computation
    """
    try:
        temporal_file = get_export_path("temporal_patterns.json")
        if not temporal_file.exists():
            raise HTTPException(status_code=404, detail="Temporal patterns data not available")

        with open(temporal_file, encoding="utf-8") as f:
            data = json.load(f)

        patterns = data.get("temporal_patterns", [])

        # Apply filters
        if series_id:
            patterns = [p for p in patterns if p.get("series_id") == series_id]

        # Filter by unit if specified
        if unit:
            patterns = [p for p in patterns if p.get("unit") == unit]

        # Filter by window if specified
        if window:
            patterns = [p for p in patterns if p.get("window") == window]

        # Limit results for API performance
        max_results = 50
        if len(patterns) > max_results:
            patterns = patterns[:max_results]

        return JSONResponse(
            content={
                "temporal_patterns": patterns,
                "metadata": data.get("metadata", {}),
                "filters_applied": {
                    "series_id": series_id,
                    "unit": unit,
                    "window": window,
                },
                "result_count": len(patterns),
                "max_results": max_results,
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Temporal patterns data not found") from e
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="Invalid temporal patterns data") from e
    except Exception as e:
        LOG.error(f"Error in temporal patterns endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e!s}") from e


@app.get("/api/v1/forecast")
async def get_forecasts(
    series_id: str = Query(None, description="Specific series ID to filter by"),
    horizon: int = Query(10, min=1, description="Forecast horizon"),
) -> JSONResponse:
    """
    Get forecast data with optional filtering.

    - **series_id**: Filter to specific concept/cluster forecasts
    - **horizon**: Forecast horizon (steps ahead)
    """
    try:
        forecast_file = get_export_path("pattern_forecast.json")
        if not forecast_file.exists():
            raise HTTPException(status_code=404, detail="Forecast data not available")

        with open(forecast_file, encoding="utf-8") as f:
            data = json.load(f)

        forecasts = data.get("forecasts", [])

        # Apply filters
        if series_id:
            forecasts = [f for f in forecasts if f.get("series_id") == series_id]

        # Filter by horizon if specified
        if horizon:
            forecasts = [f for f in forecasts if f.get("horizon") == horizon]

        # Limit results for API performance
        max_results = 20
        if len(forecasts) > max_results:
            forecasts = forecasts[:max_results]

        return JSONResponse(
            content={
                "forecasts": forecasts,
                "metadata": data.get("metadata", {}),
                "filters_applied": {"series_id": series_id, "horizon": horizon},
                "result_count": len(forecasts),
                "max_results": max_results,
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Forecast data not found") from e
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="Invalid forecast data") from e
    except Exception as e:
        LOG.error(f"Error in forecast endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e!s}") from e


@app.get("/temporal/patterns")
async def get_temporal_patterns_filtered(
    book: str = Query("Genesis", description="Biblical book name"),
    metric: str = Query(None, description="Filter by metric type (frequency, strength, cooccurrence)"),
) -> JSONResponse:
    """
    Retrieve filtered temporal patterns from share/temporal_patterns_latest.json.

    - **book**: Filter by biblical book name
    - **metric**: Filter by metric type (optional)
    """
    try:
        share_dir = Path("share")
        temporal_file = share_dir / "temporal_patterns_latest.json"

        if not temporal_file.exists():
            raise HTTPException(status_code=404, detail="Temporal patterns data not available")

        with open(temporal_file, encoding="utf-8") as f:
            data = json.load(f)

        patterns = data.get("temporal_patterns", [])

        # Apply filters
        if book:
            patterns = [p for p in patterns if p.get("book") == book]

        if metric:
            patterns = [p for p in patterns if p.get("metric") == metric]

        # Filter rolling windows if metric specified
        if metric and patterns:
            # Extract only the specified metric from rolling windows
            filtered_patterns = []
            for pattern in patterns:
                values = pattern.get("values", [])
                if metric == "mean" and values:
                    # For mean, we can compute if needed or use existing values
                    filtered_patterns.append(pattern)
                else:
                    filtered_patterns.append(pattern)
            patterns = filtered_patterns

        return JSONResponse(
            content={
                "temporal_patterns": patterns,
                "metadata": data.get("metadata", {}),
                "filters_applied": {"book": book, "metric": metric},
                "result_count": len(patterns),
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Temporal patterns data not found") from e
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="Invalid temporal patterns data") from e
    except Exception as e:
        LOG.error(f"Error in temporal patterns endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e!s}") from e


@app.get("/temporal/forecast")
async def get_temporal_forecast_filtered(
    model: str = Query("naive", description="Forecast model (naive, sma, arima)"),
    horizon: int = Query(10, min=1, max=100, description="Forecast horizon (steps ahead)"),
) -> JSONResponse:
    """
    Retrieve filtered forecasts from share/pattern_forecast_latest.json.

    - **model**: Forecast model name (naive, sma, arima)
    - **horizon**: Number of forecast steps to return
    """
    try:
        share_dir = Path("share")
        forecast_file = share_dir / "pattern_forecast_latest.json"

        if not forecast_file.exists():
            raise HTTPException(status_code=404, detail="Forecast data not available")

        with open(forecast_file, encoding="utf-8") as f:
            data = json.load(f)

        forecasts = data.get("forecasts", [])

        # Filter by model
        if model:
            forecasts = [f for f in forecasts if f.get("model") == model]

        # Limit horizon for each forecast
        if horizon:
            for forecast in forecasts:
                predictions = forecast.get("predictions", [])
                if len(predictions) > horizon:
                    forecast["predictions"] = predictions[:horizon]

                # Also limit intervals
                intervals = forecast.get("prediction_intervals", {})
                if intervals:
                    lower = intervals.get("lower", [])
                    upper = intervals.get("upper", [])
                    if len(lower) > horizon:
                        intervals["lower"] = lower[:horizon]
                        intervals["upper"] = upper[:horizon]

        # If no forecasts match, return error
        if not forecasts:
            return JSONResponse(
                content={
                    "error": f"Model '{model}' not found",
                    "available_models": list(set(f.get("model") for f in data.get("forecasts", []))),
                },
                status_code=404,
            )

        return JSONResponse(
            content={
                "forecasts": forecasts,
                "metadata": data.get("metadata", {}),
                "filters_applied": {"model": model, "horizon": horizon},
                "result_count": len(forecasts),
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Forecast data not found") from e
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="Invalid forecast data") from e
    except Exception as e:
        LOG.error(f"Error in forecast endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e!s}") from e


if __name__ == "__main__":
    import uvicorn  # noqa: E402

    # Default to port 8000, but allow override
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "127.0.0.1")

    LOG.info(f"Starting Gemantria Analytics API on {host}:{port}")
    uvicorn.run(
        "src.services.api_server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )
