#!/usr/bin/env python3
"""
Vision Tool for Explicit Vision Analysis.

Exposes vision capabilities as a callable tool for explicit use by agents.
"""

from __future__ import annotations

from typing import Any

from agentpm.adapters.vision import vision_chat


def vision_analyze(
    prompt: str,
    images: list[str] | None = None,
    *,
    describe_images: bool = True,
) -> dict[str, Any]:
    """Explicit vision analysis tool for agents.

    Args:
        prompt: Text prompt describing what to analyze
        images: List of image data (base64 strings or bytes)
        describe_images: Whether to generate detailed image descriptions

    Returns:
        Dict with analysis results:
        - analysis: str - Main analysis text
        - image_descriptions: list[str] - Descriptions of each image (if describe_images=True)
        - model: str - Model used for analysis
    """
    # Build enhanced prompt if image descriptions are requested
    enhanced_prompt = prompt
    if describe_images and images:
        enhanced_prompt = (
            f"{prompt}\n\nPlease provide a detailed description of each image and how it relates to the task."
        )

    # Call vision adapter
    analysis = vision_chat(
        prompt=enhanced_prompt,
        images=images,
        system="You are a vision analysis assistant. Analyze images carefully and provide detailed, accurate descriptions.",
    )

    # Extract image descriptions if requested
    image_descriptions = []
    if describe_images and images:
        # For now, the analysis includes descriptions in the response
        # In the future, we could make separate calls for each image
        image_descriptions = [analysis]  # Simplified - full implementation would parse descriptions

    return {
        "analysis": analysis,
        "image_descriptions": image_descriptions if describe_images else [],
        "model": "qwen3-vl-4b",  # TODO: Get from config
    }
