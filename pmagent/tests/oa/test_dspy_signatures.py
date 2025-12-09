"""Unit tests for pmagent.oa.dspy_signatures module."""

import pytest


class TestDSPySignatures:
    """Test DSPy signature classes and registry."""

    def test_import_without_dspy(self):
        """TV-28B-01: Module imports successfully without dspy installed."""
        from pmagent.oa.dspy_signatures import SIGNATURES, is_dspy_available

        assert isinstance(SIGNATURES, dict)
        # is_dspy_available returns a boolean
        assert isinstance(is_dspy_available(), bool)

    def test_signatures_registry_has_9_programs(self):
        """TV-28B-02: SIGNATURES registry contains all 9 programs (8 original + ExplainSystemState)."""
        from pmagent.oa.dspy_signatures import SIGNATURES

        expected_programs = {
            "SafeOPSDecision",
            "OPSBlockGenerator",
            "GuardFailureInterpreter",
            "PhaseTransitionValidator",
            "HandoffIntegrityValidator",
            "OAToolUsagePrediction",
            "ShareDMSDriftDetector",
            "MultiTurnKernelReasoning",
            "ExplainSystemState",
        }
        assert set(SIGNATURES.keys()) == expected_programs

    def test_get_signature_valid_program(self):
        """TV-28B-03: get_signature returns correct class for valid program."""
        from pmagent.oa.dspy_signatures import get_signature, SafeOPSDecisionSignature

        sig_class = get_signature("SafeOPSDecision")
        assert sig_class is SafeOPSDecisionSignature

    def test_get_signature_invalid_program_raises(self):
        """TV-28B-04: get_signature raises ValueError for unknown program."""
        from pmagent.oa.dspy_signatures import get_signature

        with pytest.raises(ValueError) as exc_info:
            get_signature("UnknownProgram")
        assert "UnknownProgram" in str(exc_info.value)

    def test_is_dspy_available_returns_bool(self):
        """TV-28B-05: is_dspy_available returns a boolean."""
        from pmagent.oa.dspy_signatures import is_dspy_available

        result = is_dspy_available()
        assert result in (True, False)

    def test_create_module_without_dspy_returns_none(self):
        """TV-28B-06: create_module returns None when dspy unavailable."""
        from pmagent.oa.dspy_signatures import create_module, is_dspy_available

        if not is_dspy_available():
            module = create_module("SafeOPSDecision")
            assert module is None

    def test_all_signatures_are_classes(self):
        """TV-28B-07: All signature values in registry are classes."""
        from pmagent.oa.dspy_signatures import SIGNATURES

        for program_id, sig_class in SIGNATURES.items():
            assert isinstance(sig_class, type), f"{program_id} is not a class"

    def test_new_signatures_exist(self):
        """TV-28B-08: New Phase 28B signatures are properly defined."""
        from pmagent.oa.dspy_signatures import (
            HandoffIntegrityValidatorSignature,
            MultiTurnKernelReasoningSignature,
            OAToolUsagePredictionSignature,
            ShareDMSDriftDetectorSignature,
        )

        # Just confirm they exist and are classes
        assert isinstance(HandoffIntegrityValidatorSignature, type)
        assert isinstance(OAToolUsagePredictionSignature, type)
        assert isinstance(ShareDMSDriftDetectorSignature, type)
        assert isinstance(MultiTurnKernelReasoningSignature, type)
