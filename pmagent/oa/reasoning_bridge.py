#!/usr/bin/env python3
"""
OA Reasoning Bridge Scaffolding (Phase 27.F).

This module defines the types and interface for the bridge between OA and
future DSPy reasoning programs. It contains NO DSPy imports or runtime logic.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, List, Literal, Optional, TypedDict

# --- Core Schemas ---
# These match docs/SSOT/oa/OA_REASONING_BRIDGE.md


class KernelStateRef(TypedDict):
    """Unified view of kernel state."""

    mode: str
    bootstrap: dict[str, Any]
    ssot_index: dict[str, Any]
    reality_summary: dict[str, Any]
    oa_state: dict[str, Any]


class ReasoningEnvelope(TypedDict):
    """Immutable input payload for reasoning programs."""

    envelope_id: str
    timestamp: str  # ISO8601
    program_id: str
    goal: str
    kernel_state_ref: KernelStateRef
    oa_context: dict[str, Any]
    tools_allowed: List[str]


class DiagnosticEvent(TypedDict):
    """Diagnostic event from OA diagnostics catalog."""

    category: str
    severity: str
    message: str
    details: Optional[dict[str, Any]]


class ReasoningResult(TypedDict):
    """Structured output from reasoning programs."""

    envelope_id: str
    program_id: str
    status: Literal["OK", "DEGRADED", "BLOCKED", "FAILED"]
    decision: dict[str, Any]  # Program-specific payload
    rationale: str
    tool_calls: List[dict[str, Any]]
    diagnostics: List[DiagnosticEvent]


# --- Program-Specific Result Payloads ---


class SafeOPSDecisionResult(TypedDict):
    """Payload for SafeOPSDecision."""

    allowed_action: Literal["PROCEED", "ABORT", "WARN"]
    safety_check_summary: str


class OPSBlockGeneratorResult(TypedDict):
    """Payload for OPSBlockGenerator."""

    ops_block: List[str]
    complexity_score: int
    risk_analysis: str


class GuardFailureInterpreterResult(TypedDict):
    """Payload for GuardFailureInterpreter."""

    root_cause: str
    remediation_plan: str
    is_transient: bool


class PhaseTransitionValidatorResult(TypedDict):
    """Payload for PhaseTransitionValidator."""

    transition_status: Literal["READY", "NOT_READY"]
    missing_criteria: List[str]


# --- Constants ---

PROGRAM_IDS = {
    "SafeOPSDecision",
    "OPSBlockGenerator",
    "GuardFailureInterpreter",
    "PhaseTransitionValidator",
}


# --- Bridge Interface (Scaffolding) ---


def build_envelope(
    program_id: str,
    goal: str,
    kernel_data: dict[str, Any],
    oa_context: dict[str, Any],
    tools_allowed: Optional[List[str]] = None,
) -> ReasoningEnvelope:
    """
    Build a ReasoningEnvelope using provided kernel data and context.

    Args:
        program_id: One of the allowed program IDs.
        goal: The goal string.
        kernel_data: Dict containing 'bootstrap', 'ssot', 'reality', 'oa_state', 'handoff'.
        oa_context: Operations context dict.
        tools_allowed: List of allowed tool IDs.

    Returns:
        Structured ReasoningEnvelope.
    """
    if program_id not in PROGRAM_IDS:
        raise ValueError(f"Invalid program_id: {program_id}")

    # Construct KernelStateRef helpers
    kernel_ref: KernelStateRef = {
        "mode": kernel_data.get("handoff", {}).get("kernel_mode", "UNKNOWN"),
        "bootstrap": kernel_data.get("bootstrap", {}),
        "ssot_index": kernel_data.get("ssot", {}),
        "reality_summary": kernel_data.get("reality", {}),
        "oa_state": kernel_data.get("oa_state", {}),
    }

    return {
        "envelope_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "program_id": program_id,
        "goal": goal,
        "kernel_state_ref": kernel_ref,
        "oa_context": oa_context,
        "tools_allowed": tools_allowed or [],
    }


def run_reasoning_program(envelope: ReasoningEnvelope) -> ReasoningResult:
    """
    Execute a reasoning program (STUB).

    In Phase 27.F, this is a placeholder. DSPy integration happens in Phase 28.

    Returns:
        ReasoningResult with status='BLOCKED' indicating not implemented.
    """
    return {
        "envelope_id": envelope["envelope_id"],
        "program_id": envelope["program_id"],
        "status": "BLOCKED",
        "decision": {},
        "rationale": "DSPy integration not implemented (Phase 27.F scaffolding only).",
        "tool_calls": [],
        "diagnostics": [],
    }
