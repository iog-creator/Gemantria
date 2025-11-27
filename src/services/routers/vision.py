#!/usr/bin/env python3
"""
Vision Inference Router.

Provides /api/inference/vision endpoint for multimodal vision tasks.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agentpm.adapters.vision import vision_chat
from scripts.config.env import get_lm_model_config

router = APIRouter()


class VisionRequest(BaseModel):
    """Request model for vision inference."""

    prompt: str
    images: list[str] = []  # Base64-encoded images
    system: str | None = None
    model: str | None = None


class VisionResponse(BaseModel):
    """Response model for vision inference."""

    response: str
    model: str
    provider: str
    tokens_used: int | None = None  # optional for later


@router.post("/api/inference/vision", response_model=VisionResponse)
async def vision_inference(req: VisionRequest) -> VisionResponse:
    """Vision inference endpoint for multimodal tasks.

    Args:
        req: VisionRequest with prompt, images, optional system prompt and model

    Returns:
        VisionResponse with model response, model name, provider, and optional token usage

    Raises:
        HTTPException: If vision inference fails
    """
    try:
        cfg = get_lm_model_config()
        model_name = req.model or cfg.get("vision_model", "qwen3-vl-4b")
        provider = cfg.get("vision_provider", "lmstudio")

        # Call vision adapter
        text = vision_chat(
            prompt=req.prompt,
            images=req.images if req.images else None,
            system=req.system,
            model=req.model,
        )

        return VisionResponse(
            response=text,
            model=model_name,
            provider=provider,
            tokens_used=None,  # TODO: Extract from API response if available
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision inference failed: {e!s}") from e
