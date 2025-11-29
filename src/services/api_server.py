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

# Load environment variables
ensure_env_loaded()

# Initialize logger
LOG = get_logger("api_server")

# Cache for system status endpoint (Phase 4: Status Polling Performance)
# TTL: 5 minutes (300 seconds) to reduce expensive DB/LM coherence checks
_STATUS_CACHE_TTL = int(os.getenv("STATUS_CACHE_TTL", "300"))  # 5 minutes default
_status_cache: dict[str, tuple[dict[str, Any], float]] = {}  # {endpoint: (data, timestamp)}

# Metrics for status endpoint (Phase 4: Status Polling Performance)
_status_metrics = {
    "total_calls": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "total_latency_ms": 0.0,
    "last_call_time": None,
}


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

    Phase 4: Status Polling Performance Optimization
    - Caches results with TTL (default: 5 minutes) to reduce expensive DB/LM coherence checks
    - Expensive operations (DB health, LM status, AI tracking, share manifest) are cached
    - Cache TTL configurable via STATUS_CACHE_TTL env var (seconds)

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
    endpoint = "/api/status/system"
    current_time = time.time()
    request_start = time.time()

    # Update metrics
    _status_metrics["total_calls"] += 1
    _status_metrics["last_call_time"] = current_time

    # Check cache
    if endpoint in _status_cache:
        cached_data, cached_time = _status_cache[endpoint]
        age = current_time - cached_time
        if age < _STATUS_CACHE_TTL:
            _status_metrics["cache_hits"] += 1
            latency_ms = (time.time() - request_start) * 1000
            _status_metrics["total_latency_ms"] += latency_ms
            LOG.debug(f"Status cache hit (age: {age:.1f}s, TTL: {_STATUS_CACHE_TTL}s, latency: {latency_ms:.1f}ms)")
            return JSONResponse(content=cached_data)

    # Cache miss or expired - fetch fresh data
    _status_metrics["cache_misses"] += 1
    LOG.debug("Status cache miss - fetching fresh data")
    fetch_start = time.time()

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

        # Update cache
        _status_cache[endpoint] = (response, current_time)

        fetch_duration = time.time() - fetch_start
        total_latency_ms = (time.time() - request_start) * 1000
        _status_metrics["total_latency_ms"] += total_latency_ms

        # Log metrics periodically (every 10 calls)
        if _status_metrics["total_calls"] % 10 == 0:
            avg_latency_ms = _status_metrics["total_latency_ms"] / _status_metrics["total_calls"]
            cache_hit_rate = (
                _status_metrics["cache_hits"] / (_status_metrics["cache_hits"] + _status_metrics["cache_misses"]) * 100
                if (_status_metrics["cache_hits"] + _status_metrics["cache_misses"]) > 0
                else 0
            )
            LOG.info(
                f"Status endpoint metrics: calls={_status_metrics['total_calls']}, "
                f"cache_hit_rate={cache_hit_rate:.1f}%, avg_latency={avg_latency_ms:.1f}ms"
            )

        LOG.info(
            f"Status endpoint: fetched in {fetch_duration:.2f}s, cached for {_STATUS_CACHE_TTL}s, "
            f"total_latency={total_latency_ms:.1f}ms"
        )

        return JSONResponse(content=response)
    except Exception as e:
        LOG.error(f"Error getting system status: {e}")
        # Fallback to original implementation if snapshot helper fails
        try:
            status = get_system_status()
            # Cache fallback response too (shorter TTL for errors)
            _status_cache[endpoint] = (status, current_time)
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
        <p class="text-gray-600 mb-2 text-sm">Recent LM activity analytics (advisory only; not used for health gates)</p>
        <p class="text-gray-500 mb-6 text-xs italic">Note: System health status is determined by the unified snapshot API, not by these analytics.</p>
        
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
                
                <!-- LM Insights Card -->
                <div id="lm-insights-card" class="bg-white rounded-lg shadow p-6 border border-gray-200">
                    <h2 class="text-xl font-semibold mb-1">LM Insights</h2>
                    <p class="text-xs text-gray-500 mb-4 italic">Recent LM activity analytics (advisory only)</p>
                    
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
                    const lmOk = (lm.slots || []).some((s: any) => s.service === 'OK');
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
                const okSlots = slots.filter((s: any) => s.service === 'OK').length;
                const totalSlots = slots.length;
                if (totalSlots === 0) {
                    lmSummary.textContent = 'LM: No slots configured';
                } else {
                    lmSummary.textContent = `LM: ${okSlots}/${totalSlots} slots OK`;
                }
                
                // Update KB Doc Metrics (AgentPM-Next:M4)
                if (statusData.kb_doc_health) {
                    loadDocMetrics(statusData.kb_doc_health);
                }
                
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
