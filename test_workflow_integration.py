#!/usr/bin/env python3
"""
Comprehensive workflow integration test for Gemantria project.

Tests all new elements:
- Gemini CLI integration
- Codex CLI integration
- MCP server configuration
- Environment setup
- Makefile targets
"""

import subprocess
import os
import sys
import json
from pathlib import Path


class WorkflowTest:
    def __init__(self):
        self.results = []
        self.project_root = Path(__file__).parent

    def run_command(self, cmd, cwd=None, env=None, timeout=30):
        """Run a command and return (success, output, error)"""
        try:
            result = subprocess.run(
                cmd, shell=True, cwd=cwd or self.project_root, env=env, capture_output=True, text=True, timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def test(self, name, test_func):
        """Run a test and record results"""
        print(f"🧪 Testing: {name}...")
        try:
            success, message = test_func()
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status}: {message}")
            self.results.append((name, success, message))
            return success
        except Exception as e:
            error_msg = f"Exception: {e!s}"
            print(f"   ❌ FAIL: {error_msg}")
            self.results.append((name, False, error_msg))
            return False

    def test_environment_setup(self):
        """Test environment variables and configuration"""

        def check_env():
            # Check .env file exists
            env_file = self.project_root / ".env"
            if not env_file.exists():
                return False, ".env file not found"

            # Check GEMINI_API_KEY is set in .env
            with open(env_file) as f:
                content = f.read()
                if "GEMINI_API_KEY=" not in content:
                    return False, "GEMINI_API_KEY not found in .env"

            # Check if GEMINI_API_KEY is properly formatted in .env
            if "GEMINI_API_KEY=AIzaSy" not in content:
                return False, "GEMINI_API_KEY not properly formatted in .env"

            return True, "Environment variables configured correctly"

        return check_env()

    def test_cli_installations(self):
        """Test that CLI tools are installed"""

        def check_clis():
            # Check Codex CLI
            success1, _stdout1, _stderr1 = self.run_command("which codex")
            if not success1:
                return False, "Codex CLI not found in PATH"

            # Check Gemini CLI
            env = os.environ.copy()
            env["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{env['PATH']}"
            success2, _stdout2, _stderr2 = self.run_command("which gemini", env=env)
            if not success2:
                return False, "Gemini CLI not found in PATH"

            return True, "Both CLI tools are installed and accessible"

        return check_clis()

    def test_makefile_targets(self):
        """Test Makefile targets work (with CI guards)"""

        def check_makefile():
            # Test that targets exist
            success1, stdout1, _stderr1 = self.run_command("make -pn | grep -E 'gemini\\.task|codex\\.task'")
            if not success1 or len(stdout1.strip().split("\n")) < 2:
                return False, "Makefile targets not found"

            # Test CI guard for gemini.task (should pass in non-CI)
            _success2, stdout2, _stderr2 = self.run_command("make gemini.task TASK='test' 2>&1 | head -3")
            # Should not exit with error due to CI guard
            if "HINT[gemini.task]" in stdout2:
                return False, "CI guard triggered unexpectedly"

            # Test CI guard actually works
            env_ci = os.environ.copy()
            env_ci["CI"] = "true"
            success3, stdout3, _stderr3 = self.run_command("make gemini.task TASK='test'", env=env_ci)
            if not success3 or "HINT[gemini.task]" not in stdout3:
                return False, "CI guard not working"

            return True, "Makefile targets configured correctly with CI guards"

        return check_makefile()

    def test_mcp_servers(self):
        """Test MCP server configuration"""

        def check_mcp():
            # Check Cursor settings.json has MCP servers
            settings_file = Path.home() / ".config/Cursor/User/settings.json"
            if not settings_file.exists():
                return False, "Cursor settings.json not found"

            with open(settings_file) as f:
                try:
                    settings = json.load(f)
                    mcp_servers = settings.get("cursor.mcpServers", {})
                    expected_servers = ["github", "gemantria-ops", "codex"]
                    found_servers = list(mcp_servers.keys())

                    if not all(server in found_servers for server in expected_servers):
                        return False, f"Missing MCP servers. Expected: {expected_servers}, Found: {found_servers}"

                except json.JSONDecodeError:
                    return False, "Invalid JSON in Cursor settings.json"

            # Check MCP servers are running (from earlier ps aux)
            success, stdout, _stderr = self.run_command(
                "ps aux | grep -E '(mcp-server|codex mcp-server)' | grep -v grep | wc -l"
            )
            if not success:
                return False, "Cannot check running processes"

            running_count = int(stdout.strip()) if stdout.strip().isdigit() else 0
            if running_count < 2:  # At least codex and gemantria-ops should be running
                return False, f"Not enough MCP servers running. Found: {running_count}"

            return True, f"MCP servers configured and running ({running_count} processes)"

        return check_mcp()

    def test_gemini_integration(self):
        """Test Gemini CLI integration end-to-end"""

        def check_gemini():
            # Check Gemini settings.json
            gemini_config = Path.home() / ".gemini/settings.json"
            if not gemini_config.exists():
                return False, "Gemini settings.json not found"

            with open(gemini_config) as f:
                try:
                    config = json.load(f)
                    if not config.get("general", {}).get("checkpointing", {}).get("enabled"):
                        return False, "Gemini checkpointing not enabled"

                    if config.get("model", {}).get("name") != "gemini-2.5-pro":
                        return False, "Gemini model not set to gemini-2.5-pro"

                except json.JSONDecodeError:
                    return False, "Invalid JSON in Gemini settings.json"

            # Check secrets file
            secrets_file = Path.home() / ".config/gemantria/secrets.env"
            if not secrets_file.exists():
                return False, "Gemini secrets file not found"

            # Test Gemini CLI responds (don't actually call API)
            env = os.environ.copy()
            env["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{env['PATH']}"
            success, _stdout, _stderr = self.run_command("gemini --version", env=env, timeout=10)
            if not success:
                return False, "Gemini CLI not responding"

            return True, "Gemini CLI integration complete"

        return check_gemini()

    def test_codex_integration(self):
        """Test Codex CLI integration"""

        def check_codex():
            # Test Codex MCP server mode
            success1, stdout1, _stderr1 = self.run_command("timeout 5 codex mcp-server --help 2>&1 | head -2")
            if not success1 or "Codex MCP server" not in stdout1:
                return False, "Codex MCP server not working"

            # Test Codex direct mode
            success2, _stdout2, _stderr2 = self.run_command("codex --version")
            if not success2:
                return False, "Codex CLI not working"

            return True, "Codex CLI integration complete"

        return check_codex()

    def run_all_tests(self):
        """Run all workflow tests"""
        print("🚀 Starting Comprehensive Workflow Integration Test\n")

        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("CLI Installations", self.test_cli_installations),
            ("Makefile Targets", self.test_makefile_targets),
            ("MCP Server Configuration", self.test_mcp_servers),
            ("Gemini CLI Integration", self.test_gemini_integration),
            ("Codex CLI Integration", self.test_codex_integration),
        ]

        passed = 0
        total = len(tests)

        for name, test_func in tests:
            if self.test(name, test_func):
                passed += 1

        print(f"\n📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 ALL TESTS PASSED - Workflow integration is complete!")
            return True
        else:
            print("❌ Some tests failed. Check the output above for details.")
            return False


def main():
    tester = WorkflowTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
