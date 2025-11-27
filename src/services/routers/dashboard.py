"""
Dashboard API Router.

Provides endpoints for the dashboard tiles to test connections, refresh data,
and get status updates.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.infra.structured_logger import get_logger

# Initialize logger
LOG = get_logger("dashboard_api")

router = APIRouter(prefix="/api", tags=["dashboard"])


class InferenceTestResponse(BaseModel):
    ollama: dict[str, Any]
    lmstudio: dict[str, Any]


class RefreshResponse(BaseModel):
    success: bool
    message: str


@router.post("/inference/test", response_model=InferenceTestResponse)
async def test_inference_connections():
    """Test connections to inference providers (Ollama, LM Studio)."""

    # Test Ollama
    ollama_status = {"available": False, "error": None, "details": None}
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{ollama_url}/api/tags")
            if resp.status_code == 200:
                ollama_status["available"] = True
                ollama_status["details"] = f"Connected to {ollama_url}"
                data = resp.json()
                models = [m.get("name") for m in data.get("models", [])]
                ollama_status["models"] = models[:5]  # Show first 5
            else:
                ollama_status["error"] = f"HTTP {resp.status_code}"
    except Exception as e:
        ollama_status["error"] = str(e)

    # Test LM Studio
    lmstudio_status = {"available": False, "error": None, "details": None}
    # Try common ports
    lmstudio_ports = [1234, 9994]

    # Check env var first
    env_base_url = os.getenv("LM_STUDIO_BASE_URL")
    if env_base_url:
        # Extract port/host if possible, or just use it
        target_urls = [env_base_url]
    else:
        target_urls = [f"http://localhost:{p}/v1" for p in lmstudio_ports]

    for url in target_urls:
        try:
            # Clean url
            if url.endswith("/v1"):
                base = url
            else:
                base = f"{url.rstrip('/')}/v1"

            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{base}/models")
                if resp.status_code == 200:
                    lmstudio_status["available"] = True
                    lmstudio_status["details"] = f"Connected to {base}"
                    lmstudio_status["error"] = None  # Clear any previous errors
                    data = resp.json()
                    models = [m.get("id") for m in data.get("data", [])]
                    lmstudio_status["models"] = models[:5]
                    break  # Found one
                else:
                    lmstudio_status["error"] = f"HTTP {resp.status_code} at {base}"
        except Exception as e:
            lmstudio_status["error"] = str(e)

    return InferenceTestResponse(ollama=ollama_status, lmstudio=lmstudio_status)


@router.post("/docs/refresh", response_model=RefreshResponse)
async def refresh_docs_dashboard():
    """Trigger a refresh of the docs dashboard exports."""
    try:
        # Run the pmagent command
        # We use the python script directly to avoid path issues with the CLI alias
        script_path = Path("agentpm/scripts/docs_dashboard_refresh.py").resolve()

        if not script_path.exists():
            raise FileNotFoundError(f"Script not found at {script_path}")

        # Add current directory to PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()

        result = subprocess.run(["python3", str(script_path)], capture_output=True, text=True, timeout=30, env=env)

        if result.returncode == 0:
            return RefreshResponse(success=True, message="Docs dashboard refreshed successfully")
        else:
            LOG.error(f"Docs refresh failed: {result.stderr}")
            return RefreshResponse(success=False, message=f"Refresh failed: {result.stderr}")

    except Exception as e:
        LOG.error(f"Docs refresh error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/docs/summary")
async def get_docs_summary():
    """Get the docs dashboard summary."""
    try:
        export_dir = Path("share/exports/docs-control").resolve()
        summary_file = export_dir / "summary.json"

        if not summary_file.exists():
            return {"error": "Summary not found. Please run refresh."}

        with open(summary_file) as f:
            return json.load(f)

    except Exception as e:
        LOG.error(f"Error reading docs summary: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/mcp/status")
async def get_mcp_status():
    """Get status of MCP servers."""
    # Try to read bundle proof first
    ROOT = Path(__file__).resolve().parents[3]
    bundle_proof_path = ROOT / "share" / "mcp" / "bundle_proof.json"

    if bundle_proof_path.exists():
        try:
            with open(bundle_proof_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            LOG.warning(f"Failed to read MCP bundle proof: {e}")

    # Fallback: try status cards
    status_cards_path = ROOT / "share" / "atlas" / "control_plane" / "mcp_status_cards.json"
    if status_cards_path.exists():
        try:
            with open(status_cards_path, encoding="utf-8") as f:
                cards_data = json.load(f)
            # Transform to match expected format
            return {
                "schema": "mcp_bundle_proof",
                "generated_at": cards_data.get("generated_at"),
                "all_ok": cards_data.get("ok", False),
                "proofs_count": cards_data.get("summary", {}).get("total_cards", 0),
                "proofs": {k: {"ok": v.get("ok", False)} for k, v in cards_data.get("cards", {}).items()},
            }
        except Exception as e:
            LOG.warning(f"Failed to read MCP status cards: {e}")

    # Placeholder if no files exist
    return {
        "status": "unknown",
        "servers": [],
        "message": "MCP integration pending",
        "all_ok": False,
        "proofs": {},
    }


@router.post("/mcp/test", response_model=RefreshResponse)
async def test_mcp_bundle():
    """Test MCP bundle proof generation."""
    ROOT = Path(__file__).resolve().parents[3]
    try:
        result = subprocess.run(
            ["make", "mcp.proof.e25.bundle"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=ROOT,
        )

        if result.returncode == 0:
            return RefreshResponse(success=True, message="MCP bundle proof generated successfully")
        else:
            LOG.error(f"MCP test failed: {result.stderr}")
            return RefreshResponse(success=False, message=f"MCP test failed: {result.stderr or result.stdout}")
    except subprocess.TimeoutExpired:
        return RefreshResponse(success=False, message="MCP test timed out")
    except Exception as e:
        LOG.error(f"Error testing MCP: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/mcp/refresh", response_model=RefreshResponse)
async def refresh_mcp_status():
    """Trigger MCP proof generation refresh."""
    # Same as test endpoint
    return await test_mcp_bundle()
