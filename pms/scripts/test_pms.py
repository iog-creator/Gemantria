#!/usr/bin/env python3
"""
PMS Test Suite - Comprehensive testing of PMS system components.

Tests all PMS components to ensure they work correctly together.
Run with: python pms/scripts/test_pms.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


class PMSTestCase(unittest.TestCase):
    """Base test case for PMS components."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()

        # Create test directory structure
        (self.test_dir / "exports").mkdir()
        (self.test_dir / ".cursor" / "rules").mkdir(parents=True)
        (self.test_dir / "src").mkdir()
        (self.test_dir / "docs").mkdir()

        # Change to test directory
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        # Clean up test directory
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_envelope(self, **kwargs):
        """Create a test hints envelope."""
        envelope = {"type": "hints_envelope", "version": "1.0", "items": ["test hint"], "count": 1, **kwargs}
        return envelope

    def write_test_envelope(self, envelope, filename="test_envelope.json"):
        """Write envelope to test file."""
        path = self.test_dir / "exports" / filename
        with open(path, "w") as f:
            json.dump(envelope, f, indent=2)
        return path


class TestEnvelopeErrorSystem(PMSTestCase):
    """Test envelope error system."""

    def test_validate_envelope_valid(self):
        """Test validating a valid envelope."""
        sys.path.insert(0, str(ROOT / "pms"))
        from core.envelope_error_system import EnvelopeErrorSystem

        system = EnvelopeErrorSystem()
        envelope = self.create_test_envelope()

        self.assertTrue(system._validate_envelope(envelope))

    def test_validate_envelope_invalid(self):
        """Test validating an invalid envelope."""
        sys.path.insert(0, str(ROOT / "pms"))
        from core.envelope_error_system import EnvelopeErrorSystem

        system = EnvelopeErrorSystem()

        # Missing required field
        invalid_envelope = {"type": "hints_envelope", "version": "1.0"}
        self.assertFalse(system._validate_envelope(invalid_envelope))

        # Wrong type
        invalid_envelope = self.create_test_envelope(type="wrong_type")
        self.assertFalse(system._validate_envelope(invalid_envelope))

    def test_execute_imperative_commands(self):
        """Test executing imperative commands."""
        sys.path.insert(0, str(ROOT / "pms"))
        from core.envelope_error_system import EnvelopeErrorSystem

        system = EnvelopeErrorSystem()
        envelope = self.create_test_envelope(imperative_commands=["AGENT_STOP_AND_PAY_ATTENTION"])

        # Should execute without error
        result = system.execute_imperative_commands(envelope, self.test_dir / "test.json")
        self.assertTrue(result)


class TestEnvelopeProcessor(PMSTestCase):
    """Test envelope processor."""

    def test_load_envelope(self):
        """Test loading envelope from file."""
        sys.path.insert(0, str(ROOT / "pms"))
        from scripts.envelope_processor import load_envelope

        envelope = self.create_test_envelope()
        path = self.write_test_envelope(envelope)

        loaded = load_envelope(path)
        self.assertEqual(loaded, envelope)

    def test_find_envelope_files(self):
        """Test finding envelope files."""
        sys.path.insert(0, str(ROOT / "pms"))
        from scripts.envelope_processor import find_envelope_files

        # Create test envelope
        self.write_test_envelope(self.create_test_envelope())

        envelopes = find_envelope_files()
        self.assertTrue(len(envelopes) > 0)


class TestPMSValidator(PMSTestCase):
    """Test PMS validator."""

    def test_validate_hints_envelopes(self):
        """Test envelope validation."""
        sys.path.insert(0, str(ROOT / "pms"))
        from scripts.validate_pms import PMSValidator

        validator = PMSValidator()

        # Create valid envelope
        self.write_test_envelope(self.create_test_envelope())

        self.assertTrue(validator.validate_hints_envelopes())

    def test_validate_agents_md_files_missing(self):
        """Test AGENTS.md validation when files missing."""
        sys.path.insert(0, str(ROOT / "pms"))
        from scripts.validate_pms import PMSValidator

        validator = PMSValidator()

        # Files don't exist, should fail
        self.assertFalse(validator.validate_agents_md_files())


class TestMetadataEnforcement(PMSTestCase):
    """Test metadata enforcement."""

    def test_check_metadata_script_exists(self):
        """Test that metadata enforcement script exists."""
        metadata_script = ROOT / "pms" / "scripts" / "enforce_metadata.py"
        self.assertTrue(metadata_script.exists())

    def test_metadata_script_runs(self):
        """Test that metadata script can be executed."""
        result = subprocess.run(
            [sys.executable, str(ROOT / "pms" / "scripts" / "enforce_metadata.py"), "--help"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        # Should not crash
        self.assertIn("usage:", result.stdout.lower())


class TestPMSIntegration(unittest.TestCase):
    """Integration tests for PMS system."""

    def setUp(self):
        """Set up integration test."""
        self.original_cwd = os.getcwd()
        os.chdir(ROOT)

    def tearDown(self):
        """Clean up integration test."""
        os.chdir(self.original_cwd)

    def test_pms_directory_structure(self):
        """Test that PMS directory structure exists."""
        pms_dir = ROOT / "pms"
        self.assertTrue(pms_dir.exists())

        # Check core subdirectories
        self.assertTrue((pms_dir / "core").exists())
        self.assertTrue((pms_dir / "scripts").exists())
        self.assertTrue((pms_dir / "templates").exists())
        self.assertTrue((pms_dir / "docs").exists())

    def test_pms_scripts_executable(self):
        """Test that PMS scripts are executable."""
        scripts = [
            "pms/scripts/validate_pms.py",
            "pms/scripts/envelope_processor.py",
            "pms/scripts/enforce_metadata.py",
            "pms/scripts/pms_init.py",
        ]

        for script in scripts:
            script_path = ROOT / script
            self.assertTrue(script_path.exists(), f"Script {script} not found")

            # Check if it's a Python script
            with open(script_path) as f:
                first_line = f.readline().strip()
                self.assertTrue(first_line.startswith("#!/usr/bin/env python3"), f"Script {script} has wrong shebang")

    def test_pms_templates_exist(self):
        """Test that PMS templates exist."""
        templates = [
            "pms/templates/PROJECT_MASTER_PLAN.template.md",
            "pms/templates/example-rules.mdc",
            "pms/templates/Makefile.pms",
        ]

        for template in templates:
            template_path = ROOT / template
            self.assertTrue(template_path.exists(), f"Template {template} not found")

    def test_pms_docs_exist(self):
        """Test that PMS documentation exists."""
        docs = ["pms/docs/PROJECT_MANAGEMENT_SYSTEM_SPEC.md", "pms/docs/PMS_README.md"]

        for doc in docs:
            doc_path = ROOT / doc
            self.assertTrue(doc_path.exists(), f"Doc {doc} not found")


def run_tests():
    """Run all PMS tests."""
    print("🧪 Running PMS Test Suite")
    print("=" * 40)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEnvelopeErrorSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvelopeProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestPMSValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestMetadataEnforcement))
    suite.addTests(loader.loadTestsFromTestCase(TestPMSIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 40)
    if result.wasSuccessful():
        print("🎉 ALL PMS TESTS PASSED!")
        return 0
    else:
        print("❌ PMS TESTS FAILED!")
        print(f"Errors: {len(result.errors)}")
        print(f"Failures: {len(result.failures)}")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
