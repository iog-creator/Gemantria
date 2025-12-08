#!/usr/bin/env python3
"""
OA Reasoning Bridge Scaffolding (Phase 27.F).

This module defines the types and interface for the bridge between OA and
future DSPy reasoning programs. It contains NO DSPy imports or runtime logic.
"""

from __future__ import annotations

import uuid
from datetime import datetime, UTC
from typing import Any, List, Literal, TypedDict

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
    details: dict[str, Any] | None


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
    "HandoffIntegrityValidator",
    "OAToolUsagePrediction",
    "ShareDMSDriftDetector",
    "MultiTurnKernelReasoning",
}


# --- Bridge Interface (Scaffolding) ---


def build_envelope(
    program_id: str,
    goal: str,
    kernel_data: dict[str, Any],
    oa_context: dict[str, Any],
    tools_allowed: List[str] | None = None,
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
        "timestamp": datetime.now(UTC).isoformat(),
        "program_id": program_id,
        "goal": goal,
        "kernel_state_ref": kernel_ref,
        "oa_context": oa_context,
        "tools_allowed": tools_allowed or [],
    }


def run_reasoning_program(envelope: ReasoningEnvelope) -> ReasoningResult:
    """
    Execute a reasoning program.

    Uses DSPy if available, otherwise returns BLOCKED status.

    Args:
        envelope: The reasoning envelope with program_id, goal, kernel state.

    Returns:
        ReasoningResult with decision and rationale.
    """
    import json

    # Try to import DSPy signatures
    try:
        from pmagent.oa.dspy_signatures import create_module, is_dspy_available

        if not is_dspy_available():
            return {
                "envelope_id": envelope["envelope_id"],
                "program_id": envelope["program_id"],
                "status": "BLOCKED",
                "decision": {},
                "rationale": "DSPy not installed. Install with: pip install dspy-ai",
                "tool_calls": [],
                "diagnostics": [
                    {
                        "category": "dependency",
                        "severity": "error",
                        "message": "dspy-ai package not found",
                        "details": None,
                    }
                ],
            }

        # Create module and run
        module = create_module(envelope["program_id"])
        if module is None:
            return {
                "envelope_id": envelope["envelope_id"],
                "program_id": envelope["program_id"],
                "status": "FAILED",
                "decision": {},
                "rationale": "Failed to create DSPy module",
                "tool_calls": [],
                "diagnostics": [],
            }

        # Prepare inputs based on program type
        kernel_json = json.dumps(envelope["kernel_state_ref"])
        context_json = json.dumps(envelope["oa_context"])

        program_id = envelope["program_id"]

        if program_id == "SafeOPSDecision":
            result = module(
                kernel_state=kernel_json,
                proposed_ops=envelope["goal"],
                oa_context=context_json,
            )
            return {
                "envelope_id": envelope["envelope_id"],
                "program_id": program_id,
                "status": "OK",
                "decision": {
                    "allowed": result.decision == "ALLOW",
                    "required_guards": getattr(result, "required_guards", []),
                    "risk_factors": getattr(result, "risk_factors", []),
                },
                "rationale": getattr(result, "rationale", ""),
                "tool_calls": [],
                "diagnostics": [],
            }

        elif program_id == "OPSBlockGenerator":
            result = module(
                pm_goal=envelope["goal"],
                kernel_state=kernel_json,
                relevant_ssot_docs=envelope["oa_context"].get("ssot_docs", []),
                hints=envelope["oa_context"].get("hints", []),
            )
            return {
                "envelope_id": envelope["envelope_id"],
                "program_id": program_id,
                "status": "OK",
                "decision": {
                    "ops_block_goal": getattr(result, "ops_block_goal", ""),
                    "ops_block_commands": getattr(result, "ops_block_commands", []),
                    "success_criteria": getattr(result, "success_criteria", []),
                },
                "rationale": f"Confidence: {getattr(result, 'confidence', 0.0)}",
                "tool_calls": [],
                "diagnostics": [],
            }

        elif program_id == "GuardFailureInterpreter":
            result = module(
                guard_name=envelope["oa_context"].get("guard_name", "unknown"),
                guard_output=envelope["goal"],
                kernel_state=kernel_json,
            )
            return {
                "envelope_id": envelope["envelope_id"],
                "program_id": program_id,
                "status": "OK",
                "decision": {
                    "diagnosis": getattr(result, "diagnosis", ""),
                    "root_cause": getattr(result, "root_cause", ""),
                    "remediation_steps": getattr(result, "remediation_steps", []),
                    "is_transient": getattr(result, "is_transient", False),
                },
                "rationale": getattr(result, "diagnosis", ""),
                "tool_calls": [],
                "diagnostics": [],
            }

        elif program_id == "PhaseTransitionValidator":
            result = module(
                current_phase=envelope["oa_context"].get("current_phase", ""),
                proposed_phase=envelope["oa_context"].get("proposed_phase", ""),
                kernel_state=kernel_json,
                phase_exit_criteria=json.dumps(envelope["oa_context"].get("exit_criteria", {})),
            )
            return {
                "envelope_id": envelope["envelope_id"],
                "program_id": program_id,
                "status": "OK",
                "decision": {
                    "allowed": getattr(result, "allowed", False),
                    "blockers": getattr(result, "blockers", []),
                    "recommendations": getattr(result, "recommendations", []),
                },
                "rationale": f"Allowed: {getattr(result, 'allowed', False)}",
                "tool_calls": [],
                "diagnostics": [],
            }

        elif program_id == "HandoffIntegrityValidator":
            result = module(
                kernel_state=kernel_json,
                handoff_goal=envelope["goal"],
                oa_context=context_json,
            )
            return {
                "envelope_id": envelope["envelope_id"],
                "program_id": program_id,
                "status": "OK",
                "decision": {
                    "integrity_status": getattr(result, "integrity_status", "incomplete"),
                    "blockers": getattr(result, "blockers", []),
                },
                "rationale": getattr(result, "rationale", ""),
                "tool_calls": [],
                "diagnostics": [],
            }

        elif program_id == "OAToolUsagePrediction":
            result = module(
                kernel_state=kernel_json,
                oa_context=context_json,
                task=envelope["goal"],
            )
            return {
                "envelope_id": envelope["envelope_id"],
                "program_id": program_id,
                "status": "OK",
                "decision": {
                    "tool_sequence": getattr(result, "tool_sequence", []),
                },
                "rationale": getattr(result, "rationale", ""),
                "tool_calls": [],
                "diagnostics": [],
            }

        elif program_id == "ShareDMSDriftDetector":
            result = module(
                kernel_state=kernel_json,
                oa_context=context_json,
            )
            return {
                "envelope_id": envelope["envelope_id"],
                "program_id": program_id,
                "status": "OK",
                "decision": {
                    "drift_category": getattr(result, "drift_category", "none"),
                    "missing_docs": getattr(result, "missing_docs", []),
                    "unexpected_artifacts": getattr(result, "unexpected_artifacts", []),
                    "recommended_commands": getattr(result, "recommended_commands", []),
                },
                "rationale": f"Drift: {getattr(result, 'drift_category', 'none')}",
                "tool_calls": [],
                "diagnostics": [],
            }

        elif program_id == "MultiTurnKernelReasoning":
            result = module(
                kernel_state=kernel_json,
                oa_context=context_json,
                task=envelope["goal"],
            )
            return {
                "envelope_id": envelope["envelope_id"],
                "program_id": program_id,
                "status": "OK",
                "decision": getattr(result, "decision", {}),
                "rationale": getattr(result, "rationale", ""),
                "tool_calls": [],
                "diagnostics": [
                    {
                        "category": "trace",
                        "severity": "info",
                        "message": "Multi-turn reasoning trace",
                        "details": {"steps": getattr(result, "trace_steps", [])},
                    }
                ],
            }

        # For unknown programs, return error
        return {
            "envelope_id": envelope["envelope_id"],
            "program_id": program_id,
            "status": "FAILED",
            "decision": {},
            "rationale": f"Unknown program_id: {program_id}",
            "tool_calls": [],
            "diagnostics": [],
        }

    except ImportError:
        return {
            "envelope_id": envelope["envelope_id"],
            "program_id": envelope["program_id"],
            "status": "BLOCKED",
            "decision": {},
            "rationale": "DSPy signatures module not found.",
            "tool_calls": [],
            "diagnostics": [],
        }
    except Exception as e:
        return {
            "envelope_id": envelope["envelope_id"],
            "program_id": envelope["program_id"],
            "status": "FAILED",
            "decision": {},
            "rationale": f"Reasoning program failed: {e}",
            "tool_calls": [],
            "diagnostics": [
                {
                    "category": "runtime",
                    "severity": "error",
                    "message": str(e),
                    "details": None,
                }
            ],
        }
