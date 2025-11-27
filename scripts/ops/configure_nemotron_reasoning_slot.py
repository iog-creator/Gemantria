#!/usr/bin/env python3
"""
Configure Nemotron Nano 12B v2 as the Planning Lane reasoning specialist.

Writes env defaults to .env and runs smoke test.
"""

from __future__ import annotations

import sys
from pathlib import Path


def write_env_defaults(provider: str = "ollama") -> None:
    """Write Nemotron env defaults to .env file.

    Args:
        provider: "ollama" or "lmstudio"
    """
    env_path = Path(".env")
    env_local_path = Path(".env.local")

    # Prefer .env.local if it exists
    target_path = env_local_path if env_local_path.exists() else env_path

    # Read existing content
    existing_content = ""
    if target_path.exists():
        existing_content = target_path.read_text()

    # Determine model ID based on provider
    if provider == "ollama":
        planning_provider = "ollama"
        planning_model = "nvidia/nemotron-nano-12b-v2"
    else:  # lmstudio
        planning_provider = "lmstudio"
        planning_model = "nemotron-nano-12b-v2"

    # Update or add PLANNING_PROVIDER and PLANNING_MODEL
    lines = existing_content.split("\n")
    updated = False
    planning_provider_set = False
    planning_model_set = False

    for i, line in enumerate(lines):
        if line.startswith("PLANNING_PROVIDER="):
            lines[i] = f"PLANNING_PROVIDER={planning_provider}"
            planning_provider_set = True
            updated = True
        elif line.startswith("PLANNING_MODEL="):
            lines[i] = f"PLANNING_MODEL={planning_model}"
            planning_model_set = True
            updated = True

    # Add if not present
    if not planning_provider_set:
        lines.append(f"PLANNING_PROVIDER={planning_provider}")
        updated = True
    if not planning_model_set:
        lines.append(f"PLANNING_MODEL={planning_model}")
        updated = True

    # Add LMSTUDIO_BASE_URL if using LM Studio
    if provider == "lmstudio":
        lmstudio_base_url_set = False
        for i, line in enumerate(lines):
            if line.startswith("LMSTUDIO_BASE_URL="):
                lines[i] = "LMSTUDIO_BASE_URL=http://localhost:1234/v1"
                lmstudio_base_url_set = True
                updated = True
        if not lmstudio_base_url_set:
            lines.append("LMSTUDIO_BASE_URL=http://localhost:1234/v1")
            updated = True

    if updated:
        target_path.write_text("\n".join(lines))
        print(f"✅ Updated {target_path} with Nemotron configuration")
    else:
        print(f"[INFO] {target_path} already has Nemotron configuration")


def smoke_test() -> bool:
    """Run smoke test to verify Nemotron planning lane works.

    Returns:
        True if smoke test passes
    """
    try:
        from agentpm.adapters.planning import run_planning_prompt

        prompt = "Plan three high-level steps to verify the Nemotron planning lane."
        result = run_planning_prompt(prompt)

        if result.ok and result.response:
            print("✅ Nemotron planning smoke test passed")
            print(f"Response preview: {result.response[:400]}...")
            return True
        else:
            print(f"❌ Nemotron planning smoke test failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Nemotron planning smoke test error: {e}")
        return False


def main() -> int:
    """Main configuration script."""
    import argparse

    parser = argparse.ArgumentParser(description="Configure Nemotron Planning Lane")
    parser.add_argument(
        "--provider",
        choices=["ollama", "lmstudio"],
        default="ollama",
        help="Provider for Nemotron (default: ollama)",
    )
    parser.add_argument("--no-smoke-test", action="store_true", help="Skip smoke test")

    args = parser.parse_args()

    print(f"🔧 Configuring Nemotron Planning Lane with provider: {args.provider}")
    write_env_defaults(provider=args.provider)

    if not args.no_smoke_test:
        print("🧪 Running smoke test...")
        if not smoke_test():
            print("⚠️  Smoke test failed - check Nemotron model is available")
            return 1

    print("✅ Nemotron Planning Lane configuration complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
