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
from agentpm.status.explain import explain_system_status
from agentpm.status.system import get_system_status

# Import LM indicator adapter
from agentpm.lm_widgets.adapter import INDICATOR_PATH
from datetime import UTC

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

# Mount static files from share directory (PLAN-081: orchestrator dashboard)
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
        JSON with db and lm health status:
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
            }
        }
    """
    try:
        status = get_system_status()
        return JSONResponse(content=status)
    except Exception as e:
        LOG.error(f"Error getting system status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while fetching system status: {e!s}",
        ) from e


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
        explanation = explain_system_status(use_lm=True)
        return JSONResponse(content=explanation)
    except Exception as e:
        LOG.error(f"Error getting status explanation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to compute status explanation",
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
            }
        }
        Or empty snapshot if file is missing/invalid.
    """
    import json as json_lib
    from pathlib import Path

    try:
        # Use absolute path from adapter
        indicator_path = Path(INDICATOR_PATH)
        if not indicator_path.is_absolute():
            # Resolve relative to repo root
            repo_root = Path(__file__).resolve().parents[2]
            indicator_path = repo_root / indicator_path

        if not indicator_path.exists():
            # Return empty snapshot with note
            return JSONResponse(
                content={
                    "snapshot": None,
                    "note": "LM indicator data not available; run the LM indicator export pipeline to populate this chart.",
                }
            )

        # Read and parse JSON
        try:
            indicator_data = json_lib.loads(indicator_path.read_text(encoding="utf-8"))
        except (json_lib.JSONDecodeError, OSError) as e:
            LOG.error(f"Error reading LM indicator JSON: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to parse LM indicator data",
            ) from e

        return JSONResponse(
            content={
                "snapshot": indicator_data,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        LOG.error(f"Error getting LM indicator: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to load LM indicator data",
        ) from e


def _load_json_or_hint(path: Path) -> tuple[bool, dict | None, str | None]:
    """Load JSON file with hermetic error handling.

    Returns:
        Tuple of (ok, data, error_message)
        - ok: True if file exists and is valid JSON
        - data: Parsed JSON dict, or None if error
        - error_message: Error description, or None if ok
    """
    try:
        if not path.exists():
            return (False, None, f"File not found: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return (True, data, None)
        except json.JSONDecodeError as e:
            return (False, None, f"Invalid JSON: {e}")
        except OSError as e:
            return (False, None, f"Read error: {e}")
    except Exception as e:
        return (False, None, f"Unexpected error: {e}")


@app.get("/api/compliance/head")
async def get_compliance_head_endpoint() -> JSONResponse:
    """Get compliance head snapshot for orchestrator dashboard.

    Returns:
        JSON with compliance data:
        {
            "ok": bool,
            "snapshot": {
                "generated_at": str,
                "latest_agent_run": str | null,
                "windows": {...},
                ...
            } | null,
            "error": str | null
        }
    """
    share_dir = Path("share")
    compliance_file = share_dir / "atlas" / "control_plane" / "compliance.head.json"

    ok, data, error_msg = _load_json_or_hint(compliance_file)

    if ok:
        return JSONResponse(
            content={
                "ok": True,
                "snapshot": data,
            }
        )
    else:
        return JSONResponse(
            content={
                "ok": False,
                "snapshot": None,
                "error": error_msg,
            }
        )


@app.get("/api/kb/docs_head")
async def get_kb_docs_head_endpoint() -> JSONResponse:
    """Get KB docs head snapshot for orchestrator dashboard.

    Returns:
        JSON with KB docs data:
        {
            "ok": bool,
            "snapshot": {
                "generated_at": str,
                "docs": [...],
                "schema": str,
                "ok": bool,
                "db_off": bool,
                ...
            } | null,
            "error": str | null
        }
    """
    share_dir = Path("share")
    kb_docs_file = share_dir / "atlas" / "control_plane" / "kb_docs.head.json"

    ok, data, error_msg = _load_json_or_hint(kb_docs_file)

    if ok:
        return JSONResponse(
            content={
                "ok": True,
                "snapshot": data,
            }
        )
    else:
        return JSONResponse(
            content={
                "ok": False,
                "snapshot": None,
                "error": error_msg,
            }
        )


@app.get("/api/mcp/catalog_summary")
async def get_mcp_catalog_summary() -> JSONResponse:
    """Get MCP catalog summary for orchestrator dashboard.

    Returns:
        JSON with MCP catalog summary:
        {
            "ok": bool,
            "endpoint_count": int | null,
            "last_updated": str | null,
            "error": str | null
        }
    """
    share_dir = Path("share")
    docs_dir = Path("docs")
    candidates = [
        share_dir / "atlas" / "control_plane" / "mcp_catalog.json",
        docs_dir / "atlas" / "data" / "mcp_catalog.json",
    ]

    last_error = None
    for candidate in candidates:
        ok, data, error = _load_json_or_hint(candidate)
        if not ok:
            last_error = error
            continue

        # Extract endpoint count from various possible keys
        endpoints = data.get("endpoints") or data.get("tools") or []
        if isinstance(endpoints, list):
            count = len(endpoints)
        elif isinstance(endpoints, dict):
            count = len(endpoints)
        else:
            count = 0

        last_updated = data.get("generated_at") or data.get("updated_at") or data.get("last_updated")

        return JSONResponse(
            content={
                "ok": True,
                "endpoint_count": count,
                "last_updated": last_updated,
                "error": None,
            }
        )

    # If we get here, no usable file found
    return JSONResponse(
        content={
            "ok": False,
            "endpoint_count": None,
            "last_updated": None,
            "error": last_error or "MCP catalog summary unavailable",
        }
    )


@app.get("/api/atlas/browser_verification")
async def get_browser_verification_status() -> JSONResponse:
    """Get browser verification status for orchestrator dashboard.

    Returns:
        JSON with browser verification status:
        {
            "ok": bool,
            "status": "verified" | "partial" | "missing",
            "verified_pages": int | null,
            "error": str | null
        }
    """
    evidence_dir = Path("evidence")
    candidates = [
        evidence_dir / "guard_browser_verification.json",
        evidence_dir / "browser_screenshot_integrated.json",
    ]

    last_error = None
    for path in candidates:
        ok, data, error = _load_json_or_hint(path)
        if not ok:
            last_error = error
            continue

        # Derive status from evidence content
        status = data.get("status") or data.get("verdict")
        if status not in ("verified", "partial", "missing"):
            # Default to verified if file exists and no explicit status
            status = "verified" if ok else "missing"

        verified_pages = data.get("verified_pages") or data.get("page_count") or data.get("pages_verified")

        return JSONResponse(
            content={
                "ok": True,
                "status": status,
                "verified_pages": verified_pages,
                "error": None,
            }
        )

    # If we get here, no usable file found
    return JSONResponse(
        content={
            "ok": False,
            "status": "missing",
            "verified_pages": None,
            "error": last_error or "No browser verification evidence found",
        }
    )


@app.get("/api/graph/stats_summary")
async def get_graph_stats_summary() -> JSONResponse:
    """Get graph stats summary for orchestrator dashboard.

    Returns:
        JSON with graph stats summary:
        {
            "ok": bool,
            "nodes": int | null,
            "edges": int | null,
            "clusters": int | null,
            "density": float | null,
            "error": str | null
        }
    """
    share_dir = Path("share")
    export_dir = Path(os.getenv("EXPORT_DIR", "exports"))
    candidates = [
        share_dir / "exports" / "graph_stats.json",
        export_dir / "graph_stats.json",
    ]

    last_error: str | None = None
    for path in candidates:
        ok, data, error = _load_json_or_hint(path)
        if not ok or data is None:
            last_error = error
            continue

        # Extract stats from various possible structures
        # Support both top-level fields and nested totals structure
        totals = data.get("totals") or {}
        nodes = data.get("nodes") or totals.get("nodes")
        edges = data.get("edges") or totals.get("edges")
        clusters = data.get("clusters") or data.get("total_clusters")
        density = data.get("density") or data.get("avg_density")

        return JSONResponse(
            content={
                "ok": True,
                "nodes": nodes,
                "edges": edges,
                "clusters": clusters,
                "density": density,
                "error": None,
            }
        )

    # If we get here, no usable file found
    return JSONResponse(
        content={
            "ok": False,
            "nodes": None,
            "edges": None,
            "clusters": None,
            "density": None,
            "error": last_error or "Graph stats export not available",
        }
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
            <div class="bg-white rounded-lg shadow p-6">
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
            } catch (error) {
                // Hide explanation content, show error message
                document.getElementById('explanation-content').classList.add('hidden');
                document.getElementById('explanation-error').classList.remove('hidden');
            }
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
    """HTML page showing LM indicator insights with chart."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LM Insights - Gemantria</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-2">LM Insights</h1>
        <p class="text-gray-600 mb-6">Recent local LM health and usage snapshots.</p>
        
        <div id="loading" class="text-gray-600">Loading LM indicator data...</div>
        
        <div id="no-data" class="hidden bg-yellow-50 border border-yellow-200 rounded-lg shadow p-6 mb-6">
            <p class="text-yellow-800">
                No LM indicator snapshots available yet; run the LM indicator export pipeline to populate this chart.
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
            
            <!-- Metrics Chart -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h2 class="text-xl font-semibold mb-4">Success & Error Rates</h2>
                <canvas id="lmIndicatorChart" class="max-h-96"></canvas>
            </div>
            
            <!-- Metrics Summary -->
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Metrics Summary</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="p-4 bg-blue-50 rounded">
                        <div class="text-sm text-gray-600">Total Calls</div>
                        <div id="total-calls" class="text-2xl font-bold text-blue-700"></div>
                    </div>
                    <div class="p-4 bg-green-50 rounded">
                        <div class="text-sm text-gray-600">Success Rate</div>
                        <div id="success-rate" class="text-2xl font-bold text-green-700"></div>
                    </div>
                    <div class="p-4 bg-red-50 rounded">
                        <div class="text-sm text-gray-600">Error Rate</div>
                        <div id="error-rate" class="text-2xl font-bold text-red-700"></div>
                    </div>
                </div>
                <div class="mt-4 text-sm text-gray-500">
                    <div>Window: <span id="window-days"></span> days</div>
                    <div>Generated: <span id="generated-at"></span></div>
                </div>
            </div>
        </div>
        
        <div id="error" class="hidden text-red-600 mt-4"></div>
    </div>
    
    <script>
        let chart = null;
        
        async function loadLMIndicator() {
            try {
                const response = await fetch('/api/lm/indicator');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                
                // Hide loading
                document.getElementById('loading').classList.add('hidden');
                
                if (!data.snapshot) {
                    // Show no-data message
                    document.getElementById('no-data').classList.remove('hidden');
                    return;
                }
                
                // Show content
                document.getElementById('insights-content').classList.remove('hidden');
                
                const snapshot = data.snapshot;
                
                // Update status indicator
                const statusBadge = document.getElementById('status-badge');
                const statusText = document.getElementById('status-text');
                const statusDetails = document.getElementById('status-details');
                
                let statusColor = 'bg-gray-500';
                let statusLabel = 'Unknown';
                
                if (snapshot.status === 'healthy') {
                    statusColor = 'bg-green-500';
                    statusLabel = 'Healthy';
                } else if (snapshot.status === 'degraded') {
                    statusColor = 'bg-yellow-500';
                    statusLabel = 'Degraded';
                } else if (snapshot.status === 'offline') {
                    statusColor = 'bg-red-500';
                    statusLabel = 'Offline';
                }
                
                statusBadge.className = `${statusColor} px-4 py-2 rounded-full text-white font-semibold`;
                statusBadge.textContent = statusLabel;
                statusText.textContent = `Status: ${snapshot.status} (${snapshot.reason})`;
                
                let detailsText = `Success rate: ${(snapshot.success_rate * 100).toFixed(1)}%, `;
                detailsText += `Error rate: ${(snapshot.error_rate * 100).toFixed(1)}%`;
                if (snapshot.top_error_reason) {
                    detailsText += `, Top error: ${snapshot.top_error_reason}`;
                }
                if (snapshot.db_off) {
                    detailsText += ' (Database offline)';
                }
                statusDetails.textContent = detailsText;
                
                // Update metrics
                document.getElementById('total-calls').textContent = snapshot.total_calls.toLocaleString();
                document.getElementById('success-rate').textContent = `${(snapshot.success_rate * 100).toFixed(1)}%`;
                document.getElementById('error-rate').textContent = `${(snapshot.error_rate * 100).toFixed(1)}%`;
                document.getElementById('window-days').textContent = snapshot.window_days;
                document.getElementById('generated-at').textContent = new Date(snapshot.generated_at).toLocaleString();
                
                // Create/update chart
                const ctx = document.getElementById('lmIndicatorChart').getContext('2d');
                
                if (chart) {
                    chart.destroy();
                }
                
                chart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['Success Rate', 'Error Rate'],
                        datasets: [{
                            label: 'Rate',
                            data: [
                                snapshot.success_rate * 100,
                                snapshot.error_rate * 100
                            ],
                            backgroundColor: [
                                'rgba(34, 197, 94, 0.8)',
                                'rgba(239, 68, 68, 0.8)'
                            ],
                            borderColor: [
                                'rgba(34, 197, 94, 1)',
                                'rgba(239, 68, 68, 1)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                ticks: {
                                    callback: function(value) {
                                        return value + '%';
                                    }
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return context.parsed.y.toFixed(2) + '%';
                                    }
                                }
                            }
                        }
                    }
                });
                
            } catch (error) {
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('error').classList.remove('hidden');
                document.getElementById('error').textContent = `Error loading LM indicator: ${error.message}`;
            }
        }
        
        // Load on page load
        loadLMIndicator();
        
        // Auto-refresh every 30 seconds
        setInterval(loadLMIndicator, 30000);
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
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                
                <!-- LM Insights Card -->
                <div id="lm-insights-card" class="bg-white rounded-lg shadow p-6 border border-gray-200">
                    <h2 class="text-xl font-semibold mb-4">LM Insights</h2>
                    
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
        }
        
        async function loadSystemHealth() {
            try {
                // Fetch system status
                const statusResponse = await fetch('/api/status/system');
                if (!statusResponse.ok) {
                    throw new Error(`HTTP ${statusResponse.status}: ${statusResponse.statusText}`);
                }
                const statusData = await statusResponse.json();
                
                // Fetch explanation
                let explanationData = null;
                try {
                    const explainResponse = await fetch('/api/status/explain');
                    if (explainResponse.ok) {
                        explanationData = await explainResponse.json();
                    }
                } catch (e) {
                    // Explanation is optional, continue without it
                }
                
                // Hide loading, show content
                document.getElementById('system-health-loading').classList.add('hidden');
                document.getElementById('system-health-error').classList.add('hidden');
                document.getElementById('system-health-content').classList.remove('hidden');
                
                // Update status badge
                const level = explanationData?.level || 'OK';
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
                const db = statusData.db;
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
                const lm = statusData.lm;
                const lmSummary = document.getElementById('lm-summary');
                const okSlots = lm.slots.filter(s => s.service === 'OK').length;
                const totalSlots = lm.slots.length;
                lmSummary.textContent = `LM: ${okSlots}/${totalSlots} slots OK`;
                
            } catch (error) {
                document.getElementById('system-health-loading').classList.add('hidden');
                document.getElementById('system-health-content').classList.add('hidden');
                document.getElementById('system-health-error').classList.remove('hidden');
            }
        }
        
        async function loadLMInsights() {
            try {
                const response = await fetch('/api/lm/indicator');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                
                // Hide loading, show content
                document.getElementById('lm-insights-loading').classList.add('hidden');
                document.getElementById('lm-insights-error').classList.add('hidden');
                
                if (!data.snapshot) {
                    // Show error if no snapshot
                    document.getElementById('lm-insights-error').classList.remove('hidden');
                    return;
                }
                
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
                document.getElementById('lm-insights-loading').classList.add('hidden');
                document.getElementById('lm-insights-content').classList.add('hidden');
                document.getElementById('lm-insights-error').classList.remove('hidden');
            }
        }
        
        // Load dashboard on page load
        loadDashboard();
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            loadSystemHealth();
            loadLMInsights();
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
            ]
        }
        Or empty snapshots list if file is missing/invalid.
    """
    import json as json_lib
    from pathlib import Path
    from datetime import datetime

    try:
        # Path to DB health JSON (same location as pm_snapshot writes it)
        repo_root = Path(__file__).resolve().parents[2]
        db_health_path = repo_root / "evidence" / "pm_snapshot" / "db_health.json"

        if not db_health_path.exists():
            # Return empty snapshots with note
            return JSONResponse(
                content={
                    "snapshots": [],
                    "note": "DB health data not available; run `make pm.snapshot` to populate this chart.",
                }
            )

        # Read and parse JSON
        try:
            db_health_data = json_lib.loads(db_health_path.read_text(encoding="utf-8"))
        except (json_lib.JSONDecodeError, OSError) as e:
            LOG.error(f"Error reading DB health JSON: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to parse DB health data",
            ) from e

        # Transform to timeline shape
        mode = db_health_data.get("mode", "db_off")
        ok = db_health_data.get("ok", False)
        errors = db_health_data.get("details", {}).get("errors", [])

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
        generated_at = db_health_data.get("generated_at")
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

    except HTTPException:
        raise
    except Exception as e:
        LOG.error(f"Error getting DB health timeline: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to load DB health timeline data",
        ) from e


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
        <p class="text-gray-600 mb-6">Recent database health snapshots from smokes/exports.</p>
        
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
    use_lm: bool = Query(True, description="Use AI commentary (default: True)"),
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


# --- Phase-8D: Governance docs search API + UI ---


@app.get("/api/docs/search")
async def search_docs_endpoint(
    q: str = Query(..., description="Search query"),
    k: int = Query(10, ge=1, le=50, description="Number of results"),
    tier0_only: bool = Query(True, description="Restrict to Tier-0 docs"),
) -> JSONResponse:
    """
    Search governance/docs content via semantic similarity.

    Backed by agentpm.docs.search.search_docs / existing Phase-8C pipeline.
    """
    from agentpm.docs.search import search_docs

    result = search_docs(query=q, k=k, tier0_only=tier0_only)

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
          <div class="flex items-center gap-3 text-xs text-slate-300">
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
      if (!q) {
        statusEl.textContent = "Please enter a query.";
        return;
      }
      statusEl.textContent = "Searching...";
      try {
        const url = `/api/docs/search?q=${encodeURIComponent(q)}&k=${encodeURIComponent(k)}&tier0_only=${tier0Only}`;
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
