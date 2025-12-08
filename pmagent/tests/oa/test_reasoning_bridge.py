"""Unit tests for pmagent.oa.reasoning_bridge module."""

import pytest


class TestReasoningBridge:
    """Test reasoning bridge envelope and runner functions."""

    def test_program_ids_has_8_entries(self):
        """TV-28B-09: PROGRAM_IDS contains all 8 programs."""
        from pmagent.oa.reasoning_bridge import PROGRAM_IDS

        expected = {
            "SafeOPSDecision",
            "OPSBlockGenerator",
            "GuardFailureInterpreter",
            "PhaseTransitionValidator",
            "HandoffIntegrityValidator",
            "OAToolUsagePrediction",
            "ShareDMSDriftDetector",
            "MultiTurnKernelReasoning",
        }
        assert PROGRAM_IDS == expected

    def test_build_envelope_valid_program(self):
        """TV-28B-10: build_envelope creates valid envelope structure."""
        from pmagent.oa.reasoning_bridge import build_envelope

        envelope = build_envelope(
            program_id="SafeOPSDecision",
            goal="Test goal",
            kernel_data={"handoff": {"kernel_mode": "NORMAL"}},
            oa_context={"task": "test"},
        )

        assert envelope["program_id"] == "SafeOPSDecision"
        assert envelope["goal"] == "Test goal"
        assert "envelope_id" in envelope
        assert "timestamp" in envelope
        assert "kernel_state_ref" in envelope
        assert envelope["kernel_state_ref"]["mode"] == "NORMAL"

    def test_build_envelope_invalid_program_raises(self):
        """TV-28B-11: build_envelope rejects invalid program_id."""
        from pmagent.oa.reasoning_bridge import build_envelope

        with pytest.raises(ValueError) as exc_info:
            build_envelope(
                program_id="InvalidProgram",
                goal="test",
                kernel_data={},
                oa_context={},
            )
        assert "InvalidProgram" in str(exc_info.value)

    def test_build_envelope_all_programs_valid(self):
        """TV-28B-12: build_envelope accepts all 8 program IDs."""
        from pmagent.oa.reasoning_bridge import PROGRAM_IDS, build_envelope

        for program_id in PROGRAM_IDS:
            envelope = build_envelope(
                program_id=program_id,
                goal=f"Test {program_id}",
                kernel_data={},
                oa_context={},
            )
            assert envelope["program_id"] == program_id

    def test_run_reasoning_program_returns_blocked_without_dspy(self):
        """TV-28B-13: run_reasoning_program returns BLOCKED when dspy unavailable."""
        from pmagent.oa.dspy_signatures import is_dspy_available
        from pmagent.oa.reasoning_bridge import build_envelope, run_reasoning_program

        if not is_dspy_available():
            envelope = build_envelope(
                program_id="SafeOPSDecision",
                goal="Test",
                kernel_data={},
                oa_context={},
            )
            result = run_reasoning_program(envelope)
            assert result["status"] == "BLOCKED"
            assert "dspy" in result["rationale"].lower()

    def test_reasoning_result_schema(self):
        """TV-28B-14: ReasoningResult TypedDict has correct fields."""
        from pmagent.oa.reasoning_bridge import ReasoningResult

        # Check TypedDict has expected keys
        expected_fields = {
            "envelope_id",
            "program_id",
            "status",
            "decision",
            "rationale",
            "tool_calls",
            "diagnostics",
        }
        assert set(ReasoningResult.__annotations__.keys()) == expected_fields

    def test_envelope_includes_tools_allowed(self):
        """TV-28B-15: build_envelope includes tools_allowed list."""
        from pmagent.oa.reasoning_bridge import build_envelope

        envelope = build_envelope(
            program_id="SafeOPSDecision",
            goal="Test",
            kernel_data={},
            oa_context={},
            tools_allowed=["oa.kernel_status", "oa.guard.run"],
        )
        assert envelope["tools_allowed"] == ["oa.kernel_status", "oa.guard.run"]
