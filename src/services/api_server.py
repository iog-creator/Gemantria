# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

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
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.infra.env_loader import ensure_env_loaded
from src.infra.structured_logger import get_logger

# Import system status helpers
from agentpm.status.eval_exports import (
    load_db_health_snapshot,
    load_edge_class_counts,
    load_lm_indicator,
)
from agentpm.status.explain import explain_system_status
from agentpm.status.system import get_system_status
from datetime import UTC

# Router imports
from src.services.routers.biblescholar import router as bible_router, biblescholar_router
from src.services.routers.ollama_proxy import router as ollama_router
from src.services.routers.dashboard import router as dashboard_router
from src.services.routers.vision import router as vision_router
from agentpm.server.autopilot_api import router as autopilot_router

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

# Include BibleScholar routers
app.include_router(bible_router)  # /api/bible routes
app.include_router(biblescholar_router)  # /api/biblescholar routes

# Include Ollama proxy router
app.include_router(ollama_router)

# Include Dashboard router
app.include_router(dashboard_router)

# Include Vision router
app.include_router(vision_router)

# Include Autopilot router
app.include_router(autopilot_router)

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

# Mount static files from share directory
share_dir = Path("share")
if share_dir.exists():
    app.mount("/share", StaticFiles(directory=str(share_dir)), name="share")
    LOG.info(f"Mounted static files from {share_dir} at /share")
else:
    LOG.warning(f"Share directory {share_dir} not found - static files not mounted")


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
            "docs_search": "/api/docs/search",
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


@app.get("/api/status/system")
async def get_system_status_endpoint() -> JSONResponse:
    """Get system status (DB + LM health snapshot).

    Returns:
        JSON with db and lm health status, plus optional AI tracking and share manifest:
        {
            "db": {
                "reachable": bool,
                "mode": "ready" | "db_off" | "partial",
                "notes": str
            },
            "lm": {
                "slots": [
                    {
                        "name": str,
                        "provider": str,
                        "model": str,
                        "service": "OK" | "DOWN" | "UNKNOWN" | "DISABLED" | "SKIPPED"
                    },
                    ...
                ],
                "notes": str
            },
            "ai_tracking": {
                "ok": bool,
                "mode": "db_on" | "db_off",
                "summary": {...}
            } (optional),
            "share_manifest": {
                "ok": bool,
                "count": int,
                "items": [...]
            } (optional)
        }
    """
    try:
        # Use unified snapshot helper for consistency with pm.snapshot
        from agentpm.status.snapshot import get_system_snapshot

        snapshot = get_system_snapshot(
            include_reality_check=False,  # Skip for /api/status/system (use /api/status/explain for that)
            include_ai_tracking=True,
            include_share_manifest=True,
            include_eval_insights=True,  # Include eval exports summary
            use_lm_for_explain=False,  # Fast path for API
        )

        # Extract and format response (backward compatible with existing frontend)
        system_status = get_system_status()  # Keep existing format for db/lm
        response = {
            "db": system_status.get("db", {}),
            "lm": system_status.get("lm", {}),
        }

        # Add optional AI tracking, share manifest, eval insights, and KB doc health if available
        if "ai_tracking" in snapshot:
            response["ai_tracking"] = snapshot["ai_tracking"]
        if "share_manifest" in snapshot:
            response["share_manifest"] = snapshot["share_manifest"]
        if "eval_insights" in snapshot:
            response["eval_insights"] = snapshot["eval_insights"]
        if "kb_doc_health" in snapshot:
            response["kb_doc_health"] = snapshot["kb_doc_health"]

        return JSONResponse(content=response)
    except Exception as e:
        LOG.error(f"Error getting system status: {e}")
        # Fallback to original implementation if snapshot helper fails
        try:
            status = get_system_status()
            return JSONResponse(content=status)
        except Exception as fallback_error:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error while fetching system status: {e!s}",
            ) from fallback_error


@app.get("/api/status/explain")
async def get_status_explanation_endpoint() -> JSONResponse:
    """Get human-readable explanation of system status.

    Returns:
        JSON with explanation:
        {
            "level": "OK" | "WARN" | "ERROR",
            "headline": str,
            "details": str
        }
    """
    try:
        explanation = explain_system_status(use_lm=False)  # Disabled to avoid triggering model loads
        return JSONResponse(content=explanation)
    except Exception as e:
        LOG.error(f"Error getting status explanation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to compute status explanation",
        ) from e


@app.get("/api/lm/insights")
async def get_lm_insights_endpoint() -> JSONResponse:
    """Get detailed LM insights from Phase 4 exports (7-day window).

    Returns aggregated metrics from lm_usage_7d.json, lm_health_7d.json, and lm_insights_7d.json:
    {
        "usage": {
            "total_calls": int,
            "successful_calls": int,
            "failed_calls": int,
            "total_tokens_prompt": int,
            "total_tokens_completion": int,
            "avg_latency_ms": float,
            "calls_by_day": [...]
        },
        "health": {
            "success_rate": float,
            "error_rate": float,
            "error_types": {...},
            "recent_errors": [...]
        },
        "insights": {
            "ok": bool,
            "total_calls": int,
            "success_rate": float,
            "error_rate": float,
            "top_error_reason": str | null,
            "lm_studio_usage_ratio": float | null
        },
        "generated_at": str,
        "window_days": int
    }
    """
    try:
        from pathlib import Path
        import json

        REPO_ROOT = Path(__file__).resolve().parents[2]
        OUT_DIR = REPO_ROOT / "share" / "atlas" / "control_plane"

        # Load export files
        usage_path = OUT_DIR / "lm_usage_7d.json"
        health_path = OUT_DIR / "lm_health_7d.json"
        insights_path = OUT_DIR / "lm_insights_7d.json"

        usage_data = None
        health_data = None
        insights_data = None

        # Load usage data
        if usage_path.exists():
            try:
                usage_data = json.loads(usage_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                LOG.warning(f"Failed to load lm_usage_7d.json: {e}")

        # Load health data
        if health_path.exists():
            try:
                health_data = json.loads(health_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                LOG.warning(f"Failed to load lm_health_7d.json: {e}")

        # Load insights data
        if insights_path.exists():
            try:
                insights_data = json.loads(insights_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                LOG.warning(f"Failed to load lm_insights_7d.json: {e}")

        # If no data available, return empty structure
        if not usage_data and not health_data and not insights_data:
            return JSONResponse(
                content={
                    "usage": None,
                    "health": None,
                    "insights": None,
                    "generated_at": None,
                    "window_days": 7,
                    "error": "No LM metrics data available (exports may not have been generated)",
                }
            )

        # Extract relevant fields
        response = {
            "usage": usage_data if usage_data else None,
            "health": health_data if health_data else None,
            "insights": insights_data if insights_data else None,
            "generated_at": insights_data.get("generated_at")
            if insights_data
            else usage_data.get("generated_at")
            if usage_data
            else None,
            "window_days": insights_data.get("window_days", 7)
            if insights_data
            else usage_data.get("window_days", 7)
            if usage_data
            else 7,
        }

        return JSONResponse(content=response)
    except Exception as e:
        LOG.error(f"Error getting LM insights: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load LM insights: {e!s}",
        ) from e


@app.get("/api/lm/indicator")
async def get_lm_indicator_endpoint() -> JSONResponse:
    """Get LM indicator snapshot for visualization.

    Returns:
        JSON with LM indicator data:
        {
            "snapshot": {
                "status": "offline" | "healthy" | "degraded",
                "reason": str,
                "success_rate": float,
                "error_rate": float,
                "total_calls": int,
                "db_off": bool,
                "top_error_reason": str | None,
                "window_days": int,
                "generated_at": str
            } | null,
            "note": str (if snapshot is null)
        }
        Uses shared eval exports helper (hermetic, tolerant of missing files).
    """
    try:
        indicator_data = load_lm_indicator()

        # Check if data is available
        if not indicator_data.get("available", False):
            return JSONResponse(
                content={
                    "snapshot": None,
                    "note": indicator_data.get(
                        "note",
                        "LM indicator data not available; run the LM indicator export pipeline to populate this chart.",
                    ),
                }
            )

        # Remove internal fields before returning
        snapshot = {k: v for k, v in indicator_data.items() if k not in ("available", "note")}

        return JSONResponse(
            content={
                "snapshot": snapshot,
            }
        )

    except Exception as e:
        LOG.error(f"Error getting LM indicator: {e}")
        return JSONResponse(
            content={
                "snapshot": None,
                "note": f"Failed to load LM indicator data: {e}",
            }
        )


@app.get("/api/inference/models")
async def get_inference_models_endpoint() -> JSONResponse:
    """Get unified inference model activity from Ollama and LM Studio.

    Returns:
        JSON with inference model data:
        {
            "ollama": {
                "available": bool,
                "base_url": str,
                "available_models": [{"id": str, "name": str}],
                "active_requests": [...],
                "recent_requests": [...]
            },
            "lmstudio": {
                "available": bool,
                "base_urls": [str],
                "available_models": [{"id": str, "base_url": str}],
                "recent_activity": [...]
            },
            "last_updated": str
        }
    """
    from datetime import UTC, datetime
    from src.services.inference_monitor import (
        get_lmstudio_loaded_models,
        get_lmstudio_recent_activity,
        get_ollama_loaded_models,
    )
    from src.services.ollama_monitor.store import get_monitor_snapshot
    from scripts.config.env import get_lm_model_config

    try:
        cfg = get_lm_model_config()
        ollama_base_url = cfg.get("ollama_base_url", "http://127.0.0.1:11434")
        ollama_enabled = cfg.get("ollama_enabled", True)

        # Get Ollama data
        ollama_data = {
            "available": False,
            "base_url": ollama_base_url,
            "available_models": [],
            "active_requests": [],
            "recent_requests": [],
        }

        if ollama_enabled:
            try:
                # Get monitor snapshot
                monitor_snapshot = get_monitor_snapshot()
                ollama_data["active_requests"] = monitor_snapshot.get("activeRequests", [])

                # Filter recent requests to last 2 days
                from datetime import UTC, datetime, timedelta

                two_days_ago = datetime.now(UTC) - timedelta(days=2)
                all_recent = monitor_snapshot.get("recentRequests", [])
                recent_filtered = []
                for req in all_recent:
                    try:
                        req_time = datetime.fromisoformat(req.get("timestamp", "").replace("Z", "+00:00"))
                        if req_time >= two_days_ago:
                            # Add simplified inference summary
                            from src.services.inference_monitor import simplify_inference_output

                            req["inference_summary"] = simplify_inference_output(
                                req.get("promptPreview", ""), req.get("endpoint")
                            )
                            recent_filtered.append(req)
                    except (ValueError, TypeError):
                        # If timestamp parsing fails, include it anyway (recent by default)
                        from src.services.inference_monitor import simplify_inference_output

                        req["inference_summary"] = simplify_inference_output(
                            req.get("promptPreview", ""), req.get("endpoint")
                        )
                        recent_filtered.append(req)

                ollama_data["recent_requests"] = recent_filtered

                # Get available models (list from /api/tags)
                available_models = get_ollama_loaded_models(ollama_base_url)

                # Extract recently used models from recent requests
                recently_used_models = set()
                for req in recent_filtered:
                    if req.get("model"):
                        recently_used_models.add(req["model"])

                # Filter available models to only show recently used ones
                if recently_used_models:
                    ollama_data["recently_used_models"] = [
                        m
                        for m in available_models
                        if m.get("name") in recently_used_models or m.get("id") in recently_used_models
                    ]
                else:
                    ollama_data["recently_used_models"] = []

                ollama_data["available_models"] = available_models
                ollama_data["available"] = True
            except Exception as e:
                LOG.debug(f"Ollama monitor unavailable: {e}")

        # Get LM Studio data
        lmstudio_data = {
            "available": False,
            "base_urls": [],
            "available_models": [],
            "recent_activity": [],
        }

        lm_studio_enabled = cfg.get("lm_studio_enabled", False)
        if lm_studio_enabled:
            # Collect all LM Studio base URLs
            base_urls = []
            default_base_url = cfg.get("base_url", "http://127.0.0.1:9994/v1")
            if default_base_url:
                # Remove /v1 suffix for consistency
                clean_url = default_base_url.rstrip("/")
                if clean_url.endswith("/v1"):
                    clean_url = clean_url[:-3]
                base_urls.append(clean_url)

            theology_base_url = cfg.get("theology_lmstudio_base_url")
            if theology_base_url:
                clean_url = theology_base_url.rstrip("/")
                if clean_url.endswith("/v1"):
                    clean_url = clean_url[:-3]
                if clean_url not in base_urls:
                    base_urls.append(clean_url)

            lmstudio_data["base_urls"] = base_urls

            # Get available models (list from /v1/models)
            if base_urls:
                available_models = get_lmstudio_loaded_models(base_urls)
                lmstudio_data["available_models"] = available_models
                if available_models:
                    lmstudio_data["available"] = True

            # Get recent activity from DB (last 2 days)
            recent_activity = get_lmstudio_recent_activity(days=2, limit=1000)
            lmstudio_data["recent_activity"] = recent_activity

            # Extract recently used models (models that appear in recent activity)
            recently_used_models = set()
            for act in recent_activity:
                if act.get("model") and act["model"] != "unknown":
                    recently_used_models.add(act["model"])

            # Filter available models to only show recently used ones
            if recently_used_models:
                lmstudio_data["recently_used_models"] = [
                    m for m in available_models if m.get("id") in recently_used_models
                ]
            else:
                lmstudio_data["recently_used_models"] = []

        return JSONResponse(
            content={
                "ollama": ollama_data,
                "lmstudio": lmstudio_data,
                "last_updated": datetime.now(UTC).isoformat(),
            }
        )

    except Exception as e:
        LOG.error(f"Error getting inference models: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to get inference models data",
                "details": str(e),
            },
        )


@app.get("/status", response_class=HTMLResponse)
async def status_page() -> HTMLResponse:
    """HTML status page showing DB + LM health."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Status - Gemantria</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-ok { background-color: #10b981; }
        .status-down { background-color: #ef4444; }
        .status-unknown { background-color: #6b7280; }
        .status-disabled { background-color: #9ca3af; }
    </style>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">System Status</h1>
        
        <div id="loading" class="text-gray-600">Loading status...</div>
        
        <div id="status-content" class="hidden">
            <!-- Explanation Section -->
            <div class="bg-blue-50 border border-blue-200 rounded-lg shadow p-6 mb-6">
                <h2 class="text-xl font-semibold mb-3">Explanation</h2>
                <div id="explanation-content">
                    <h3 id="explanation-headline" class="text-lg font-medium mb-2 text-gray-800"></h3>
                    <p id="explanation-details" class="text-sm text-gray-700"></p>
                </div>
                <div id="explanation-error" class="hidden text-sm text-gray-500 italic">
                    Explanation unavailable; raw status is still shown below.
                </div>
            </div>
            
            <!-- DB Status Section -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h2 class="text-xl font-semibold mb-4">DB Status</h2>
                <div id="db-status" class="text-lg">
                    <span id="db-indicator"></span>
                    <span id="db-text"></span>
                </div>
                <p id="db-notes" class="text-sm text-gray-600 mt-2"></p>
            </div>
            
            <!-- LM Status Section -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h2 class="text-xl font-semibold mb-4">LM Slots</h2>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Slot</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Model</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Service</th>
                            </tr>
                        </thead>
                        <tbody id="lm-slots" class="bg-white divide-y divide-gray-200">
                        </tbody>
                    </table>
                </div>
                <p id="lm-notes" class="text-sm text-gray-600 mt-4"></p>
            </div>
            
            <!-- Documentation Health Section (KB-Reg:M5) -->
            <div id="doc-health-card" class="bg-white rounded-lg shadow p-6 mb-6 hidden">
                <h2 class="text-xl font-semibold mb-4">Documentation Health</h2>
                <div id="doc-health-content">
                    <div class="mb-4">
                        <div class="text-sm text-gray-600 mb-2">
                            <span id="doc-total"></span>
                            <span id="doc-subsystem-breakdown" class="ml-2"></span>
                        </div>
                        <div id="doc-hints-badge" class="hidden inline-block px-2 py-1 rounded-full text-xs font-semibold mb-2"></div>
                    </div>
                    
                    <!-- Metrics Section (AgentPM-Next:M4) -->
                    <div id="doc-metrics-container" class="hidden mb-4 grid grid-cols-3 gap-4 text-center border-t border-b border-gray-100 py-4 bg-gray-50 rounded-md">
                        <div>
                            <div id="doc-freshness-val" class="text-lg font-bold text-gray-800">--%</div>
                            <div class="text-xs text-gray-500">Freshness</div>
                        </div>
                        <div>
                            <div id="doc-fixes-val" class="text-lg font-bold text-gray-800">--</div>
                            <div class="text-xs text-gray-500">Fixes (7d)</div>
                        </div>
                        <div>
                            <div id="doc-missing-val" class="text-lg font-bold text-gray-800">--</div>
                            <div class="text-xs text-gray-500">Missing/Stale</div>
                        </div>
                    </div>

                    <div id="doc-key-docs" class="mt-4">
                        <h3 class="text-sm font-medium text-gray-700 mb-2">Key Documents:</h3>
                        <ul id="doc-key-docs-list" class="list-disc list-inside text-sm text-gray-600 space-y-1">
                        </ul>
                    </div>
                </div>
                <div id="doc-health-unavailable" class="hidden text-sm text-gray-500 italic">
                    Documentation registry unavailable
                </div>
            </div>
            
            <p class="text-xs text-gray-500 mt-6">All LM/DB checks are local (127.0.0.1).</p>
        </div>
        
        <div id="error" class="hidden text-red-600 mt-4"></div>
    </div>
    
    <script>
        async function loadExplanation() {
            try {
                const response = await fetch('/api/status/explain');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const explanation = await response.json();
                
                // Show explanation content
                document.getElementById('explanation-content').classList.remove('hidden');
                document.getElementById('explanation-error').classList.add('hidden');
                
                const headline = document.getElementById('explanation-headline');
                const details = document.getElementById('explanation-details');
                
                headline.textContent = explanation.headline || 'Status summary';
                details.textContent = explanation.details || 'No details available';
                
                // Style based on level
                const level = explanation.level || 'OK';
                const explanationCard = document.querySelector('.bg-blue-50');
                if (level === 'ERROR') {
                    explanationCard.className = 'bg-red-50 border border-red-200 rounded-lg shadow p-6 mb-6';
                } else if (level === 'WARN') {
                    explanationCard.className = 'bg-yellow-50 border border-yellow-200 rounded-lg shadow p-6 mb-6';
                } else {
                    explanationCard.className = 'bg-green-50 border border-green-200 rounded-lg shadow p-6 mb-6';
                }
                
                // Load documentation health (KB-Reg:M5)
                loadDocumentationHealth(explanation);
            } catch (error) {
                // Hide explanation content, show error message
                document.getElementById('explanation-content').classList.add('hidden');
                document.getElementById('explanation-error').classList.remove('hidden');
            }
        }
        
        function loadDocumentationHealth(explanation) {
            const docCard = document.getElementById('doc-health-card');
            const docContent = document.getElementById('doc-health-content');
            const docUnavailable = document.getElementById('doc-health-unavailable');
            
            // Note: This loads registry summary from explanation (M5); metrics (M3) loaded via snapshot
            if (!explanation.documentation || !explanation.documentation.available) {
                // Don't hide if we might have snapshot metrics; wait for snapshot to confirm
                // But for now, assume registry availability is master switch
                docCard.classList.remove('hidden');
                docContent.classList.add('hidden');
                docUnavailable.classList.remove('hidden');
                return;
            }
            
            const doc = explanation.documentation;
            docCard.classList.remove('hidden');
            docContent.classList.remove('hidden');
            docUnavailable.classList.add('hidden');
            
            // Update total and subsystem breakdown
            const docTotal = document.getElementById('doc-total');
            docTotal.textContent = `Total: ${doc.total} document(s)`;
            
            const docSubsystem = document.getElementById('doc-subsystem-breakdown');
            const subsystems = Object.entries(doc.by_subsystem || {})
                .map(([sub, count]) => `${sub}: ${count}`)
                .join(', ');
            docSubsystem.textContent = subsystems ? `(${subsystems})` : '';
            
            // Show hints badge if there are WARN hints
            const warnHints = (doc.hints || []).filter(h => h.level === 'WARN');
            const hintsBadge = document.getElementById('doc-hints-badge');
            if (warnHints.length > 0) {
                hintsBadge.classList.remove('hidden');
                hintsBadge.className = 'inline-block px-2 py-1 rounded-full text-xs font-semibold mb-2 bg-yellow-500 text-white';
                hintsBadge.textContent = `⚠️ ${warnHints.length} warning(s)`;
            } else {
                hintsBadge.classList.add('hidden');
            }
            
            // Update key docs list
            const keyDocsList = document.getElementById('doc-key-docs-list');
            keyDocsList.innerHTML = '';
            if (doc.key_docs && doc.key_docs.length > 0) {
                doc.key_docs.forEach(docItem => {
                    const li = document.createElement('li');
                    const link = document.createElement('a');
                    link.href = `/${docItem.path}`;
                    link.className = 'text-blue-600 hover:text-blue-800';
                    link.textContent = docItem.title;
                    li.appendChild(link);
                    keyDocsList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'No key documents found';
                li.className = 'text-gray-400 italic';
                keyDocsList.appendChild(li);
            }
        }
        
        function loadDocMetrics(docHealth) {
            const metricsContainer = document.getElementById('doc-metrics-container');
            
            if (!docHealth || !docHealth.available || !docHealth.metrics) {
                metricsContainer.classList.add('hidden');
                return;
            }
            
            metricsContainer.classList.remove('hidden');
            const m = docHealth.metrics;
            
            // Freshness
            const freshRatio = m.kb_fresh_ratio?.overall ?? 0;
            const freshPct = Math.round(freshRatio * 100);
            const freshEl = document.getElementById('doc-freshness-val');
            freshEl.textContent = `${freshPct}%`;
            // Color code freshness
            if (freshPct >= 90) freshEl.className = "text-lg font-bold text-green-600";
            else if (freshPct >= 70) freshEl.className = "text-lg font-bold text-yellow-600";
            else freshEl.className = "text-lg font-bold text-red-600";
            
            // Fixes
            document.getElementById('doc-fixes-val').textContent = m.kb_fixes_applied_last_7d ?? 0;
            
            // Missing/Stale
            const missing = m.kb_missing_count ?? 0;
            // Estimate stale from breakdown if available, or just use missing for now
            // Actually docHealth usually has detailed counts
            let stale = 0;
            if (m.kb_stale_count_by_subsystem) {
                stale = Object.values(m.kb_stale_count_by_subsystem).reduce((a, b) => a + b, 0);
            }
            
            const missingStaleEl = document.getElementById('doc-missing-val');
            missingStaleEl.textContent = `${missing} / ${stale}`;
            if (missing + stale > 0) missingStaleEl.className = "text-lg font-bold text-yellow-600";
            else missingStaleEl.className = "text-lg font-bold text-gray-800";
        }

        async function loadStatus() {
            try {
                const response = await fetch('/api/status/system');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                
                // Hide loading, show content
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('status-content').classList.remove('hidden');
                
                // Update DB status
                const db = data.db;
                const dbIndicator = document.getElementById('db-indicator');
                const dbText = document.getElementById('db-text');
                const dbNotes = document.getElementById('db-notes');
                
                let dbStatusText = '';
                let dbStatusClass = '';
                if (db.mode === 'ready' && db.reachable) {
                    dbStatusText = 'Reachable ✅';
                    dbStatusClass = 'status-ok';
                } else if (db.mode === 'partial') {
                    dbStatusText = 'Partial ⚠️';
                    dbStatusClass = 'status-unknown';
                } else {
                    dbStatusText = 'Down ❌';
                    dbStatusClass = 'status-down';
                }
                
                dbIndicator.innerHTML = `<span class="status-dot ${dbStatusClass}"></span>`;
                dbText.textContent = `DB Status: ${dbStatusText}`;
                dbNotes.textContent = db.notes;
                
                // Update LM slots
                const lm = data.lm;
                const lmSlots = document.getElementById('lm-slots');
                const lmNotes = document.getElementById('lm-notes');
                
                lmSlots.innerHTML = '';
                lm.slots.forEach(slot => {
                    const row = document.createElement('tr');
                    let serviceClass = 'status-unknown';
                    if (slot.service === 'OK') {
                        serviceClass = 'status-ok';
                    } else if (slot.service === 'DOWN') {
                        serviceClass = 'status-down';
                    } else if (slot.service === 'DISABLED') {
                        serviceClass = 'status-disabled';
                    }
                    
                    row.innerHTML = `
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${slot.name}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${slot.provider}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${slot.model}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <span class="status-dot ${serviceClass}"></span>${slot.service}
                        </td>
                    `;
                    lmSlots.appendChild(row);
                });
                
                lmNotes.textContent = lm.notes;
                
                // Load KB Doc Metrics if available (AgentPM-Next:M4)
                if (data.kb_doc_health) {
                    loadDocMetrics(data.kb_doc_health);
                }
                
            } catch (error) {
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('error').classList.remove('hidden');
                document.getElementById('error').textContent = `Error loading status: ${error.message}`;
            }
        }
        
        // Load status and explanation on page load
        loadStatus();
        loadExplanation();
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            loadStatus();
            loadExplanation();
        }, 30000);
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/lm-insights", response_class=HTMLResponse)
async def lm_insights_page() -> HTMLResponse:
    """HTML page showing Inference Models Insight with real-time activity from Ollama and LM Studio.

    Features:
    - Summary cards showing key metrics at a glance
    - Inference section with simplified summaries for orchestrator readability
    - Only shows recently used models (last 2 days)
    - Better visual hierarchy for understanding at a glance
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inference Models Insight - Gemantria</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: rgb(17, 24, 39); }
    </style>
</head>
<body class="bg-gray-900 p-8 text-white">
    <div class="max-w-7xl mx-auto">
        <h1 class="text-3xl font-bold mb-2 text-white">Inference Models Insight</h1>
        <p class="text-gray-400 mb-6 text-sm">Real-time monitoring of Ollama and LM Studio inference models (last 2 days). Understanding at a glance.</p>
        
        <div id="loading" class="text-gray-300">Loading inference models data...</div>
        
        <div id="error" class="hidden text-red-400 mt-4"></div>
        
        <div id="content" class="hidden">
            <!-- Summary Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div class="bg-gray-800 rounded-lg shadow p-4 border border-gray-700">
                    <div class="text-sm text-gray-400 mb-1">Total Requests</div>
                    <div id="summary-total" class="text-2xl font-bold text-white">—</div>
                </div>
                <div class="bg-gray-800 rounded-lg shadow p-4 border border-gray-700">
                    <div class="text-sm text-gray-400 mb-1">Errors</div>
                    <div id="summary-errors" class="text-2xl font-bold text-red-400">—</div>
                </div>
                <div class="bg-gray-800 rounded-lg shadow p-4 border border-gray-700">
                    <div class="text-sm text-gray-400 mb-1">Avg Duration</div>
                    <div id="summary-avg-duration" class="text-2xl font-bold text-white">—</div>
                </div>
                <div class="bg-gray-800 rounded-lg shadow p-4 border border-gray-700">
                    <div class="text-sm text-gray-400 mb-1">Active Now</div>
                    <div id="summary-active" class="text-2xl font-bold text-blue-400">—</div>
                </div>
            </div>
            
            <!-- Provider Tabs -->
            <div class="mb-6 border-b border-gray-700">
                <nav class="flex space-x-8">
                    <button id="tab-ollama" class="tab-button py-4 px-1 border-b-2 font-medium text-sm text-blue-400 border-blue-400" onclick="switchTab('ollama')">
                        Ollama
                    </button>
                    <button id="tab-lmstudio" class="tab-button py-4 px-1 border-b-2 font-medium text-sm text-gray-400 border-transparent hover:text-gray-300 hover:border-gray-600" onclick="switchTab('lmstudio')">
                        LM Studio
                    </button>
                </nav>
            </div>
            
            <!-- Ollama Tab Content -->
            <div id="tab-content-ollama" class="tab-content">
                <!-- Status and Recently Used Models -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div class="bg-gray-800 rounded-lg shadow p-6 border border-gray-700">
                        <h2 class="text-lg font-semibold mb-3 text-white">Status</h2>
                        <div id="ollama-status" class="text-sm text-gray-300"></div>
                    </div>
                    <div class="bg-gray-800 rounded-lg shadow p-6 border border-gray-700">
                        <h2 class="text-lg font-semibold mb-3 text-white">Recently Used Models</h2>
                        <div id="ollama-models" class="text-sm text-gray-300">No models used in last 2 days</div>
                    </div>
                </div>
                
                <!-- Inference Section -->
                <div class="mb-6 bg-gray-800 rounded-lg shadow p-6 border border-gray-700">
                    <h2 class="text-lg font-semibold mb-4 text-white">Inference</h2>
                    <p class="text-xs text-gray-400 mb-4">Simplified summaries for orchestrator readability</p>
                    <div id="ollama-inference" class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-700">
                            <thead class="bg-gray-700">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Model</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Summary</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Time</th>
                                </tr>
                            </thead>
                            <tbody id="ollama-inference-body" class="bg-gray-800 divide-y divide-gray-700">
                            </tbody>
                        </table>
                        <div id="ollama-inference-empty" class="text-sm text-gray-400 py-4 text-center">No inference activity</div>
                    </div>
                </div>
                
                <div class="mb-6 bg-gray-800 rounded-lg shadow p-6 border border-gray-700">
                    <h2 class="text-xl font-semibold mb-4 text-white">Active Requests</h2>
                    <div id="ollama-active" class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-700">
                            <thead class="bg-gray-700">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Model</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Endpoint</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Start Time</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Prompt Preview</th>
                                </tr>
                            </thead>
                            <tbody id="ollama-active-body" class="bg-gray-800 divide-y divide-gray-700">
                            </tbody>
                        </table>
                        <div id="ollama-active-empty" class="text-sm text-gray-400 py-4 text-center">No active requests</div>
                    </div>
                </div>
                
                <!-- Recent Activity (Detailed) -->
                <div class="bg-gray-800 rounded-lg shadow p-6 border border-gray-700">
                    <h2 class="text-lg font-semibold mb-4 text-white">Recent Activity (Last 2 Days)</h2>
                    <div id="ollama-recent" class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-700">
                            <thead class="bg-gray-700">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Model</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Endpoint</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Duration</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Tokens</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Time</th>
                                </tr>
                            </thead>
                            <tbody id="ollama-recent-body" class="bg-gray-800 divide-y divide-gray-700">
                            </tbody>
                        </table>
                        <div id="ollama-recent-empty" class="text-sm text-gray-400 py-4 text-center">No recent requests</div>
                    </div>
                </div>
            </div>
            
            <!-- LM Studio Tab Content -->
            <div id="tab-content-lmstudio" class="tab-content hidden">
                <!-- Status and Recently Used Models -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div class="bg-gray-800 rounded-lg shadow p-6 border border-gray-700">
                        <h2 class="text-lg font-semibold mb-3 text-white">Status</h2>
                        <div id="lmstudio-status" class="text-sm text-gray-300"></div>
                    </div>
                    <div class="bg-gray-800 rounded-lg shadow p-6 border border-gray-700">
                        <h2 class="text-lg font-semibold mb-3 text-white">Recently Used Models</h2>
                        <div id="lmstudio-models" class="text-sm text-gray-300">No models used in last 2 days</div>
                    </div>
                </div>
                
                <!-- Inference Section -->
                <div class="mb-6 bg-gray-800 rounded-lg shadow p-6 border border-gray-700">
                    <h2 class="text-lg font-semibold mb-4 text-white">Inference</h2>
                    <p class="text-xs text-gray-400 mb-4">Simplified summaries for orchestrator readability</p>
                    <div id="lmstudio-inference" class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-700">
                            <thead class="bg-gray-700">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Model</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Summary</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Time</th>
                                </tr>
                            </thead>
                            <tbody id="lmstudio-inference-body" class="bg-gray-800 divide-y divide-gray-700">
                            </tbody>
                        </table>
                        <div id="lmstudio-inference-empty" class="text-sm text-gray-400 py-4 text-center">No inference activity</div>
                    </div>
                </div>
                
                <!-- Recent Activity (Detailed) -->
                <div class="bg-gray-800 rounded-lg shadow p-6 border border-gray-700">
                    <h2 class="text-lg font-semibold mb-4 text-white">Recent Activity (Last 2 Days)</h2>
                    <div id="lmstudio-activity" class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-700">
                            <thead class="bg-gray-700">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Model</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Input Tokens</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Output Tokens</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Duration</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">File/Process</th>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Time</th>
                                </tr>
                            </thead>
                            <tbody id="lmstudio-activity-body" class="bg-gray-800 divide-y divide-gray-700">
                            </tbody>
                        </table>
                        <div id="lmstudio-activity-empty" class="text-sm text-gray-400 py-4 text-center">No recent activity</div>
                    </div>
                </div>
            </div>
            
            <div class="mt-6 text-sm text-gray-400 text-center">
                Last updated: <span id="last-updated"></span>
            </div>
        </div>
    </div>
    
    <script>
        let currentTab = 'ollama';
        
        function switchTab(tab) {
            currentTab = tab;
            
            // Update tab buttons
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('text-blue-400', 'border-blue-400');
                btn.classList.add('text-gray-400', 'border-transparent');
            });
            
            if (tab === 'ollama') {
                document.getElementById('tab-ollama').classList.remove('text-gray-400', 'border-transparent');
                document.getElementById('tab-ollama').classList.add('text-blue-400', 'border-blue-400');
                document.getElementById('tab-content-ollama').classList.remove('hidden');
                document.getElementById('tab-content-lmstudio').classList.add('hidden');
            } else {
                document.getElementById('tab-lmstudio').classList.remove('text-gray-400', 'border-transparent');
                document.getElementById('tab-lmstudio').classList.add('text-blue-400', 'border-blue-400');
                document.getElementById('tab-content-lmstudio').classList.remove('hidden');
                document.getElementById('tab-content-ollama').classList.add('hidden');
            }
        }
        
        function formatTimestamp(ts) {
            if (!ts) return '—';
            try {
                const date = new Date(ts);
                return date.toLocaleString();
            } catch {
                return ts;
            }
        }
        
        function formatDuration(ms) {
            if (ms == null) return '—';
            if (ms < 1000) return `${Math.round(ms)}ms`;
            return `${(ms / 1000).toFixed(2)}s`;
        }
        
        function getStatusColor(status) {
            if (status === 'success' || status === 'completed') return 'text-green-400';
            if (status === 'error' || status === 'failed') return 'text-red-400';
            if (status === 'pending' || status === 'active') return 'text-yellow-400';
            return 'text-gray-300';
        }
        
        async function loadInferenceModels() {
            try {
                const response = await fetch('/api/inference/models');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                
                // Hide loading, show content
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('content').classList.remove('hidden');
                
                // Update last updated
                document.getElementById('last-updated').textContent = formatTimestamp(data.last_updated);
                
                // Calculate summary statistics
                const ollama = data.ollama;
                const lmstudio = data.lmstudio;
                const allRecent = [
                    ...(ollama.recent_requests || []),
                    ...(lmstudio.recent_activity || [])
                ];
                const allActive = [
                    ...(ollama.active_requests || [])
                ];
                
                const totalRequests = allRecent.length;
                const errors = allRecent.filter(r => r.status === 'error').length;
                const durations = allRecent.filter(r => r.durationMs != null).map(r => r.durationMs);
                const avgDuration = durations.length > 0 
                    ? (durations.reduce((a, b) => a + b, 0) / durations.length).toFixed(0) + 'ms'
                    : '—';
                const active = allActive.length;
                
                // Update summary cards
                document.getElementById('summary-total').textContent = totalRequests;
                document.getElementById('summary-errors').textContent = errors;
                document.getElementById('summary-avg-duration').textContent = avgDuration;
                document.getElementById('summary-active').textContent = active;
                
        function getStatusColor(status) {
            if (status === 'success' || status === 'completed') return 'text-green-400';
            if (status === 'error' || status === 'failed') return 'text-red-400';
            if (status === 'pending' || status === 'active') return 'text-yellow-400';
            return 'text-gray-300';
        }
        
                // Ollama data
                const ollamaStatus = document.getElementById('ollama-status');
                if (ollama.available) {
                    ollamaStatus.innerHTML = `<span class="text-green-400 font-semibold">✓ Available</span><br><span class="text-xs text-gray-400">${ollama.base_url}</span>`;
                } else {
                    ollamaStatus.innerHTML = `<span class="text-red-400 font-semibold">✗ Unavailable</span><br><span class="text-xs text-gray-400">${ollama.base_url}</span>`;
                }
                
                // Ollama models (only recently used)
                const ollamaModelsEl = document.getElementById('ollama-models');
                if (ollama.recently_used_models && ollama.recently_used_models.length > 0) {
                    ollamaModelsEl.innerHTML = ollama.recently_used_models.map(m => 
                        `<div class="mb-1"><span class="font-medium text-sm text-white">${m.name || m.id}</span></div>`
                    ).join('');
                } else {
                    ollamaModelsEl.textContent = 'No models used in last 2 days';
                }
                
                // Ollama inference section
                const ollamaInferenceBody = document.getElementById('ollama-inference-body');
                const ollamaInferenceEmpty = document.getElementById('ollama-inference-empty');
                if (ollama.recent_requests && ollama.recent_requests.length > 0) {
                    ollamaInferenceEmpty.classList.add('hidden');
                    ollamaInferenceBody.innerHTML = ollama.recent_requests.slice(0, 10).map(req => `
                        <tr>
                            <td class="px-4 py-2 text-sm text-white">${req.model || '—'}</td>
                            <td class="px-4 py-2 text-sm text-gray-300 font-medium">${req.inference_summary || '—'}</td>
                            <td class="px-4 py-2 text-sm ${getStatusColor(req.status)}">${req.status || '—'}</td>
                            <td class="px-4 py-2 text-sm text-gray-400">${formatTimestamp(req.timestamp)}</td>
                        </tr>
                    `).join('');
                } else {
                    ollamaInferenceBody.innerHTML = '';
                    ollamaInferenceEmpty.classList.remove('hidden');
                }
                
                // Ollama active requests
                const ollamaActiveBody = document.getElementById('ollama-active-body');
                const ollamaActiveEmpty = document.getElementById('ollama-active-empty');
                if (ollama.active_requests && ollama.active_requests.length > 0) {
                    ollamaActiveEmpty.classList.add('hidden');
                    ollamaActiveBody.innerHTML = ollama.active_requests.map(req => `
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-white">${req.model || '—'}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">${req.endpoint || '—'}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm ${getStatusColor(req.status)}">${req.status || 'pending'}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">${formatTimestamp(req.timestamp)}</td>
                            <td class="px-6 py-4 text-sm text-gray-300 max-w-xs truncate">${req.promptPreview || '—'}</td>
                        </tr>
                    `).join('');
                } else {
                    ollamaActiveBody.innerHTML = '';
                    ollamaActiveEmpty.classList.remove('hidden');
                }
                
                // Ollama recent requests (detailed)
                const ollamaRecentBody = document.getElementById('ollama-recent-body');
                const ollamaRecentEmpty = document.getElementById('ollama-recent-empty');
                if (ollama.recent_requests && ollama.recent_requests.length > 0) {
                    ollamaRecentEmpty.classList.add('hidden');
                    ollamaRecentBody.innerHTML = ollama.recent_requests.map(req => `
                        <tr>
                            <td class="px-4 py-2 text-sm text-white">${req.model || '—'}</td>
                            <td class="px-4 py-2 text-sm text-gray-400">${req.endpoint || '—'}</td>
                            <td class="px-4 py-2 text-sm ${getStatusColor(req.status)}">${req.status || '—'}</td>
                            <td class="px-4 py-2 text-sm text-gray-400">${formatDuration(req.durationMs)}</td>
                            <td class="px-4 py-2 text-sm text-gray-400">${req.outputTokens != null ? req.outputTokens : '—'}</td>
                            <td class="px-4 py-2 text-sm text-gray-400">${formatTimestamp(req.timestamp)}</td>
                        </tr>
                    `).join('');
                } else {
                    ollamaRecentBody.innerHTML = '';
                    ollamaRecentEmpty.classList.remove('hidden');
                }
                
                // LM Studio data
                const lmstudioStatus = document.getElementById('lmstudio-status');
                if (lmstudio.available) {
                    lmstudioStatus.innerHTML = `<span class="text-green-400 font-semibold">✓ Available</span><br><span class="text-xs text-gray-400">${lmstudio.base_urls.join(', ')}</span>`;
                } else {
                    lmstudioStatus.innerHTML = `<span class="text-red-400 font-semibold">✗ Unavailable</span>${lmstudio.base_urls.length > 0 ? `<br><span class="text-xs text-gray-400">${lmstudio.base_urls.join(', ')}</span>` : ''}`;
                }
                
                // LM Studio models (only recently used)
                const lmstudioModelsEl = document.getElementById('lmstudio-models');
                if (lmstudio.recently_used_models && lmstudio.recently_used_models.length > 0) {
                    lmstudioModelsEl.innerHTML = lmstudio.recently_used_models.map(m => 
                        `<div class="mb-1"><span class="font-medium text-sm text-white">${m.id}</span> <span class="text-gray-400 text-xs">(${m.base_url})</span></div>`
                    ).join('');
                } else {
                    lmstudioModelsEl.textContent = 'No models used in last 2 days';
                }
                
                // LM Studio inference section
                const lmstudioInferenceBody = document.getElementById('lmstudio-inference-body');
                const lmstudioInferenceEmpty = document.getElementById('lmstudio-inference-empty');
                if (lmstudio.recent_activity && lmstudio.recent_activity.length > 0) {
                    lmstudioInferenceEmpty.classList.add('hidden');
                    lmstudioInferenceBody.innerHTML = lmstudio.recent_activity.slice(0, 10).map(act => `
                        <tr>
                            <td class="px-4 py-2 text-sm text-white">${act.model || '—'}</td>
                            <td class="px-4 py-2 text-sm text-gray-300 font-medium">${act.inference_summary || '—'}</td>
                            <td class="px-4 py-2 text-sm ${getStatusColor(act.status)}">${act.status || '—'}</td>
                            <td class="px-4 py-2 text-sm text-gray-400">${formatTimestamp(act.timestamp)}</td>
                        </tr>
                    `).join('');
                } else {
                    lmstudioInferenceBody.innerHTML = '';
                    lmstudioInferenceEmpty.classList.remove('hidden');
                }
                
                // LM Studio activity (detailed)
                const lmstudioActivityBody = document.getElementById('lmstudio-activity-body');
                const lmstudioActivityEmpty = document.getElementById('lmstudio-activity-empty');
                if (lmstudio.recent_activity && lmstudio.recent_activity.length > 0) {
                    lmstudioActivityEmpty.classList.add('hidden');
                    lmstudioActivityBody.innerHTML = lmstudio.recent_activity.map(act => `
                        <tr>
                            <td class="px-4 py-2 text-sm text-white">${act.model || '—'}</td>
                            <td class="px-4 py-2 text-sm ${getStatusColor(act.status)}">${act.status || '—'}</td>
                            <td class="px-4 py-2 text-sm text-gray-400">${act.input_tokens != null ? act.input_tokens : '—'}</td>
                            <td class="px-4 py-2 text-sm text-gray-400">${act.output_tokens != null ? act.output_tokens : '—'}</td>
                            <td class="px-4 py-2 text-sm text-gray-400">${formatDuration(act.duration_ms)}</td>
                            <td class="px-4 py-2 text-sm text-gray-400">${act.file_context || '—'}</td>
                            <td class="px-4 py-2 text-sm text-gray-400">${formatTimestamp(act.timestamp)}</td>
                        </tr>
                    `).join('');
                } else {
                    lmstudioActivityBody.innerHTML = '';
                    lmstudioActivityEmpty.classList.remove('hidden');
                }
                
            } catch (error) {
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('error').classList.remove('hidden');
                document.getElementById('error').textContent = `Error loading inference models: ${error.message}`;
            }
        }
        
        // Load on page load
        loadInferenceModels();
        
        // Auto-refresh every 3 seconds
        setInterval(loadInferenceModels, 3000);
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page() -> HTMLResponse:
    """HTML dashboard page providing overview of system health and LM insights."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Gemantria</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-ok { background-color: #10b981; }
        .status-warn { background-color: #f59e0b; }
        .status-error { background-color: #ef4444; }
        .status-down { background-color: #ef4444; }
        .status-unknown { background-color: #6b7280; }
    </style>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold mb-2">System Dashboard</h1>
        <p class="text-gray-600 mb-6">Overview of system health and LM activity.</p>
        
        <div id="loading" class="text-gray-600">Loading dashboard data...</div>
        
        <div id="dashboard-content" class="hidden">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <!-- System Health Card -->
                <div id="system-health-card" class="bg-white rounded-lg shadow p-6 border border-gray-200">
                    <h2 class="text-xl font-semibold mb-4">System Health</h2>
                    
                    <div id="system-health-loading" class="text-sm text-gray-500">Loading...</div>
                    <div id="system-health-content" class="hidden">
                        <div class="mb-4">
                            <div id="system-status-badge" class="inline-block px-3 py-1 rounded-full text-white font-semibold text-sm mb-2"></div>
                            <div id="system-headline" class="text-lg font-medium text-gray-800 mb-2"></div>
                        </div>
                        
                        <div class="space-y-2 text-sm">
                            <div id="db-summary" class="text-gray-700"></div>
                            <div id="lm-summary" class="text-gray-700"></div>
                        </div>
                        
                        <div class="mt-4 pt-4 border-t border-gray-200">
                            <a href="/status" class="text-blue-600 hover:text-blue-800 text-sm font-medium">View details →</a>
                        </div>
                    </div>
                    <div id="system-health-error" class="hidden text-sm text-red-600">
                        Data unavailable
                    </div>
                </div>
                
                <!-- Inference Models Insight Card -->
                <div id="lm-insights-card" class="bg-white rounded-lg shadow p-6 border border-gray-200">
                    <h2 class="text-xl font-semibold mb-1">Inference Models Insight</h2>
                    <p class="text-xs text-gray-500 mb-4 italic">Real-time monitoring of Ollama and LM Studio inference models</p>
                    
                    <div id="lm-insights-loading" class="text-sm text-gray-500">Loading...</div>
                    <div id="lm-insights-content" class="hidden">
                        <div class="mb-4">
                            <div id="lm-status-badge" class="inline-block px-3 py-1 rounded-full text-white font-semibold text-sm mb-2"></div>
                            <div id="lm-reason" class="text-sm text-gray-600 mb-2"></div>
                        </div>
                        
                        <div class="space-y-2 text-sm">
                            <div id="lm-metrics" class="text-gray-700"></div>
                        </div>
                        
                        <div class="mt-4 pt-4 border-t border-gray-200">
                            <a href="/lm-insights" class="text-blue-600 hover:text-blue-800 text-sm font-medium">View details →</a>
                        </div>
                    </div>
                    <div id="lm-insights-error" class="hidden text-sm text-red-600">
                        Data unavailable
                    </div>
                </div>
                
                <!-- Rerank / Edge Strength Metrics Card -->
                <div id="rerank-metrics-card" class="bg-white rounded-lg shadow p-6 border border-gray-200">
                    <h2 class="text-xl font-semibold mb-1">Rerank / Edge Strength Metrics</h2>
                    <p class="text-xs text-gray-500 mb-4 italic">Granite rerank metrics (advisory; core health still via /status + /lm-insights)</p>
                    
                    <div id="rerank-metrics-loading" class="text-sm text-gray-500">Loading...</div>
                    <div id="rerank-metrics-content" class="hidden">
                        <div class="space-y-2 text-sm">
                            <div id="rerank-nodes" class="text-gray-700"></div>
                            <div id="rerank-edges" class="text-gray-700"></div>
                        </div>
                        
                        <!-- Edge Strength Bar Chart -->
                        <div id="rerank-chart-container" class="mt-4 mb-4">
                            <div class="text-xs font-semibold text-gray-600 mb-2">Edge Strength Distribution</div>
                            <div id="rerank-chart" class="space-y-2">
                                <!-- Chart bars will be rendered here by JavaScript -->
                            </div>
                            <div id="rerank-chart-empty" class="text-xs text-gray-400 italic hidden">
                                No edge data available yet
                            </div>
                        </div>
                        
                        <div class="space-y-2 text-sm">
                            <div id="rerank-strong" class="text-gray-700"></div>
                            <div id="rerank-weak" class="text-gray-700"></div>
                            <div id="rerank-avg-strength" class="text-gray-700"></div>
                        </div>
                        
                        <!-- Explanatory Text -->
                        <div class="mt-4 pt-3 border-t border-gray-200">
                            <p class="text-xs text-gray-600 leading-relaxed">
                                <strong>Edge Strength</strong> is computed as <code class="text-xs bg-gray-100 px-1 rounded">0.5 * cosine + 0.5 * rerank_score</code>.
                                Edges are classified as <strong>strong</strong> (≥0.90), <strong>weak</strong> (≥0.75), or <strong>other</strong> (&lt;0.75).
                                Strong edges indicate high semantic similarity and rerank confidence.
                            </p>
                        </div>
                        
                        <div id="rerank-note" class="mt-2 text-xs text-gray-500 italic"></div>
                    </div>
                    <div id="rerank-metrics-error" class="hidden text-sm text-red-600">
                        Data unavailable
                    </div>
                </div>
            </div>
        </div>
        
        <div id="error" class="hidden text-red-600 mt-4"></div>
    </div>
    
    <script>
        async function loadDashboard() {
            // Hide loading, show content
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('dashboard-content').classList.remove('hidden');
            
            // Load System Health
            await loadSystemHealth();
            
            // Load LM Insights
            await loadLMInsights();
            
            // Load Rerank Metrics
            await loadRerankMetrics();
        }
        
        async function loadSystemHealth() {
            try {
                // Fetch system status
                const statusResponse = await fetch('/api/status/system');
                if (!statusResponse.ok) {
                    throw new Error(`HTTP ${statusResponse.status}: ${statusResponse.statusText}`);
                }
                const statusData = await statusResponse.json();
                
                // Hide loading, show content
                document.getElementById('system-health-loading').classList.add('hidden');
                document.getElementById('system-health-error').classList.add('hidden');
                document.getElementById('system-health-content').classList.remove('hidden');
                
                // Fetch explanation (optional, don't fail if it errors)
                let explanationData = null;
                try {
                    const explainResponse = await fetch('/api/status/explain');
                    if (explainResponse.ok) {
                        explanationData = await explainResponse.json();
                    }
                } catch (e) {
                    // Explanation is optional, continue without it
                    console.warn('Failed to load explanation:', e);
                }
                
                // Update status badge (use explanation level if available, otherwise infer from status)
                let level = explanationData?.level;
                if (!level) {
                    // Infer level from DB and LM status
                    const db = statusData.db || {};
                    const lm = statusData.lm || {};
                    const dbOk = db.mode === 'ready' && db.reachable;
                    const lmOk = (lm.slots || []).some((s) => s.service === 'OK');
                    if (!dbOk || !lmOk) {
                        level = db.mode === 'db_off' || !lmOk ? 'ERROR' : 'WARN';
                    } else {
                        level = 'OK';
                    }
                }
                
                const statusBadge = document.getElementById('system-status-badge');
                if (level === 'ERROR') {
                    statusBadge.className = 'inline-block px-3 py-1 rounded-full text-white font-semibold text-sm mb-2 bg-red-500';
                    statusBadge.textContent = 'ERROR';
                } else if (level === 'WARN') {
                    statusBadge.className = 'inline-block px-3 py-1 rounded-full text-white font-semibold text-sm mb-2 bg-yellow-500';
                    statusBadge.textContent = 'WARN';
                } else {
                    statusBadge.className = 'inline-block px-3 py-1 rounded-full text-white font-semibold text-sm mb-2 bg-green-500';
                    statusBadge.textContent = 'OK';
                }
                
                // Update headline
                const headline = document.getElementById('system-headline');
                headline.textContent = explanationData?.headline || 'System status summary';
                
                // Update DB summary
                const db = statusData.db || {};
                const dbSummary = document.getElementById('db-summary');
                let dbText = 'DB: ';
                if (db.mode === 'ready' && db.reachable) {
                    dbText += 'ready ✅';
                } else if (db.mode === 'partial') {
                    dbText += 'partial ⚠️';
                } else {
                    dbText += 'db_off ❌';
                }
                dbSummary.textContent = dbText;
                
                // Update LM summary
                const lm = statusData.lm || {};
                const lmSummary = document.getElementById('lm-summary');
                const slots = lm.slots || [];
                const okSlots = slots.filter((s) => s.service === 'OK').length;
                const totalSlots = slots.length;
                if (totalSlots === 0) {
                    lmSummary.textContent = 'LM: No slots configured';
                } else {
                    lmSummary.textContent = `LM: ${okSlots}/${totalSlots} slots OK`;
                }
                
                // Note: KB Doc Metrics display is available on /status page
                // Dashboard shows simplified summary only
                
            } catch (error) {
                console.error('Failed to load system health:', error);
                document.getElementById('system-health-loading').classList.add('hidden');
                document.getElementById('system-health-content').classList.add('hidden');
                document.getElementById('system-health-error').classList.remove('hidden');
                document.getElementById('system-health-error').textContent = `Error: ${error.message || 'Failed to load system health'}`;
            }
        }
        
        async function loadLMInsights() {
            try {
                const response = await fetch('/api/lm/indicator');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                
                // Hide loading
                document.getElementById('lm-insights-loading').classList.add('hidden');
                
                if (!data.snapshot) {
                    // Show informative message if no snapshot (this is expected if exports haven't run)
                    document.getElementById('lm-insights-error').classList.remove('hidden');
                    document.getElementById('lm-insights-error').textContent = data.note || 'LM indicator data not available. Run exports to populate.';
                    document.getElementById('lm-insights-content').classList.add('hidden');
                    return;
                }
                
                // Show content
                document.getElementById('lm-insights-error').classList.add('hidden');
                document.getElementById('lm-insights-content').classList.remove('hidden');
                
                const snapshot = data.snapshot;
                
                // Update status badge
                const statusBadge = document.getElementById('lm-status-badge');
                if (snapshot.status === 'healthy') {
                    statusBadge.className = 'inline-block px-3 py-1 rounded-full text-white font-semibold text-sm mb-2 bg-green-500';
                    statusBadge.textContent = 'Healthy';
                } else if (snapshot.status === 'degraded') {
                    statusBadge.className = 'inline-block px-3 py-1 rounded-full text-white font-semibold text-sm mb-2 bg-yellow-500';
                    statusBadge.textContent = 'Degraded';
                } else {
                    statusBadge.className = 'inline-block px-3 py-1 rounded-full text-white font-semibold text-sm mb-2 bg-red-500';
                    statusBadge.textContent = 'Offline';
                }
                
                // Update reason
                const reason = document.getElementById('lm-reason');
                reason.textContent = snapshot.reason || snapshot.top_error_reason || 'No details available';
                
                // Update metrics
                const metrics = document.getElementById('lm-metrics');
                const totalCalls = snapshot.total_calls || 0;
                const successRate = ((snapshot.success_rate || 0) * 100).toFixed(1);
                metrics.textContent = `Total Calls: ${totalCalls} | Success Rate: ${successRate}%`;
                
            } catch (error) {
                console.error('Failed to load LM insights:', error);
                document.getElementById('lm-insights-loading').classList.add('hidden');
                document.getElementById('lm-insights-content').classList.add('hidden');
                document.getElementById('lm-insights-error').classList.remove('hidden');
                document.getElementById('lm-insights-error').textContent = `Error: ${error.message || 'Failed to load LM insights'}`;
            }
        }
        
        // Load dashboard on page load
        loadDashboard();
        
        async function loadRerankMetrics() {
            try {
                const response = await fetch('/api/rerank/summary');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                
                // Hide loading, show content
                document.getElementById('rerank-metrics-loading').classList.add('hidden');
                document.getElementById('rerank-metrics-error').classList.add('hidden');
                document.getElementById('rerank-metrics-content').classList.remove('hidden');
                
                // Update metrics
                document.getElementById('rerank-nodes').textContent = `Nodes: ${data.nodes || 0}`;
                document.getElementById('rerank-edges').textContent = `Edges: ${data.edges || 0}`;
                document.getElementById('rerank-strong').textContent = `Strong edges: ${data.strong_edges || 0}`;
                document.getElementById('rerank-weak').textContent = `Weak edges: ${data.weak_edges || 0}`;
                
                const avgStrength = data.avg_edge_strength;
                if (avgStrength !== null && avgStrength !== undefined) {
                    document.getElementById('rerank-avg-strength').textContent = `Avg edge strength: ${avgStrength.toFixed(4)}`;
                } else {
                    document.getElementById('rerank-avg-strength').textContent = 'Avg edge strength: N/A';
                }
                
                // Render bar chart for edge strength distribution
                const chartContainer = document.getElementById('rerank-chart');
                const chartEmpty = document.getElementById('rerank-chart-empty');
                const totalEdges = data.edges || 0;
                const strongEdges = data.strong_edges || 0;
                const weakEdges = data.weak_edges || 0;
                const otherEdges = Math.max(0, totalEdges - strongEdges - weakEdges);
                
                if (totalEdges === 0) {
                    chartContainer.classList.add('hidden');
                    chartEmpty.classList.remove('hidden');
                } else {
                    chartContainer.classList.remove('hidden');
                    chartEmpty.classList.add('hidden');
                    
                    // Clear previous chart
                    chartContainer.innerHTML = '';
                    
                    // Calculate max value for scaling
                    const maxValue = Math.max(strongEdges, weakEdges, otherEdges, 1);
                    
                    // Render bars
                    const categories = [
                        { label: 'Strong (≥0.90)', count: strongEdges, color: 'bg-green-500' },
                        { label: 'Weak (≥0.75)', count: weakEdges, color: 'bg-yellow-500' },
                        { label: 'Other (<0.75)', count: otherEdges, color: 'bg-gray-300' }
                    ];
                    
                    categories.forEach(cat => {
                        const percentage = maxValue > 0 ? (cat.count / maxValue) * 100 : 0;
                        const barHtml = `
                            <div class="flex items-center space-x-2">
                                <div class="text-xs text-gray-600 w-24 flex-shrink-0">${cat.label}</div>
                                <div class="flex-1 bg-gray-200 rounded h-6 relative overflow-hidden">
                                    <div class="${cat.color} h-full rounded transition-all duration-300" style="width: ${percentage}%"></div>
                                    <div class="absolute inset-0 flex items-center justify-center text-xs font-semibold text-gray-700">
                                        ${cat.count}
                                    </div>
                                </div>
                            </div>
                        `;
                        chartContainer.insertAdjacentHTML('beforeend', barHtml);
                    });
                }
                
                // Show note if present
                if (data.note) {
                    document.getElementById('rerank-note').textContent = data.note;
                } else {
                    document.getElementById('rerank-note').textContent = '';
                }
                
            } catch (error) {
                document.getElementById('rerank-metrics-loading').classList.add('hidden');
                document.getElementById('rerank-metrics-content').classList.add('hidden');
                document.getElementById('rerank-metrics-error').classList.remove('hidden');
            }
        }
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            loadSystemHealth();
            loadLMInsights();
            loadRerankMetrics();
        }, 30000);
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/api/db/health_timeline")
async def get_db_health_timeline_endpoint() -> JSONResponse:
    """Get DB health timeline snapshot for visualization.

    Returns:
        JSON with DB health timeline data:
        {
            "snapshots": [
                {
                    "generated_at": "2025-11-15T02:33:53.743825+00:00",
                    "mode": "ready" | "partial" | "db_off",
                    "notes": str,
                    "ok": bool
                },
                ...
            ],
            "note": str (if snapshots is empty)
        }
        Uses shared eval exports helper (hermetic, tolerant of missing files).
    """
    from datetime import datetime

    try:
        db_health_data = load_db_health_snapshot()

        # Check if data is available
        if not db_health_data.get("available", False):
            return JSONResponse(
                content={
                    "snapshots": [],
                    "note": db_health_data.get(
                        "note",
                        "DB health data not available; run `make pm.snapshot` to populate this chart.",
                    ),
                }
            )

        # Remove internal fields
        db_health_clean = {k: v for k, v in db_health_data.items() if k not in ("available", "note")}

        # Transform to timeline shape (single snapshot for now)
        mode = db_health_clean.get("mode", "db_off")
        ok = db_health_clean.get("ok", False)
        errors = db_health_clean.get("details", {}).get("errors", [])

        # Build notes
        if mode == "ready" and ok:
            notes = "Database is ready and all checks passed"
        elif mode == "partial":
            notes = f"Database connected but some tables missing: {errors[0] if errors else 'unknown'}"
        elif mode == "db_off":
            notes = f"Database unavailable: {errors[0] if errors else 'connection failed'}"
        else:
            notes = f"Unknown status: {mode}"

        # Create snapshot with generated_at (use current time if not present)
        generated_at = db_health_clean.get("generated_at")
        if not generated_at:
            generated_at = datetime.now(UTC).isoformat()

        snapshot = {
            "generated_at": generated_at,
            "mode": mode,
            "notes": notes,
            "ok": ok,
        }

        return JSONResponse(
            content={
                "snapshots": [snapshot],
            }
        )

    except Exception as e:
        LOG.error(f"Error getting DB health timeline: {e}")
        return JSONResponse(
            content={
                "snapshots": [],
                "note": f"Failed to load DB health timeline data: {e}",
            }
        )


@app.get("/api/eval/edges")
async def get_eval_edges_endpoint() -> JSONResponse:
    """Get edge class counts for visualization.

    Returns:
        JSON with edge class counts:
        {
            "data": {
                "thresholds": {"strong": float, "weak": float},
                "counts": {"strong": int, "weak": int, "other": int}
            } | null,
            "note": str (if data is null)
        }
        Uses shared eval exports helper (hermetic, tolerant of missing files).
    """
    try:
        edge_data = load_edge_class_counts()

        # Check if data is available
        if not edge_data.get("available", False):
            return JSONResponse(
                content={
                    "data": None,
                    "note": edge_data.get(
                        "note",
                        "Edge class counts not available; run `make eval.reclassify` to populate this data.",
                    ),
                }
            )

        # Remove internal fields before returning
        data = {k: v for k, v in edge_data.items() if k not in ("available", "note")}

        return JSONResponse(
            content={
                "data": data,
            }
        )

    except Exception as e:
        LOG.error(f"Error getting edge class counts: {e}")
        return JSONResponse(
            content={
                "data": None,
                "note": f"Failed to load edge class counts: {e}",
            }
        )


@app.get("/api/rerank/summary")
async def get_rerank_summary_endpoint() -> JSONResponse:
    """Get rerank/edge strength metrics summary.

    Returns:
        JSON with rerank metrics:
        {
            "nodes": int,
            "edges": int,
            "strong_edges": int,
            "weak_edges": int,
            "avg_edge_strength": float | null,
            "note": str (if data is missing)
        }
        Gracefully handles missing files in hermetic/empty-DB runs.
    """
    try:
        # Load graph stats
        graph_stats_path = get_export_path("graph_stats.json")
        graph_stats = load_json_file(graph_stats_path)
        nodes = graph_stats.get("nodes", 0)
        edges = graph_stats.get("edges", 0)

        # Load edge class counts
        edge_data = load_edge_class_counts()
        strong_edges = 0
        weak_edges = 0
        if edge_data.get("available", False):
            counts = edge_data.get("counts", {})
            strong_edges = counts.get("strong", 0)
            weak_edges = counts.get("weak", 0)

        # Try to get avg_edge_strength from graph_latest.json metadata
        avg_edge_strength = None
        graph_latest_path = get_export_path("graph_latest.json")
        graph_latest = load_json_file(graph_latest_path)
        if graph_latest:
            metadata = graph_latest.get("metadata", {})
            if "avg_edge_strength" in metadata:
                avg_edge_strength = metadata.get("avg_edge_strength")
            # Also check network_aggregation_summary if present
            elif "network_aggregation_summary" in metadata:
                summary = metadata.get("network_aggregation_summary", {})
                if "avg_edge_strength" in summary:
                    avg_edge_strength = summary.get("avg_edge_strength")

        # Build response
        response = {
            "nodes": nodes,
            "edges": edges,
            "strong_edges": strong_edges,
            "weak_edges": weak_edges,
            "avg_edge_strength": avg_edge_strength,
        }

        # Add note if data is incomplete
        if not graph_stats or nodes == 0:
            response["note"] = "Graph stats not available; run pipeline to populate data."
        elif not edge_data.get("available", False):
            response["note"] = "Edge class counts not available; run `make eval.reclassify` to populate."

        return JSONResponse(content=response)

    except Exception as e:
        LOG.error(f"Error getting rerank summary: {e}")
        return JSONResponse(
            content={
                "nodes": 0,
                "edges": 0,
                "strong_edges": 0,
                "weak_edges": 0,
                "avg_edge_strength": None,
                "note": f"Failed to load rerank summary: {e}",
            }
        )


@app.get("/db-insights", response_class=HTMLResponse)
async def db_insights_page() -> HTMLResponse:
    """HTML page showing DB health timeline insights with chart."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DB Insights - Gemantria</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-2">DB Health Timeline</h1>
        <p class="text-gray-600 mb-2 text-sm">Recent DB health history (advisory only; not used for health gates)</p>
        <p class="text-gray-500 mb-6 text-xs italic">Note: System health status is determined by the unified snapshot API, not by these analytics.</p>
        
        <div id="loading" class="text-gray-600">Loading DB health data...</div>
        
        <div id="no-data" class="hidden bg-yellow-50 border border-yellow-200 rounded-lg shadow p-6 mb-6">
            <p class="text-yellow-800">
                No DB health snapshots available yet; run `make pm.snapshot` to populate this chart.
            </p>
        </div>
        
        <div id="insights-content" class="hidden">
            <!-- Status Indicator -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h2 class="text-xl font-semibold mb-4">Current Status</h2>
                <div id="status-indicator" class="flex items-center mb-4">
                    <span id="status-badge" class="px-4 py-2 rounded-full text-white font-semibold"></span>
                    <span id="status-text" class="ml-3 text-lg"></span>
                </div>
                <div id="status-details" class="text-sm text-gray-600"></div>
            </div>
            
            <!-- Health Timeline Chart -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h2 class="text-xl font-semibold mb-4">Health Mode Over Time</h2>
                <canvas id="dbHealthChart" class="max-h-96"></canvas>
            </div>
            
            <!-- Summary -->
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Summary</h2>
                <div class="space-y-2 text-sm">
                    <div><strong>Latest Mode:</strong> <span id="latest-mode"></span></div>
                    <div><strong>Status:</strong> <span id="latest-status"></span></div>
                    <div><strong>Generated:</strong> <span id="latest-generated"></span></div>
                    <div><strong>Notes:</strong> <span id="latest-notes" class="text-gray-600"></span></div>
                </div>
            </div>
        </div>
        
        <div id="error" class="hidden text-red-600 mt-4"></div>
    </div>
    
    <script>
        let chart = null;
        
        // Map mode to numeric value for chart
        function modeToValue(mode) {
            if (mode === 'ready') return 2;
            if (mode === 'partial') return 1;
            return 0; // db_off
        }
        
        function valueToMode(value) {
            if (value === 2) return 'ready';
            if (value === 1) return 'partial';
            return 'db_off';
        }
        
        async function loadDBHealthTimeline() {
            try {
                const response = await fetch('/api/db/health_timeline');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                
                // Hide loading
                document.getElementById('loading').classList.add('hidden');
                
                if (!data.snapshots || data.snapshots.length === 0) {
                    // Show no-data message
                    document.getElementById('no-data').classList.remove('hidden');
                    return;
                }
                
                // Show content
                document.getElementById('insights-content').classList.remove('hidden');
                
                const snapshots = data.snapshots;
                const latest = snapshots[snapshots.length - 1];
                
                // Update status indicator
                const statusBadge = document.getElementById('status-badge');
                const statusText = document.getElementById('status-text');
                const statusDetails = document.getElementById('status-details');
                
                let statusColor = 'bg-gray-500';
                let statusLabel = 'Unknown';
                if (latest.mode === 'ready') {
                    statusColor = 'bg-green-500';
                    statusLabel = 'Ready';
                } else if (latest.mode === 'partial') {
                    statusColor = 'bg-yellow-500';
                    statusLabel = 'Partial';
                } else {
                    statusColor = 'bg-red-500';
                    statusLabel = 'Offline';
                }
                
                statusBadge.className = `px-4 py-2 rounded-full text-white font-semibold ${statusColor}`;
                statusText.textContent = statusLabel;
                statusDetails.textContent = latest.notes || 'No details available';
                
                // Update summary
                document.getElementById('latest-mode').textContent = latest.mode;
                document.getElementById('latest-status').textContent = latest.ok ? 'OK ✓' : 'Not OK ✗';
                document.getElementById('latest-generated').textContent = new Date(latest.generated_at).toLocaleString();
                document.getElementById('latest-notes').textContent = latest.notes || 'No notes';
                
                // Prepare chart data
                const labels = snapshots.map(s => {
                    const date = new Date(s.generated_at);
                    return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
                });
                const values = snapshots.map(s => modeToValue(s.mode));
                
                // Destroy existing chart if it exists
                if (chart) {
                    chart.destroy();
                }
                
                // Create chart
                const ctx = document.getElementById('dbHealthChart').getContext('2d');
                chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'DB Health Mode',
                            data: values,
                            borderColor: 'rgb(59, 130, 246)',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            tension: 0.1,
                            pointRadius: 6,
                            pointHoverRadius: 8,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 2.5,
                                ticks: {
                                    stepSize: 1,
                                    callback: function(value) {
                                        return valueToMode(value);
                                    }
                                },
                                title: {
                                    display: true,
                                    text: 'Health Mode'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Time'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const mode = valueToMode(context.parsed.y);
                                        const snapshot = snapshots[context.dataIndex];
                                        return `Mode: ${mode}${snapshot.ok ? ' (OK)' : ' (Not OK)'}`;
                                    }
                                }
                            }
                        }
                    }
                });
                
            } catch (error) {
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('error').classList.remove('hidden');
                document.getElementById('error').textContent = `Error loading DB health timeline: ${error.message}`;
            }
        }
        
        // Load on page load
        loadDBHealthTimeline();
        
        // Auto-refresh every 30 seconds
        setInterval(loadDBHealthTimeline, 30000);
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/api/bible/passage")
async def get_bible_passage(
    reference: str = Query(..., description="Bible reference (e.g., 'John 3:16-18')"),
    use_lm: bool = Query(False, description="Use AI commentary (default: False to avoid model loads)"),
) -> JSONResponse:
    """Get Bible passage and optional commentary.

    Args:
        reference: Bible reference string (e.g., "John 3:16-18").
        use_lm: If True, generate theology commentary; if False, return fallback.

    Returns:
        JSON with:
        {
            "reference": str,
            "verses": [
                {
                    "book": str,
                    "chapter": int,
                    "verse": int,
                    "text": str,
                },
                ...
            ],
            "commentary": {
                "source": "lm_theology" | "fallback",
                "text": str,
            },
            "errors": list[str],
        }
    """
    from agentpm.biblescholar.passage import get_passage_and_commentary

    try:
        result = get_passage_and_commentary(reference, use_lm=use_lm)
        return JSONResponse(content=result)
    except Exception as e:
        # Unexpected error - return 500 with error details
        return JSONResponse(
            status_code=500,
            content={
                "reference": reference,
                "verses": [],
                "commentary": {"source": "fallback", "text": f"Unexpected error: {e!s}"},
                "errors": [f"Unexpected error: {e!s}"],
            },
        )


@app.get("/api/bible/semantic-search")
async def semantic_search_endpoint(
    query: str = Query(..., description="Search query (e.g., 'hope in difficult times')"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results (1-50)"),
    translation: str = Query("KJV", description="Bible translation (default: KJV)"),
) -> JSONResponse:
    """Semantic search over Bible verses using vector embeddings.

    Args:
        query: User's search query (concepts, questions, themes).
        limit: Maximum number of results to return (1-50).
        translation: Bible translation to search (default: KJV).

    Returns:
        JSON with:
        {
            "query": str,
            "translation": str,
            "limit": int,
            "model": str,
            "results_count": int,
            "results": [
                {
                    "verse_id": int,
                    "book_name": str,
                    "chapter_num": int,
                    "verse_num": int,
                    "text": str,
                    "translation_source": str,
                    "similarity_score": float (0.0-1.0)
                },
                ...
            ],
            "generated_at": str (RFC3339)
        }
    """
    from agentpm.biblescholar.semantic_search_flow import semantic_search
    from datetime import datetime, UTC

    try:
        result = semantic_search(query=query, limit=limit, translation=translation)

        # Convert to API response format
        response = {
            "query": result.query,
            "translation": translation,
            "limit": limit,
            "model": result.model,
            "results_count": result.total_results,
            "results": [
                {
                    "verse_id": r.verse_id,
                    "book_name": r.book_name,
                    "chapter_num": r.chapter_num,
                    "verse_num": r.verse_num,
                    "text": r.text,
                    "translation_source": r.translation_source,
                    "similarity_score": r.similarity_score,
                }
                for r in result.results
            ],
            "generated_at": datetime.now(UTC).isoformat(),
        }

        return JSONResponse(content=response)
    except Exception as e:
        LOG.error(f"Error in semantic search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Semantic search failed: {e!s}",
        ) from e


class KeywordSearchRequest(BaseModel):
    query: str
    limit: int = 20
    translation: str = "KJV"


class CrossLanguageRequest(BaseModel):
    strongs_id: str
    reference: str | None = None
    limit: int = 10


@app.post("/api/bible/search")
async def keyword_search_endpoint(request: KeywordSearchRequest) -> JSONResponse:  # noqa: B008
    """Keyword search across Bible verses.

    Args:
        query: Search keyword (case-insensitive, minimum 2 characters).
        limit: Maximum number of results to return (1-100).
        translation: Bible translation to search (default: KJV).

    Returns:
        JSON with:
        {
            "query": str,
            "translation": str,
            "limit": int,
            "results_count": int,
            "results": [
                {
                    "verse_id": int,
                    "book_name": str,
                    "chapter_num": int,
                    "verse_num": int,
                    "text": str,
                    "translation_source": str
                },
                ...
            ],
            "generated_at": str (RFC3339),
            "mode": "available" | "db_off"
        }
    """
    from agentpm.biblescholar.search_flow import search_verses, get_db_status
    from datetime import datetime, UTC

    db_status = get_db_status()
    if db_status == "db_off":
        return JSONResponse(
            content={
                "query": request.query,
                "translation": request.translation,
                "limit": request.limit,
                "results_count": 0,
                "results": [],
                "generated_at": datetime.now(UTC).isoformat(),
                "mode": "db_off",
            }
        )

    try:
        results = search_verses(query=request.query, translation=request.translation, limit=request.limit)

        response = {
            "query": request.query,
            "translation": request.translation,
            "limit": request.limit,
            "results_count": len(results),
            "results": [
                {
                    "verse_id": r.verse_id,
                    "book_name": r.book_name,
                    "chapter_num": r.chapter_num,
                    "verse_num": r.verse_num,
                    "text": r.text,
                    "translation_source": r.translation_source,
                }
                for r in results
            ],
            "generated_at": datetime.now(UTC).isoformat(),
            "mode": db_status,
        }

        return JSONResponse(content=response)
    except Exception as e:
        LOG.error(f"Error in keyword search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Keyword search failed: {e!s}",
        ) from e


@app.get("/api/bible/lexicon/{strongs_id}")
async def lexicon_lookup_endpoint(strongs_id: str) -> JSONResponse:
    """Lookup lexicon entry by Strong's number.

    Args:
        strongs_id: Strong's number (e.g., "H7965" for Hebrew, "G1" for Greek).

    Returns:
        JSON with:
        {
            "strongs_id": str,
            "lemma": str,
            "gloss": str | None,
            "language": "hebrew" | "greek",
            "occurrence_count": int | None,
            "mode": "available" | "db_off"
        }
    """
    from agentpm.biblescholar.lexicon_flow import fetch_lexicon_entry
    from agentpm.biblescholar.lexicon_adapter import LexiconAdapter

    try:
        entry = fetch_lexicon_entry(strongs_id)

        if not entry:
            # Check status to determine if DB is off or entry just not found
            adapter = LexiconAdapter()
            db_status = adapter.db_status
            if db_status == "db_off":
                return JSONResponse(
                    content={
                        "strongs_id": strongs_id,
                        "lemma": "",
                        "gloss": None,
                        "language": "unknown",
                        "occurrence_count": None,
                        "mode": "db_off",
                    }
                )
            raise HTTPException(
                status_code=404,
                detail=f"Lexicon entry not found for Strong's number: {strongs_id}",
            )

        # Entry found = DB is available
        # Determine language from Strong's prefix
        is_hebrew = strongs_id.upper().startswith("H")
        language = "hebrew" if is_hebrew else "greek"

        response = {
            "strongs_id": entry.strongs_id,
            "lemma": entry.lemma,
            "gloss": entry.gloss,
            "language": language,
            "occurrence_count": None,  # Could be added if needed
            "mode": "available",
        }

        return JSONResponse(content=response)
    except HTTPException:
        raise
    except Exception as e:
        LOG.error(f"Error in lexicon lookup: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lexicon lookup failed: {e!s}",
        ) from e


@app.post("/api/bible/cross-language")
async def cross_language_endpoint(request: CrossLanguageRequest) -> JSONResponse:  # noqa: B008
    """Find Hebrew↔Greek semantic connections for a Strong's number.

    Args:
        strongs_id: Source Strong's number (e.g., "H7965" for Hebrew, "G1" for Greek).
        reference: Optional Bible reference to use as starting point.
        limit: Maximum number of connections to return (1-50).

    Returns:
        JSON with:
        {
            "strongs_id": str,
            "reference": str | None,
            "limit": int,
            "connections_count": int,
            "connections": [
                {
                    "source_strongs": str,
                    "target_strongs": str,
                    "target_lemma": str,
                    "similarity_score": float (0.0-1.0),
                    "common_verses": list[str]
                },
                ...
            ],
            "generated_at": str (RFC3339),
            "mode": "available" | "db_off"
        }
    """
    from agentpm.biblescholar.cross_language_flow import find_cross_language_connections
    from agentpm.biblescholar.lexicon_adapter import LexiconAdapter
    from datetime import datetime, UTC

    try:
        connections = find_cross_language_connections(
            strongs_id=request.strongs_id, reference=request.reference, limit=request.limit
        )
        adapter = LexiconAdapter()
        db_status = adapter.db_status

        response = {
            "strongs_id": request.strongs_id,
            "reference": request.reference,
            "limit": request.limit,
            "connections_count": len(connections),
            "connections": [
                {
                    "source_strongs": c.source_strongs,
                    "target_strongs": c.target_strongs,
                    "target_lemma": c.target_lemma,
                    "similarity_score": c.similarity_score,
                    "common_verses": c.common_verses,
                }
                for c in connections
            ],
            "generated_at": datetime.now(UTC).isoformat(),
            "mode": db_status,
        }

        return JSONResponse(content=response)
    except Exception as e:
        LOG.error(f"Error in cross-language search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Cross-language search failed: {e!s}",
        ) from e


@app.get("/api/bible/insights/{reference}")
async def insights_endpoint(
    reference: str,
    translations: str | None = Query(None, description="Comma-separated list of translations (e.g., 'ESV,ASV')"),
    include_lexicon: bool = Query(True, description="Include lexicon entries"),
    include_similar: bool = Query(True, description="Include similar verses"),
    similarity_limit: int = Query(5, ge=1, le=20, description="Number of similar verses (1-20)"),
) -> JSONResponse:
    """Get contextual insights for a Bible verse.

    Args:
        reference: Bible reference (e.g., "John 3:16").
        translations: Optional comma-separated list of additional translations.
        include_lexicon: Whether to include lexicon entries.
        include_similar: Whether to include similar verses.
        similarity_limit: Number of similar verses to fetch (1-20).

    Returns:
        JSON with:
        {
            "reference": str,
            "primary_text": str,
            "secondary_texts": dict[str, str],
            "lexicon_entries": [
                {
                    "strongs_id": str,
                    "lemma": str,
                    "gloss": str | None,
                    ...
                },
                ...
            ],
            "similar_verses": [
                {
                    "verse_id": int,
                    "book_name": str,
                    "chapter_num": int,
                    "verse_num": int,
                    "text": str,
                    "similarity_score": float
                },
                ...
            ],
            "generated_at": str (RFC3339),
            "mode": "available" | "db_off"
        }
    """
    from agentpm.biblescholar.insights_flow import get_verse_context
    from agentpm.biblescholar.lexicon_adapter import LexiconAdapter
    from datetime import datetime, UTC

    try:
        # Parse translations
        translation_list = None
        if translations:
            translation_list = [t.strip() for t in translations.split(",") if t.strip()]

        context = get_verse_context(
            reference=reference,
            translations=translation_list,
            include_lexicon=include_lexicon,
            include_similar=include_similar,
            similarity_limit=similarity_limit,
        )

        if not context:
            raise HTTPException(
                status_code=404,
                detail=f"Verse not found for reference: {reference}",
            )

        adapter = LexiconAdapter()
        db_status = adapter.db_status

        response = {
            "reference": context.reference,
            "primary_text": context.primary_text,
            "secondary_texts": context.secondary_texts,
            "lexicon_entries": [
                {
                    "strongs_id": e.strongs_id,
                    "lemma": e.lemma,
                    "gloss": e.gloss,
                }
                for e in context.lexicon_entries
            ],
            "similar_verses": [
                {
                    "verse_id": v.verse_id,
                    "book_name": v.book_name,
                    "chapter_num": v.chapter_num,
                    "verse_num": v.verse_num,
                    "text": v.text,
                    "similarity_score": v.similarity_score,
                }
                for v in context.similar_verses
            ],
            "generated_at": datetime.now(UTC).isoformat(),
            "mode": db_status,
        }

        return JSONResponse(content=response)
    except HTTPException:
        raise
    except Exception as e:
        LOG.error(f"Error in insights lookup: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Insights lookup failed: {e!s}",
        ) from e


@app.get("/api/mcp/tools/search")
async def mcp_tools_search_endpoint(
    q: str | None = Query(None, description="Search query (semantic + keyword)"),
    subsystem: str | None = Query(None, description="Filter by subsystem (e.g., 'biblescholar')"),
    visibility: str | None = Query(None, description="Filter by visibility ('internal' or 'external')"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results (1-100)"),
) -> JSONResponse:
    """Hybrid semantic + keyword search for MCP tools.

    Combines vector similarity (embedding) with keyword matching and metadata filters.

    Args:
        q: Search query (optional). If provided, performs semantic similarity search.
        subsystem: Filter by subsystem (e.g., 'biblescholar').
        visibility: Filter by visibility ('internal' or 'external').
        limit: Maximum number of results to return (1-100).

    Returns:
        JSON with:
        {
            "query": str | None,
            "filters": {
                "subsystem": str | None,
                "visibility": str | None
            },
            "limit": int,
            "results_count": int,
            "results": [
                {
                    "name": str,
                    "description": str,
                    "tags": list[str],
                    "subsystem": str | None,
                    "visibility": str,
                    "popularity_score": int,
                    "similarity_score": float | None
                },
                ...
            ],
            "generated_at": str (RFC3339),
            "mode": "available" | "db_off"
        }
    """
    from scripts.config.env import get_rw_dsn
    from datetime import datetime, UTC
    import psycopg

    try:
        dsn = get_rw_dsn()
        if not dsn:
            return JSONResponse(
                content={
                    "query": q,
                    "filters": {"subsystem": subsystem, "visibility": visibility},
                    "limit": limit,
                    "results_count": 0,
                    "results": [],
                    "generated_at": datetime.now(UTC).isoformat(),
                    "mode": "db_off",
                }
            )

        with psycopg.connect(dsn) as conn:
            # Build query with filters
            conditions = []
            params: dict[str, Any] = {}

            # Subsystem filter
            if subsystem:
                conditions.append("subsystem = %(subsystem)s")
                params["subsystem"] = subsystem

            # Visibility filter
            if visibility:
                conditions.append("visibility = %(visibility)s")
                params["visibility"] = visibility

            # Semantic search (if query provided and embedding column exists)
            query_embedding = None
            if q:
                try:
                    from agentpm.adapters.lm_studio import embed

                    embeddings = embed([q], model_slot="embedding")
                    if embeddings and embeddings[0]:
                        query_embedding = embeddings[0]
                        # Check if embedding column exists
                        with conn.cursor() as cur:
                            cur.execute(
                                """
                                SELECT EXISTS(
                                    SELECT 1 FROM information_schema.columns
                                    WHERE table_schema = 'mcp' AND table_name = 'tools'
                                    AND column_name = 'embedding'
                                )
                                """
                            )
                            has_embedding = cur.fetchone()[0]
                            if has_embedding and query_embedding:
                                # Use vector similarity with stricter threshold (0.5 instead of 0.3)
                                # This reduces noise and improves search quality
                                conditions.append(
                                    "embedding IS NOT NULL AND 1 - (embedding <=> %(query_embedding)s::vector) > 0.5"
                                )
                                params["query_embedding"] = str(query_embedding)
                            else:
                                # Fallback to keyword search
                                conditions.append('(name ILIKE %(keyword)s OR "desc" ILIKE %(keyword)s)')
                                params["keyword"] = f"%{q}%"
                    else:
                        # Fallback to keyword search
                        conditions.append('(name ILIKE %(keyword)s OR "desc" ILIKE %(keyword)s)')
                        params["keyword"] = f"%{q}%"
                except Exception as e:
                    LOG.warning(f"Embedding generation failed, using keyword search: {e}")
                    conditions.append('(name ILIKE %(keyword)s OR "desc" ILIKE %(keyword)s)')
                    params["keyword"] = f"%{q}%"
            elif q:
                # Keyword search only
                conditions.append('(name ILIKE %(keyword)s OR "desc" ILIKE %(keyword)s)')
                params["keyword"] = f"%{q}%"

            # Build SQL
            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # Order by similarity if embedding search, else by popularity
            if query_embedding and "query_embedding" in params:
                order_by = "ORDER BY 1 - (embedding <=> %(query_embedding)s::vector) DESC, popularity_score DESC"
            else:
                order_by = "ORDER BY popularity_score DESC, name ASC"

            sql = f"""
                SELECT
                    name,
                    "desc",
                    tags,
                    COALESCE(subsystem, '') as subsystem,
                    COALESCE(visibility, 'internal') as visibility,
                    COALESCE(popularity_score, 0) as popularity_score,
                    CASE
                        WHEN %(query_embedding)s::vector IS NOT NULL AND embedding IS NOT NULL
                        THEN 1 - (embedding <=> %(query_embedding)s::vector)
                        ELSE NULL
                    END as similarity_score
                FROM mcp.tools
                WHERE {where_clause}
                {order_by}
                LIMIT %(limit)s
            """
            params["limit"] = limit
            if "query_embedding" not in params:
                params["query_embedding"] = None

            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

            results = [
                {
                    "name": row[0],
                    "description": row[1] or "",
                    "tags": row[2] or [],
                    "subsystem": row[3] or None,
                    "visibility": row[4] or "internal",
                    "popularity_score": row[5] or 0,
                    "similarity_score": float(row[6]) if row[6] is not None else None,
                }
                for row in rows
            ]

            response = {
                "query": q,
                "filters": {"subsystem": subsystem, "visibility": visibility},
                "limit": limit,
                "results_count": len(results),
                "results": results,
                "generated_at": datetime.now(UTC).isoformat(),
                "mode": "available",
            }

            return JSONResponse(content=response)

    except Exception as e:
        LOG.error(f"Error in MCP tools search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"MCP tools search failed: {e!s}",
        ) from e


@app.get("/bible", response_class=HTMLResponse)
async def bible_page() -> HTMLResponse:
    """HTML page for Bible Scholar passage lookup with commentary."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bible Scholar - Gemantria</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-2">Bible Scholar</h1>
        <p class="text-gray-600 mb-6">Passage & Commentary</p>

        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <form id="passage-form" class="space-y-4">
                <div>
                    <label for="reference" class="block text-sm font-medium text-gray-700 mb-2">
                        Bible Reference
                    </label>
                    <input
                        type="text"
                        id="reference"
                        name="reference"
                        placeholder="e.g. John 3:16-18"
                        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        required
                    />
                </div>
                <div class="flex items-center">
                    <input
                        type="checkbox"
                        id="use-lm"
                        name="use_lm"
                        checked
                        class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label for="use-lm" class="ml-2 block text-sm text-gray-700">
                        Use AI commentary
                    </label>
                </div>
                <button
                    type="submit"
                    class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                    Lookup Passage
                </button>
            </form>
        </div>

        <div id="loading" class="hidden text-center py-8">
            <p class="text-gray-600">Loading...</p>
        </div>

        <div id="error" class="hidden bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p class="text-red-800" id="error-message"></p>
        </div>

        <div id="results" class="hidden space-y-6">
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-2xl font-semibold mb-4" id="passage-title"></h2>
                <div id="passage-text" class="space-y-3 text-gray-800"></div>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-xl font-semibold mb-4">Commentary</h3>
                <div id="commentary-text" class="text-gray-700 whitespace-pre-wrap"></div>
                <p class="text-sm text-gray-500 mt-2" id="commentary-source"></p>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('passage-form');
        const loading = document.getElementById('loading');
        const error = document.getElementById('error');
        const errorMessage = document.getElementById('error-message');
        const results = document.getElementById('results');
        const passageTitle = document.getElementById('passage-title');
        const passageText = document.getElementById('passage-text');
        const commentaryText = document.getElementById('commentary-text');
        const commentarySource = document.getElementById('commentary-source');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const reference = document.getElementById('reference').value.trim();
            const useLm = document.getElementById('use-lm').checked;

            if (!reference) {
                showError('Please enter a Bible reference');
                return;
            }

            // Show loading, hide results and error
            loading.classList.remove('hidden');
            results.classList.add('hidden');
            error.classList.add('hidden');

            try {
                const url = `/api/bible/passage?reference=${encodeURIComponent(reference)}&use_lm=${useLm}`;
                const response = await fetch(url);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();

                // Show errors if any
                if (data.errors && data.errors.length > 0) {
                    showError(data.errors.join('; '));
                    return;
                }

                // Display passage
                passageTitle.textContent = data.reference;
                passageText.innerHTML = '';

                if (data.verses && data.verses.length > 0) {
                    data.verses.forEach((verse) => {
                        const verseDiv = document.createElement('div');
                        verseDiv.className = 'mb-2';
                        verseDiv.innerHTML = `<span class="font-semibold text-blue-600">${verse.verse}.</span> ${verse.text}`;
                        passageText.appendChild(verseDiv);
                    });
                } else {
                    passageText.innerHTML = '<p class="text-gray-500">No verses found.</p>';
                }

                // Display commentary
                if (data.commentary) {
                    commentaryText.textContent = data.commentary.text || 'No commentary available.';
                    const sourceLabel = data.commentary.source === 'lm_theology' ? 'AI Commentary (Theology Model)' : 'Fallback (LM Unavailable)';
                    commentarySource.textContent = `Source: ${sourceLabel}`;
                } else {
                    commentaryText.textContent = 'No commentary available.';
                    commentarySource.textContent = '';
                }

                // Show results
                loading.classList.add('hidden');
                results.classList.remove('hidden');
            } catch (err) {
                loading.classList.add('hidden');
                showError(`Failed to fetch passage: ${err.message}`);
            }
        });

        function showError(message) {
            errorMessage.textContent = message;
            error.classList.remove('hidden');
        }
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


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
    min_score: float | None = Query(0.0, description="Minimum pattern score threshold"),
    pattern_type: str | None = Query(None, description="Filter by pattern type (e.g., 'louvain_community')"),
) -> JSONResponse:
    """Get pattern mining data from Phase 12 database tables.

    Returns discovered patterns and their occurrences from public.patterns
    and public.pattern_occurrences tables.
    """
    try:
        import psycopg2
        import psycopg2.extras
        from scripts.config.env import get_rw_dsn
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Database driver not available",
        )

    dsn = get_rw_dsn()
    if not dsn:
        raise HTTPException(
            status_code=503,
            detail="Database connection not configured",
        )

    try:
        conn = psycopg2.connect(dsn)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Build query with filters
        query = """
            SELECT 
                p.id,
                p.name,
                p.type,
                p.definition,
                p.metadata,
                p.created_at,
                COUNT(po.id) as occurrence_count,
                COALESCE(AVG(po.score), 0) as avg_score
            FROM public.patterns p
            LEFT JOIN public.pattern_occurrences po ON p.id = po.pattern_id
            WHERE 1=1
        """
        params = []

        if pattern_type:
            query += " AND p.type = %s"
            params.append(pattern_type)

        query += " GROUP BY p.id, p.name, p.type, p.definition, p.metadata, p.created_at"

        if min_score and min_score > 0.0:
            query += " HAVING COALESCE(AVG(po.score), 0) >= %s"
            params.append(min_score)

        query += " ORDER BY avg_score DESC, p.created_at DESC"

        if limit and limit > 0:
            query += " LIMIT %s"
            params.append(limit)

        cur.execute(query, params)
        patterns = cur.fetchall()

        # Convert to list of dicts and format
        patterns_list = []
        for pattern in patterns:
            patterns_list.append(
                {
                    "id": str(pattern["id"]),
                    "name": pattern["name"],
                    "type": pattern["type"],
                    "definition": pattern["definition"],
                    "metadata": pattern["metadata"],
                    "occurrence_count": pattern["occurrence_count"],
                    "avg_score": float(pattern["avg_score"]),
                    "created_at": pattern["created_at"].isoformat() if pattern["created_at"] else None,
                }
            )

        cur.close()
        conn.close()

        return JSONResponse(
            content={
                "patterns": patterns_list,
                "metadata": {
                    "total_count": len(patterns_list),
                    "applied_filters": {
                        "limit": limit,
                        "min_score": min_score,
                        "pattern_type": pattern_type,
                    },
                    "source": "public.patterns (Phase 12)",
                },
            }
        )

    except Exception as e:
        LOG.error(f"Error querying patterns: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve patterns: {e!s}",
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

    # Log full traceback for debugging
    LOG.error(
        f"Unhandled exception in {request.method} {request.url.path}",
        exc_info=True,
        extra={
            "path": str(request.url.path),
            "method": request.method,
            "error": str(exc),
        },
    )

    # Don't expose internal details in production
    detail = str(exc) if os.getenv("DEBUG", "0") == "1" else "Internal server error"

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": detail,
            "path": str(request.url.path),
        },
    )


@app.get("/api/health")
async def api_health_check():
    """Health check endpoint for monitoring and load balancers."""
    try:
        # Basic health checks
        checks = {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
        }

        # Check if export directory is accessible
        export_dir = os.getenv("EXPORT_DIR", "exports")
        if Path(export_dir).exists():
            checks["exports"] = "available"
        else:
            checks["exports"] = "unavailable"
            checks["status"] = "degraded"

        # Optional: Check database connectivity (non-blocking)
        try:
            from scripts.config.env import get_rw_dsn

            dsn = get_rw_dsn()
            if dsn:
                checks["database"] = "configured"
            else:
                checks["database"] = "not_configured"
        except Exception:
            checks["database"] = "unknown"

        status_code = 200 if checks["status"] == "healthy" else 503
        return JSONResponse(content=checks, status_code=status_code)

    except Exception as e:
        LOG.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time(),
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


# --- Phase-8D: Governance docs search API + UI ---


@app.get("/api/docs/search")
async def search_docs_endpoint(
    q: str = Query(..., description="Search query"),
    k: int = Query(10, ge=1, le=50, description="Number of results"),
    tier0_only: bool = Query(True, description="Restrict to Tier-0 docs"),
    doc_type: str | None = Query(
        None, description="Filter by document type (ssot, runbook, reference, legacy, unknown)"
    ),
) -> JSONResponse:
    """
    Search governance/docs content via semantic similarity.

    Backed by agentpm.docs.search.search_docs / existing Phase-8C pipeline.
    """
    from agentpm.docs.search import search_docs

    result = search_docs(query=q, k=k, tier0_only=tier0_only, doc_type=doc_type)

    if not result.get("ok", False):
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "query": result.get("query", q),
                "error": result.get("error", "Search failed"),
                "results": [],
            },
        )

    raw_results = result.get("results", [])
    transformed_results = []
    for idx, r in enumerate(raw_results, start=1):
        logical_name = r.get("logical_name", "")
        # Simple logical_name split: PREFIX::path
        if "::" in logical_name:
            _prefix, path = logical_name.split("::", 1)
        else:
            path = logical_name

        title = r.get("title") or logical_name or "Untitled"
        snippet = r.get("content") or r.get("snippet") or ""
        meta = r.get("meta") or {}

        transformed_results.append(
            {
                "rank": idx,
                "score": r.get("score"),
                "source_id": logical_name,
                "title": title,
                "snippet": snippet,
                "section": {
                    "heading": meta.get("heading"),
                    "anchor": meta.get("anchor"),
                },
                "provenance": {
                    "doc_path": path,
                    "fragment_id": meta.get("fragment_id"),
                    "content_hash": meta.get("content_hash"),
                },
            }
        )

    payload = {
        "ok": True,
        "query": result.get("query", q),
        "k": result.get("k", k),
        "tier0_only": result.get("tier0_only", tier0_only),
        "results": transformed_results,
        "model_name": result.get("model_name"),
    }
    return JSONResponse(content=payload)


@app.get("/governance-search", response_class=HTMLResponse)
async def governance_search_page() -> HTMLResponse:
    """
    HTML page for governance docs search (Phase-8D).

    Simple two-column layout:
    - Left: search form + result list
    - Right: selected result details
    """
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Governance Docs Search</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen bg-slate-950 text-slate-50">
  <div class="mx-auto max-w-6xl p-4 space-y-4">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold">Governance Search</h1>
        <p class="text-sm text-slate-400">
          Search Tier-0 governance docs via semantic similarity.
        </p>
      </div>
      <a href="/docs/atlas/index.html" class="text-sm text-blue-400 hover:underline">
        ← Back to Atlas
      </a>
    </header>

    <section class="grid gap-4 md:grid-cols-2">
      <!-- Left: search form + results -->
      <div class="space-y-3">
        <form id="search-form" class="space-y-2 rounded-xl border border-slate-800 bg-slate-900/60 p-3">
          <label class="block text-xs font-semibold uppercase tracking-wide text-slate-400">
            Query
          </label>
          <input
            id="q"
            name="q"
            type="text"
            required
            placeholder="How does the system enforce correctness across Tier-0 docs?"
            class="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-blue-500"
          />
          <div class="flex flex-wrap items-center gap-3 text-xs text-slate-300">
            <label class="flex items-center gap-1">
              <span>k</span>
              <input
                id="k"
                name="k"
                type="number"
                min="1"
                max="50"
                value="10"
                class="w-16 rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-xs outline-none focus:border-blue-500"
              />
            </label>
            <label class="flex items-center gap-1">
              <span class="text-slate-400">Type:</span>
              <select
                id="doc_type"
                name="doc_type"
                class="rounded-md border border-slate-700 bg-slate-950 px-2 py-1 text-xs outline-none focus:border-blue-500"
              >
                <option value="">All types</option>
                <option value="ssot">SSOT</option>
                <option value="runbook">Runbook</option>
                <option value="reference">Reference</option>
                <option value="legacy">Legacy</option>
                <option value="unknown">Unknown</option>
              </select>
            </label>
            <label class="inline-flex items-center gap-2">
              <input
                id="tier0_only"
                name="tier0_only"
                type="checkbox"
                checked
                class="h-3 w-3 rounded border-slate-600 bg-slate-950 text-blue-500"
              />
              <span>Tier-0 only</span>
            </label>
            <button
              type="submit"
              class="ml-auto rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold hover:bg-blue-500"
            >
              Search
            </button>
          </div>
          <p id="status" class="text-xs text-slate-400"></p>
        </form>

        <div
          id="results"
          class="space-y-2 rounded-xl border border-slate-800 bg-slate-900/40 p-2 text-sm"
        >
          <p class="text-xs text-slate-400">
            Enter a query and press <span class="font-semibold">Search</span> to see results.
          </p>
        </div>
      </div>

      <!-- Right: selected result details -->
      <div
        id="detail"
        class="min-h-[200px] rounded-xl border border-slate-800 bg-slate-900/40 p-3 text-sm"
      >
        <p class="text-xs text-slate-400">
          Select a result to view the matching section here.
        </p>
      </div>
    </section>
  </div>

  <script>
    const form = document.getElementById("search-form");
    const statusEl = document.getElementById("status");
    const resultsEl = document.getElementById("results");
    const detailEl = document.getElementById("detail");

    function renderResults(data) {
      resultsEl.innerHTML = "";
      if (!data.ok) {
        const p = document.createElement("p");
        p.className = "text-xs text-red-400";
        p.textContent = data.error || "Search failed.";
        resultsEl.appendChild(p);
        return;
      }
      if (!data.results || data.results.length === 0) {
        const p = document.createElement("p");
        p.className = "text-xs text-slate-400";
        p.textContent = "No results found.";
        resultsEl.appendChild(p);
        return;
      }
      data.results.forEach((r) => {
        const card = document.createElement("button");
        card.type = "button";
        card.className =
          "w-full rounded-lg border border-slate-800 bg-slate-900/70 p-2 text-left text-xs hover:border-blue-500";
        card.innerHTML = `
          <div class="flex items-center justify-between gap-2">
            <div class="truncate text-[11px] font-semibold">
              <span class="text-slate-400">#${r.rank}</span>
              <span class="ml-1">${r.title || r.source_id || "Untitled"}</span>
            </div>
            <span class="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] text-slate-300">
              score: ${typeof r.score === "number" ? r.score.toFixed(3) : "n/a"}
            </span>
          </div>
          <p class="mt-1 line-clamp-3 text-[11px] text-slate-300">${r.snippet || ""}</p>
          <p class="mt-1 text-[10px] text-slate-500">${r.source_id || ""}</p>
        `;
        card.addEventListener("click", () => {
          detailEl.innerHTML = `
            <div class="space-y-2 text-xs">
              <div class="flex items-center justify-between gap-2">
                <div>
                  <h2 class="text-sm font-semibold">${r.title || "Untitled"}</h2>
                  <p class="text-[11px] text-slate-400">${r.source_id || ""}</p>
                </div>
                <span class="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] text-slate-300">
                  score: ${typeof r.score === "number" ? r.score.toFixed(3) : "n/a"}
                </span>
              </div>
              <pre class="whitespace-pre-wrap rounded-lg bg-slate-950/70 p-2 text-[11px] text-slate-200">${r.snippet || ""}</pre>
            </div>
          `;
        });
        resultsEl.appendChild(card);
      });
    }

    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const q = document.getElementById("q").value.trim();
      const k = document.getElementById("k").value || "10";
      const tier0Only = document.getElementById("tier0_only").checked ? "true" : "false";
      const docType = document.getElementById("doc_type").value;
      if (!q) {
        statusEl.textContent = "Please enter a query.";
        return;
      }
      statusEl.textContent = "Searching...";
      try {
        let url = `/api/docs/search?q=${encodeURIComponent(q)}&k=${encodeURIComponent(k)}&tier0_only=${tier0Only}`;
        if (docType) {
          url += `&doc_type=${encodeURIComponent(docType)}`;
        }
        const res = await fetch(url);
        const data = await res.json();
        statusEl.textContent = data.ok
          ? `Found ${data.results.length} result(s).`
          : "Search failed.";
        renderResults(data);
      } catch (err) {
        console.error(err);
        statusEl.textContent = "Search failed (network or server error).";
      }
    });
  </script>
</body>
</html>"""
    return HTMLResponse(content=html)


# --- Doc Control Panel API endpoints (DM-002) ---


@app.get("/api/docs/control/canonical")
async def get_canonical_docs() -> JSONResponse:
    """
    Get canonical documents list from DM-002 export.

    Returns:
        JSON with canonical documents from share/exports/docs-control/canonical.json
    """
    canonical_path = Path("share/exports/docs-control/canonical.json")
    data = load_json_file(canonical_path)

    if not data:
        return JSONResponse(
            status_code=404,
            content={
                "ok": False,
                "error": "Canonical documents export not found. Run 'pmagent docs dashboard-refresh' to generate.",
                "items": [],
                "total": 0,
            },
        )

    return JSONResponse(
        content={
            "ok": True,
            "items": data.get("items", []),
            "total": data.get("total", 0),
            "generated_at": data.get("generated_at"),
        }
    )


@app.get("/api/docs/control/archive-candidates")
async def get_archive_candidates() -> JSONResponse:
    """
    Get archive candidates grouped by directory from DM-002 export.

    Returns:
        JSON with archive candidates from share/exports/docs-control/archive-candidates.json
    """
    candidates_path = Path("share/exports/docs-control/archive-candidates.json")
    data = load_json_file(candidates_path)

    if not data:
        return JSONResponse(
            status_code=404,
            content={
                "ok": False,
                "error": "Archive candidates export not found. Run 'pmagent docs dashboard-refresh' to generate.",
                "groups": [],
                "total_groups": 0,
                "total_items": 0,
            },
        )

    return JSONResponse(
        content={
            "ok": True,
            "groups": data.get("groups", []),
            "total_groups": data.get("total_groups", 0),
            "total_items": data.get("total_items", 0),
            "generated_at": data.get("generated_at"),
        }
    )


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
