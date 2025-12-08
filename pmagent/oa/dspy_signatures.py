#!/usr/bin/env python3
"""
DSPy Signatures for OA Reasoning Programs (Phase 28).

This module defines dspy.Signature classes for the four OA reasoning programs.
Import is guarded - dspy is optional for development without it installed.

Training data: examples/dspy/*.jsonl
Schemas: docs/SSOT/oa/OA_REASONING_BRIDGE.md
"""

from __future__ import annotations

from typing import Any, List, Literal, TYPE_CHECKING

# Guard dspy import - falls back gracefully if not installed
try:
    import dspy

    HAS_DSPY = True
except ImportError:
    HAS_DSPY = False
    dspy = None  # type: ignore


# ============================================================================
# Type-only stubs for when dspy is not installed
# ============================================================================

if TYPE_CHECKING or not HAS_DSPY:
    # Define minimal stubs for type checking and non-dspy environments
    class SignatureStub:
        """Stub base class when dspy is not available."""

        pass

    if not HAS_DSPY:

        class DummyField:
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                self.desc = kwargs.get("desc", "")

        class DummySignature:
            pass

        # Make dspy a stub namespace
        class dspy:  # type: ignore  # noqa: N801
            class Signature(DummySignature):
                pass

            @staticmethod
            def InputField(*args: Any, **kwargs: Any) -> Any:
                return kwargs.get("default", None)

            @staticmethod
            def OutputField(*args: Any, **kwargs: Any) -> Any:
                return kwargs.get("default", None)


# ============================================================================
# DSPy Signatures for OA Reasoning Programs
# ============================================================================


class SafeOPSDecisionSignature(dspy.Signature):
    """
    Decide if proposed OPS work is safe given current kernel state.

    Training data: examples/dspy/*.jsonl (program_id=SafeOPSDecision)
    """

    # Inputs
    kernel_state: str = dspy.InputField(desc="Current kernel mode, health, and interpretation as JSON string")
    proposed_ops: str = dspy.InputField(
        desc="Description of proposed OPS work (e.g., 'migrate schema', 'add new phase')"
    )
    oa_context: str = dspy.InputField(desc="OA context including constraints and active goal as JSON string")

    # Outputs
    decision: Literal["ALLOW", "DENY", "CONDITIONAL"] = dspy.OutputField(
        desc="ALLOW = safe to proceed, DENY = forbidden, CONDITIONAL = requires guards first"
    )
    rationale: str = dspy.OutputField(desc="Chain-of-thought explanation based on kernel state and OPS contract rules")
    required_guards: List[str] = dspy.OutputField(desc="Guards that must pass before proceeding (if CONDITIONAL)")
    risk_factors: List[str] = dspy.OutputField(desc="Risk factors identified in the proposed work")


class OPSBlockGeneratorSignature(dspy.Signature):
    """
    Generate a complete OPS block from PM goal and kernel state.

    Training data: examples/dspy/*.jsonl (program_id=OPSBlockGenerator)
    """

    # Inputs
    pm_goal: str = dspy.InputField(desc="PM's stated goal (e.g., 'Implement Phase 27.A kernel interpreter')")
    kernel_state: str = dspy.InputField(desc="Current kernel mode, phase, health as JSON string")
    relevant_ssot_docs: List[str] = dspy.InputField(desc="SSOT doc paths relevant to the goal")
    hints: List[str] = dspy.InputField(desc="Hints from registry relevant to the goal")

    # Outputs
    ops_block_goal: str = dspy.OutputField(desc="Single sentence stating the objective")
    ops_block_commands: List[str] = dspy.OutputField(desc="Runnable shell commands in execution order")
    success_criteria: List[str] = dspy.OutputField(desc="Observable outcomes that indicate success")
    confidence: float = dspy.OutputField(desc="Confidence score 0.0-1.0 that OPS block is correct and complete")


class GuardFailureInterpreterSignature(dspy.Signature):
    """
    Interpret guard failure and recommend remediation.

    Training data: examples/dspy/*.jsonl (program_id=GuardFailureInterpreter)
    """

    # Inputs
    guard_name: str = dspy.InputField(desc="Name of failed guard (e.g., 'reality.green', 'dms_alignment')")
    guard_output: str = dspy.InputField(desc="Raw output from guard script (stdout + stderr)")
    kernel_state: str = dspy.InputField(desc="Current kernel state for context as JSON string")

    # Outputs
    diagnosis: str = dspy.OutputField(desc="Human-readable explanation of what went wrong")
    root_cause: str = dspy.OutputField(desc="Likely root cause (e.g., 'lint errors in pmagent/', 'missing config')")
    remediation_steps: List[str] = dspy.OutputField(desc="Ordered list of commands to fix the issue")
    is_transient: bool = dspy.OutputField(desc="True if failure is likely transient (e.g., network issue)")


class PhaseTransitionValidatorSignature(dspy.Signature):
    """
    Validate if transitioning from current phase to proposed phase is allowed.

    Training data: examples/dspy/*.jsonl (program_id=PhaseTransitionValidator)
    """

    # Inputs
    current_phase: str = dspy.InputField(desc="Current phase number (e.g., '27')")
    proposed_phase: str = dspy.InputField(desc="Proposed next phase number (e.g., '28')")
    kernel_state: str = dspy.InputField(desc="Current kernel state as JSON string")
    phase_exit_criteria: str = dspy.InputField(
        desc="Exit criteria for current phase from PHASE_INDEX doc as JSON string"
    )

    # Outputs
    allowed: bool = dspy.OutputField(desc="True if transition is allowed, False otherwise")
    blockers: List[str] = dspy.OutputField(desc="Items blocking transition (if allowed=False)")
    recommendations: List[str] = dspy.OutputField(desc="Recommended actions before proceeding")


class HandoffIntegrityValidatorSignature(dspy.Signature):
    """
    Validate handoff surfaces are complete and coherent.

    Training data: examples/dspy/handoff_integrity_validator.jsonl
    """

    # Inputs
    kernel_state: str = dspy.InputField(desc="Current kernel state as JSON string")
    handoff_goal: str = dspy.InputField(desc="Goal or task for handoff validation")
    oa_context: str = dspy.InputField(desc="OA context including constraints as JSON string")

    # Outputs
    integrity_status: Literal["clean", "dirty", "incomplete"] = dspy.OutputField(
        desc="clean = handoff complete, dirty = conflicts present, incomplete = missing items"
    )
    blockers: List[str] = dspy.OutputField(desc="Items blocking clean handoff")
    rationale: str = dspy.OutputField(desc="Explanation of integrity assessment")


class OAToolUsagePredictionSignature(dspy.Signature):
    """
    Predict sequence of OA tools to call for a task.

    Training data: examples/dspy/oa_tool_usage_prediction.jsonl
    """

    # Inputs
    kernel_state: str = dspy.InputField(desc="Current kernel state as JSON string")
    oa_context: str = dspy.InputField(desc="OA context with task description as JSON string")
    task: str = dspy.InputField(desc="Task description for tool prediction")

    # Outputs
    tool_sequence: List[str] = dspy.OutputField(
        desc="Ordered list of OA tools to call (e.g., ['oa.kernel_status', 'oa.guard.run:reality.green'])"
    )
    rationale: str = dspy.OutputField(desc="Explanation of why these tools were selected")


class ShareDMSDriftDetectorSignature(dspy.Signature):
    """
    Detect drift between share/ artifacts and DMS registry.

    Training data: examples/dspy/share_dms_drift_detector.jsonl
    """

    # Inputs
    kernel_state: str = dspy.InputField(desc="Current kernel state as JSON string")
    oa_context: str = dspy.InputField(desc="OA context as JSON string")

    # Outputs
    drift_category: Literal["none", "minor", "major", "critical"] = dspy.OutputField(
        desc="none = in sync, minor = cosmetic, major = functional, critical = blocking"
    )
    missing_docs: List[str] = dspy.OutputField(desc="Docs in DMS but missing from share/")
    unexpected_artifacts: List[str] = dspy.OutputField(desc="Artifacts in share/ not in DMS")
    recommended_commands: List[str] = dspy.OutputField(desc="Commands to resolve drift")


class MultiTurnKernelReasoningSignature(dspy.Signature):
    """
    Multi-step reasoning with kernel state and trace.

    Training data: examples/dspy/multi_turn_kernel_reasoning.jsonl
    """

    # Inputs
    kernel_state: str = dspy.InputField(desc="Current kernel state as JSON string")
    oa_context: str = dspy.InputField(desc="OA context with task as JSON string")
    task: str = dspy.InputField(desc="Multi-step reasoning task")

    # Outputs
    decision: dict = dspy.OutputField(desc="Final decision payload")
    rationale: str = dspy.OutputField(desc="Overall reasoning explanation")
    trace_steps: List[str] = dspy.OutputField(desc="Ordered list of reasoning steps taken")


# ============================================================================
# Signature Registry
# ============================================================================

SIGNATURES = {
    "SafeOPSDecision": SafeOPSDecisionSignature,
    "OPSBlockGenerator": OPSBlockGeneratorSignature,
    "GuardFailureInterpreter": GuardFailureInterpreterSignature,
    "PhaseTransitionValidator": PhaseTransitionValidatorSignature,
    "HandoffIntegrityValidator": HandoffIntegrityValidatorSignature,
    "OAToolUsagePrediction": OAToolUsagePredictionSignature,
    "ShareDMSDriftDetector": ShareDMSDriftDetectorSignature,
    "MultiTurnKernelReasoning": MultiTurnKernelReasoningSignature,
}


def get_signature(program_id: str) -> type:
    """Get DSPy signature class for a program ID."""
    if program_id not in SIGNATURES:
        raise ValueError(f"Unknown program_id: {program_id}. Valid: {list(SIGNATURES.keys())}")
    return SIGNATURES[program_id]


def is_dspy_available() -> bool:
    """Check if dspy is installed and available."""
    return HAS_DSPY


# ============================================================================
# Module pattern for DSPy (when available)
# ============================================================================


def create_module(program_id: str) -> Any | None:
    """
    Create a DSPy Module for the given program.

    Returns None if dspy is not installed.

    Usage:
        module = create_module("SafeOPSDecision")
        if module:
            result = module(kernel_state=..., proposed_ops=...)
    """
    if not HAS_DSPY:
        return None

    sig_class = get_signature(program_id)

    class ReasoningModule(dspy.Module):
        def __init__(self) -> None:
            super().__init__()
            self.predictor = dspy.ChainOfThought(sig_class)

        def forward(self, **kwargs: Any) -> Any:
            return self.predictor(**kwargs)

    return ReasoningModule()
