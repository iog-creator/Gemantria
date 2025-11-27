#!/usr/bin/env python3
"""
Test Granite 4.0 Model with pmagent System

Simulates how Granite would use pmagent to:
1. Find documentation
2. Query knowledge base
3. Use registry commands
4. Answer questions

This validates that the system is usable by Granite models.
"""

import subprocess
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Install with: pip install requests")
    sys.exit(1)


def call_granite(prompt: str, system: str | None = None) -> str:
    """Call Granite 4.0 via Ollama API."""
    url = "http://127.0.0.1:11434/api/generate"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "granite4:tiny-h",
        "prompt": prompt,
        "system": system or "You are a helpful AI assistant.",
        "stream": False,
        "options": {
            "temperature": 0.0,
            "max_tokens": 512,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except requests.exceptions.RequestException as e:
        return f"ERROR: {e}"


def run_pmagent_command(cmd: list[str]) -> tuple[str, int]:
    """Run a pmagent command and return output."""
    try:
        result = subprocess.run(
            ["pmagent"] + cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out", 1
    except Exception as e:
        return f"ERROR: {e}", 1


def test_scenario(name: str, prompt: str, system: str | None = None):
    """Test a scenario with Granite."""
    print(f"\n{'=' * 60}")
    print(f"TEST: {name}")
    print(f"{'=' * 60}")
    print(f"\nPrompt to Granite:\n{prompt}\n")

    response = call_granite(prompt, system)
    print(f"\nGranite Response:\n{response}\n")

    # Check if response suggests using pmagent
    if "pmagent" in response.lower():
        print("✓ Granite suggested using pmagent")
    else:
        print("⚠ Granite did not mention pmagent")

    return response


def main():
    """Run Granite tests with pmagent."""
    print("Granite 4.0 Model + pmagent Integration Test")
    print("=" * 60)

    # Test 1: Find documentation about SVG icons
    system1 = """You are a project manager AI. When you need to find documentation, 
use pmagent commands like 'pmagent ask query' or 'pmagent kb registry list'.
Always use the tools available rather than guessing."""

    prompt1 = """I need to find documentation about SVG icon sizing requirements. 
What pmagent command should I use, and what would be a good query?"""

    response1 = test_scenario("Finding SVG Icon Documentation", prompt1, system1)

    # Test 2: Query the knowledge base
    print("\n" + "=" * 60)
    print("EXECUTING: pmagent ask query 'SVG icon sizing requirements'")
    print("=" * 60)
    output, _code = run_pmagent_command(["ask", "query", "SVG icon sizing requirements", "--limit", "3"])
    print(output)

    # Test 3: List KB registry
    print("\n" + "=" * 60)
    print("EXECUTING: pmagent kb registry list --limit 5")
    print("=" * 60)
    output, _code = run_pmagent_command(["kb", "registry", "list", "--limit", "5"])
    print(output[:500] + "..." if len(output) > 500 else output)

    # Test 4: Ask Granite to use pmagent to answer a question
    system2 = """You are a project manager AI. You have access to pmagent commands.
When asked a question, you should:
1. Use 'pmagent ask query' to search for relevant documentation
2. Use 'pmagent kb registry list' to see what documents are available
3. Use 'pmagent ask docs' to get AI-generated answers from documentation
Provide the exact commands to run."""

    prompt2 = """How do I fix SVG icons that are rendering too large in the UI?
What pmagent commands should I run to find this information?"""

    response2 = test_scenario("Using pmagent to Answer Questions", prompt2, system2)

    # Test 5: Execute the suggested commands
    if "ask query" in response2.lower():
        print("\n" + "=" * 60)
        print("EXECUTING: pmagent ask query 'SVG icons rendering too large'")
        print("=" * 60)
        output, _code = run_pmagent_command(["ask", "query", "SVG icons rendering too large", "--limit", "3"])
        print(output)

    # Test 6: Test error handling
    print("\n" + "=" * 60)
    print("TEST: Error Handling")
    print("=" * 60)
    print("\nTesting with a query that might not find results...")
    output, _code = run_pmagent_command(["ask", "query", "xyzabc123nonexistent", "--limit", "3"])
    print(output)

    if "Suggestions:" in output or "threshold" in output.lower():
        print("\n✓ Error messages are helpful")
    else:
        print("\n⚠ Error messages could be improved")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("\nTests completed. Review output above to verify:")
    print("1. Granite can understand how to use pmagent")
    print("2. pmagent commands work correctly")
    print("3. Search finds relevant documentation")
    print("4. Error messages are helpful")
    print("5. System is usable by Granite models")


if __name__ == "__main__":
    main()
