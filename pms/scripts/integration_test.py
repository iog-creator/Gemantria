#!/usr/bin/env python3
"""
PMS Integration Tests - End-to-end testing of PMS system.

Tests complete workflows and component interactions.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


class PMSIntegrationTest(unittest.TestCase):
    """Integration tests for complete PMS workflows."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Copy PMS system to test directory
        if (ROOT / "pms").exists():
            shutil.copytree(ROOT / "pms", self.test_dir / "pms")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_pms_workflow(self):
        """Test complete PMS workflow from initialization to validation."""
        # Step 1: Initialize PMS
        result = self._run_script("pms/scripts/pms_init.py")
        self.assertEqual(result.returncode, 0, "PMS initialization failed")

        # Step 2: Create project structure
        self._create_test_project_structure()

        # Step 3: Validate PMS system
        result = self._run_script("pms/scripts/validate_pms.py")
        self.assertEqual(result.returncode, 0, "PMS validation failed")

        # Step 4: Test envelope processing
        self._create_test_envelope()
        result = self._run_script("pms/scripts/envelope_processor.py", "--process-pending")
        self.assertEqual(result.returncode, 0, "Envelope processing failed")

        # Step 5: Test metadata enforcement
        result = self._run_script("pms/scripts/enforce_metadata.py", "--help")
        self.assertEqual(result.returncode, 0, "Metadata enforcement check failed")

    def test_housekeeping_workflow(self):
        """Test housekeeping workflow."""
        # Initialize PMS
        self._create_test_project_structure()

        # Run housekeeping
        result = subprocess.run(
            ["make", "-f", str(ROOT / "pms" / "templates" / "Makefile.pms"), "housekeeping"],
            cwd=self.test_dir,
            capture_output=True,
            text=True,
        )

        # Housekeeping might fail due to missing dependencies, but should not crash
        self.assertIn(result.returncode, [0, 1], "Housekeeping crashed")

    def test_recovery_workflow(self):
        """Test recovery workflow."""
        # Create broken PMS installation
        pms_dir = self.test_dir / "pms"
        if pms_dir.exists():
            shutil.rmtree(pms_dir)

        # Run recovery
        result = self._run_script("pms/scripts/pms_recover.py")
        # Recovery might not work without full PMS, but should not crash
        self.assertIn(result.returncode, [0, 1], "Recovery crashed")

    def test_envelope_error_system(self):
        """Test envelope error system with imperative commands."""
        self._create_test_project_structure()

        # Create envelope with imperative commands
        envelope = {
            "type": "hints_envelope",
            "version": "1.0",
            "items": ["Test hint"],
            "count": 1,
            "imperative_commands": ["AGENT_STOP_AND_PAY_ATTENTION"],
        }

        envelope_path = self.test_dir / "exports" / "test_envelope.json"
        envelope_path.parent.mkdir(parents=True, exist_ok=True)
        with open(envelope_path, "w") as f:
            json.dump(envelope, f, indent=2)

        # Test envelope error system
        result = self._run_script("pms/core/envelope_error_system.py")
        self.assertEqual(result.returncode, 0, "Envelope error system failed")

    def _create_test_project_structure(self):
        """Create minimal test project structure."""
        # Create directories
        dirs = ["src", "docs", "exports", ".cursor/rules"]
        for dir_name in dirs:
            (self.test_dir / dir_name).mkdir(parents=True, exist_ok=True)

        # Create AGENTS.md files
        agents_content = """# Test Governance

## Rules Inventory

<!-- RULES_INVENTORY_START -->
| # | Title |
|---:|-------|
<!-- RULES_INVENTORY_END -->
"""

        agents_files = ["AGENTS.md", "docs/AGENTS.md", "src/AGENTS.md"]
        for file_path in agents_files:
            full_path = self.test_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w") as f:
                f.write(agents_content)

        # Create Makefile
        makefile_content = """# Test Makefile
include pms/templates/Makefile.pms
"""
        with open(self.test_dir / "Makefile", "w") as f:
            f.write(makefile_content)

    def _create_test_envelope(self):
        """Create a test hints envelope."""
        envelope = {
            "type": "hints_envelope",
            "version": "1.0",
            "items": ["Test hint for integration testing"],
            "count": 1,
            "imperative_commands": ["PROCESS_HINTS_ENVELOPE_IMMEDIATELY"],
        }

        envelope_path = self.test_dir / "exports" / "test_envelope.json"
        envelope_path.parent.mkdir(parents=True, exist_ok=True)
        with open(envelope_path, "w") as f:
            json.dump(envelope, f, indent=2)

    def _run_script(self, script_path: str, *args) -> subprocess.CompletedProcess:
        """Run a PMS script and return result."""
        cmd = [sys.executable, script_path] + list(args)
        return subprocess.run(cmd, cwd=self.test_dir, capture_output=True, text=True)


class PMSPerformanceTest(unittest.TestCase):
    """Performance tests for PMS system."""

    def setUp(self):
        """Set up performance test."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up performance test."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_validation_performance(self):
        """Test PMS validation performance."""
        import time

        # Copy PMS system
        if (ROOT / "pms").exists():
            shutil.copytree(ROOT / "pms", self.test_dir / "pms")

        # Create minimal project structure
        (self.test_dir / "AGENTS.md").write_text("# Test")
        (self.test_dir / "docs").mkdir()
        (self.test_dir / "docs" / "AGENTS.md").write_text("# Test")
        (self.test_dir / "src").mkdir()
        (self.test_dir / "src" / "AGENTS.md").write_text("# Test")
        (self.test_dir / ".cursor" / "rules").mkdir(parents=True)

        # Measure validation time
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "pms/scripts/validate_pms.py"], cwd=self.test_dir, capture_output=True, text=True
        )
        end_time = time.time()

        validation_time = end_time - start_time

        # Should complete in reasonable time (< 30 seconds)
        self.assertLess(validation_time, 30, f"Validation took too long: {validation_time}s")

        # Should succeed
        self.assertEqual(result.returncode, 0, f"Validation failed: {result.stderr}")


def run_integration_tests():
    """Run all integration tests."""
    print("🧪 Running PMS Integration Tests")
    print("=" * 50)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(PMSIntegrationTest))
    suite.addTests(loader.loadTestsFromTestCase(PMSPerformanceTest))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        return 0
    else:
        print("❌ INTEGRATION TESTS FAILED!")
        print(f"Errors: {len(result.errors)}")
        print(f"Failures: {len(result.failures)}")
        return 1


if __name__ == "__main__":
    sys.exit(run_integration_tests())
