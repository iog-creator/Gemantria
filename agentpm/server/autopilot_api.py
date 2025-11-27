"""
Autopilot Backend API (Phase C).

This module implements the API contract for the Orchestrator Shell's Autopilot.
Phase C: Executes guarded pmagent commands when dry_run is False.
"""

import logging
import subprocess
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agentpm.guarded.autopilot_adapter import map_intent_to_command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("autopilot")

router = APIRouter(prefix="/api/autopilot", tags=["autopilot"])


class IntentRequest(BaseModel):
    intent_text: str
    context: dict[str, Any] | None = None


class IntentResponse(BaseModel):
    accepted: bool
    plan_id: str
    summary: str
    status: str


@router.post("/intent", response_model=IntentResponse)
async def handle_intent(request: IntentRequest):
    """
    Handle an autopilot intent.

    Phase C: If context.dry_run is False, maps intent to command and executes it.
    Otherwise, returns a "planned" status without executing actions.
    """
    plan_id = f"autopilot-plan-{uuid.uuid4().hex[:8]}"

    logger.info(f"Received intent: {request.intent_text} (plan_id={plan_id})")
    if request.context:
        logger.info(f"Context: {request.context}")

    # Check if dry_run is False (default to True for safety)
    dry_run = request.context.get("dry_run", True) if request.context else True

    if dry_run:
        # Phase B behavior: return planned status
        return IntentResponse(
            accepted=False,
            plan_id=plan_id,
            summary="Dry run: Intent received and logged. No actions taken.",
            status="planned",
        )

    # Phase C: Map intent to command and execute
    command = map_intent_to_command(request.intent_text)

    if command is None:
        # Unknown intent - reject
        logger.warning(f"Unknown intent rejected: {request.intent_text}")
        raise HTTPException(
            status_code=400,
            detail=f"Unknown intent: '{request.intent_text}'. Only whitelisted intents are allowed.",
        )

    # Execute the command
    try:
        logger.info(f"Executing command: {command}")
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=30,  # Safety timeout
        )

        summary = f"Command executed: {command}\nExit code: {result.returncode}"
        if result.stdout:
            summary += f"\nOutput: {result.stdout[:500]}"  # Limit output length
        if result.stderr:
            summary += f"\nErrors: {result.stderr[:500]}"

        return IntentResponse(
            accepted=True,
            plan_id=plan_id,
            summary=summary,
            status="completed" if result.returncode == 0 else "failed",
        )
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timeout: {command}")
        raise HTTPException(status_code=504, detail=f"Command timeout: {command}") from e
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e!s}") from e


@router.get("/health")
async def health_check():
    return {"status": "ok", "phase": "C"}
