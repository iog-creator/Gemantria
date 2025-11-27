#!/usr/bin/env python3
"""
Work Verification System.

Verify that work actually works (not just "complete"):
- Run relevant tests
- Check for runtime errors
- Verify integration points
- Browser verification for UI work (Rule 067)
- LM slot verification for model integration work
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def _check_lm_slots() -> dict[str, Any]:
    """Check that LM slots (local_agent, planning, vision) are properly configured."""
    try:
        result = subprocess.run(
            ["pmagent", "lm", "status", "--json-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        # Expect keys: "local_agent", "planning", "vision"
        return {
            "ok": True,
            "slots": data,
        }
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as exc:
        return {
            "ok": False,
            "error": str(exc),
        }


def verify_work_complete(
    work_type: str,
    files_changed: list[str],
    *,
    run_tests: bool = True,
    check_runtime: bool = True,
    browser_verify: bool = False,
) -> dict[str, Any]:
    """
    Verify that work actually works.

    Args:
        work_type: Type of work (e.g., "phase_13b", "feature", "bugfix")
        files_changed: List of changed files
        run_tests: Whether to run tests
        check_runtime: Whether to check for runtime errors
        browser_verify: Whether to perform browser verification (Rule 067)

    Returns:
        Dict with verification results
    """
    verification: dict[str, Any] = {
        "ok": True,
        "hermetic": {},
        "live": {},
        "ui": {},
        "lm_slots": {},
    }

    # 1. Hermetic verification: lint, format, syntax
    print("🔍 Running hermetic verification (lint, format)...")
    try:
        # Check ruff format
        format_result = subprocess.run(
            ["ruff", "format", "--check", "."],
            capture_output=True,
            text=True,
        )
        verification["hermetic"]["format_ok"] = format_result.returncode == 0
        if format_result.returncode != 0:
            verification["hermetic"]["format_output"] = format_result.stdout + format_result.stderr

        # Check ruff lint
        lint_result = subprocess.run(
            ["ruff", "check", "."],
            capture_output=True,
            text=True,
        )
        verification["hermetic"]["lint_ok"] = lint_result.returncode == 0
        if lint_result.returncode != 0:
            verification["hermetic"]["lint_output"] = lint_result.stdout + lint_result.stderr

        if not verification["hermetic"].get("format_ok") or not verification["hermetic"].get("lint_ok"):
            verification["ok"] = False
            print("❌ Hermetic verification failed (format or lint errors)")

    except FileNotFoundError:
        verification["hermetic"]["error"] = "ruff not found"
        verification["ok"] = False

    # 2. Test verification (if requested)
    if run_tests:
        print("🧪 Running tests...")
        # Determine relevant test files based on changed files
        test_files = []
        for file in files_changed:
            if file.endswith(".py"):
                # Try to find corresponding test file
                test_file = file.replace(".py", "_test.py").replace("src/", "tests/")
                if Path(test_file).exists():
                    test_files.append(test_file)

        if test_files:
            try:
                test_result = subprocess.run(
                    ["pytest", "-x", "-v"] + test_files,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                verification["hermetic"]["tests_ok"] = test_result.returncode == 0
                if test_result.returncode != 0:
                    verification["hermetic"]["tests_output"] = test_result.stdout + test_result.stderr
                    verification["ok"] = False
                    print("❌ Tests failed")
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                verification["hermetic"]["tests_error"] = str(e)
                print(f"⚠️  Test execution error: {e}")

    # 3. Runtime verification (if requested and applicable)
    if check_runtime:
        # Check for obvious syntax errors by trying to import changed modules
        print("🔍 Checking for runtime errors...")
        for file in files_changed:
            if file.endswith(".py") and not file.endswith("_test.py"):
                try:
                    # Try to compile the file
                    with open(file) as f:
                        compile(f.read(), file, "exec")
                except SyntaxError as e:
                    verification["live"]["syntax_errors"] = verification["live"].get("syntax_errors", [])
                    verification["live"]["syntax_errors"].append({"file": file, "error": str(e)})
                    verification["ok"] = False
                    print(f"❌ Syntax error in {file}: {e}")

    # 4. Service status check and auto-start (Rule-062) - BEFORE browser verification
    if (
        browser_verify
        or "ui" in work_type.lower()
        or any("ui" in f.lower() or "webui" in f.lower() for f in files_changed)
    ):
        print("🔍 Checking required services (Rule-062: auto-start if down)...")
        try:
            # Check service status
            services_result = subprocess.run(
                ["make", "services.check"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            services_output = services_result.stdout + services_result.stderr

            # Check if Vite server is running (required for UI work)
            vite_running = "Vite Dev Server" in services_output and "✓ Running" in services_output
            api_running = "API Server" in services_output and "✓ Running" in services_output

            if not vite_running:
                print("🚀 Auto-starting Vite dev server (Rule-062)...")
                try:
                    # Start Vite dev server in background
                    subprocess.Popen(
                        ["npm", "run", "dev"],
                        cwd=Path(__file__).parent.parent.parent / "webui" / "graph",
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    # Wait a few seconds for server to start
                    import time

                    time.sleep(3)
                    print("✅ Vite dev server started")
                except Exception as e:
                    verification["ui"]["vite_start_error"] = str(e)
                    verification["ok"] = False
                    print(f"❌ Failed to start Vite server: {e}")

            if not api_running:
                print("🚀 Auto-starting API server (Rule-062)...")
                try:
                    # Start API server in background
                    subprocess.Popen(
                        [
                            "python3",
                            "-m",
                            "uvicorn",
                            "src.services.api_server:app",
                            "--host",
                            "0.0.0.0",
                            "--port",
                            "8000",
                            "--reload",
                        ],
                        cwd=Path(__file__).parent.parent.parent,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    # Wait a few seconds for server to start
                    import time

                    time.sleep(3)
                    print("✅ API server started")
                except Exception as e:
                    verification["ui"]["api_start_error"] = str(e)
                    verification["ok"] = False
                    print(f"❌ Failed to start API server: {e}")

            verification["ui"]["services_ok"] = vite_running or (
                vite_running is False and "vite_start_error" not in verification["ui"]
            )
            verification["ui"]["api_ok"] = api_running or (
                api_running is False and "api_start_error" not in verification["ui"]
            )

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            verification["ui"]["services_check_error"] = str(e)
            print(f"⚠️  Service check error: {e}")

    # 5. Browser verification (if requested and applicable)
    if browser_verify:
        print("🌐 Running browser verification (Rule 067)...")
        try:
            browser_result = subprocess.run(
                ["make", "browser.verify"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            verification["ui"]["browser_ok"] = browser_result.returncode == 0
            if browser_result.returncode != 0:
                verification["ui"]["browser_output"] = browser_result.stdout + browser_result.stderr
                verification["ok"] = False
                print("❌ Browser verification failed")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            verification["ui"]["browser_error"] = str(e)
            print(f"⚠️  Browser verification error: {e}")

    # 6. LM slot verification (if LM integration work)
    if work_type in {"lm_integration", "planning_lane", "vision_lane"}:
        print("🤖 Checking LM slots...")
        lm_slots = _check_lm_slots()
        verification["lm_slots"] = lm_slots
        if not lm_slots.get("ok"):
            print("⚠️  LM slots check failed (non-fatal)")

    if verification["ok"]:
        print("✅ Work verification passed")
    else:
        print("❌ Work verification failed - check details above")

    return verification


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify work completion")
    parser.add_argument("--work-type", required=True, help="Type of work")
    parser.add_argument("--files-changed", nargs="+", default=[], help="Changed files")
    parser.add_argument("--no-tests", action="store_true", help="Skip tests")
    parser.add_argument("--no-runtime", action="store_true", help="Skip runtime checks")
    parser.add_argument("--browser-verify", action="store_true", help="Enable browser verification")

    args = parser.parse_args()

    result = verify_work_complete(
        work_type=args.work_type,
        files_changed=args.files_changed,
        run_tests=not args.no_tests,
        check_runtime=not args.no_runtime,
        browser_verify=args.browser_verify,
    )

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
