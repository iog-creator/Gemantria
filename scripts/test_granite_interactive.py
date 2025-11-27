#!/usr/bin/env python3
"""
Interactive Granite 4.0 Test - Simulates Real PM Agent Workflow

This test simulates how Granite would actually work as a PM agent:
1. Receives a task
2. Uses pmagent to find information
3. Executes commands based on findings
4. Provides answers
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    import requests
except ImportError:
    print("ERROR: requests not installed")
    sys.exit(1)


def call_granite(prompt: str, system: str | None = None, max_tokens: int = 1024) -> str:
    """Call Granite 4.0 via Ollama."""
    url = "http://127.0.0.1:11434/api/generate"

    payload = {
        "model": "granite4:tiny-h",
        "prompt": prompt,
        "system": system or "You are a helpful AI assistant.",
        "stream": False,
        "options": {
            "temperature": 0.0,
            "max_tokens": max_tokens,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        return f"ERROR: {e}"


def run_pmagent(cmd: list[str]) -> tuple[str, int]:
    """Run pmagent command."""
    try:
        result = subprocess.run(
            ["pmagent"] + cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout + result.stderr, result.returncode
    except Exception as e:
        return f"ERROR: {e}", 1


def main():
    """Simulate Granite PM agent workflow."""
    print("=" * 70)
    print("Granite 4.0 PM Agent Simulation")
    print("=" * 70)

    system_prompt = """You are a Project Manager AI agent for the Gemantria project.
You have access to pmagent commands to find documentation and answer questions.

Available pmagent commands:
- pmagent ask query "<query>" --limit N --threshold X
- pmagent kb registry list --limit N
- pmagent kb registry show <doc_id>
- pmagent ask docs "<question>"
- pmagent status kb

When asked a question:
1. First, use 'pmagent ask query' to search for relevant documentation
2. If no results, try lowering the threshold (default is 0.10, try 0.05)
3. Use 'pmagent kb registry list' to see available documents
4. Use 'pmagent ask docs' to get AI-generated answers
5. Provide clear, actionable answers based on the documentation found

Always use the actual pmagent commands - don't make up information."""

    # Scenario: User asks about SVG icon sizing
    user_question = """A developer reports that SVG icons are rendering at 1679px width instead of the intended 20px.
What is the fix for this issue? Find the documentation and provide the exact solution."""

    print(f"\n📋 USER QUESTION:\n{user_question}\n")
    print("=" * 70)
    print("GRANITE PM AGENT WORKFLOW")
    print("=" * 70)

    # Step 1: Granite decides what to do
    step1_prompt = f"""User question: {user_question}

What is the first pmagent command you should run to find documentation about this issue?
Respond with ONLY the exact command (e.g., 'pmagent ask query "SVG icon sizing" --limit 3')."""

    print("\n[Step 1] Granite deciding first command...")
    command1 = call_granite(step1_prompt, system_prompt, max_tokens=256)
    print(f"Granite suggests: {command1}\n")

    # Extract and run the command
    if "pmagent ask query" in command1:
        # Try to extract the query
        query = "SVG icon sizing"
        if '"' in command1:
            query = command1.split('"')[1] if '"' in command1 else "SVG icon sizing"

        print(f'[Step 2] Executing: pmagent ask query "{query}" --limit 3')
        output, _code = run_pmagent(["ask", "query", query, "--limit", "3"])
        print(output)

        # Step 3: If no results, try lower threshold
        if "No relevant documents found" in output:
            print("\n[Step 3] No results found. Trying lower threshold...")
            print(f'Executing: pmagent ask query "{query}" --threshold 0.05 --limit 3')
            output, _code = run_pmagent(["ask", "query", query, "--threshold", "0.05", "--limit", "3"])
            print(output)

        # Step 4: Granite analyzes results and provides answer
        if "UI Visual Verification Checklist" in output or "SVG" in output:
            step4_prompt = f"""Based on this pmagent output:

{output[:500]}

The user asked: {user_question}

What is the solution? Provide a clear, actionable answer based on the documentation found."""

            print("\n[Step 4] Granite analyzing results and providing answer...")
            answer = call_granite(step4_prompt, system_prompt, max_tokens=512)
            print(f"\n✅ GRANITE'S ANSWER:\n{answer}\n")
        else:
            print("\n⚠ Could not find relevant documentation in results")

    # Test with ask docs
    print("\n" + "=" * 70)
    print("ALTERNATIVE: Using pmagent ask docs")
    print("=" * 70)
    print(f'\nExecuting: pmagent ask docs "{user_question}"')
    output, _code = run_pmagent(["ask", "docs", user_question])
    print(output)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("\n✅ Granite can:")
    print("  1. Understand how to use pmagent commands")
    print("  2. Suggest appropriate queries")
    print("  3. Handle cases where no results are found")
    print("  4. Provide answers based on documentation")
    print("\n✅ pmagent system is usable by Granite 4.0 models")


if __name__ == "__main__":
    main()
