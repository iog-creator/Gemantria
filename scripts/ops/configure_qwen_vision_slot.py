#!/usr/bin/env python3
"""
Configure Qwen3-VL-4B as the Vision Lane multimodal specialist.

Writes env defaults to .env and verifies configuration.
"""

from __future__ import annotations

import sys
from pathlib import Path


def write_env_defaults() -> None:
    """Write Qwen3-VL-4B env defaults to .env file."""
    env_path = Path(".env")
    env_local_path = Path(".env.local")

    # Prefer .env.local if it exists
    target_path = env_local_path if env_local_path.exists() else env_path

    # Read existing content
    existing_content = ""
    if target_path.exists():
        existing_content = target_path.read_text()

    # Update or add VISION_PROVIDER and VISION_MODEL
    lines = existing_content.split("\n")
    updated = False
    vision_provider_set = False
    vision_model_set = False
    lmstudio_base_url_set = False

    for i, line in enumerate(lines):
        if line.startswith("VISION_PROVIDER="):
            lines[i] = "VISION_PROVIDER=lmstudio"
            vision_provider_set = True
            updated = True
        elif line.startswith("VISION_MODEL="):
            lines[i] = "VISION_MODEL=qwen3-vl-4b"
            vision_model_set = True
            updated = True
        elif line.startswith("LMSTUDIO_BASE_URL="):
            lines[i] = "LMSTUDIO_BASE_URL=http://localhost:1234/v1"
            lmstudio_base_url_set = True
            updated = True

    # Add if not present
    if not vision_provider_set:
        lines.append("VISION_PROVIDER=lmstudio")
        updated = True
    if not vision_model_set:
        lines.append("VISION_MODEL=qwen3-vl-4b")
        updated = True
    if not lmstudio_base_url_set:
        lines.append("LMSTUDIO_BASE_URL=http://localhost:1234/v1")
        updated = True

    if updated:
        target_path.write_text("\n".join(lines))
        print(f"✅ Updated {target_path} with Qwen3-VL-4B configuration")
    else:
        print(f"[INFO] {target_path} already has Qwen3-VL-4B configuration")


def verify_config() -> bool:
    """Verify Qwen3-VL-4B configuration is correct.

    Returns:
        True if configuration is valid
    """
    try:
        from scripts.config.env import get_lm_model_config

        cfg = get_lm_model_config()
        vision_provider = cfg.get("vision_provider", "").strip().lower()
        vision_model = cfg.get("vision_model", "").strip()

        if vision_provider != "lmstudio":
            print(f"⚠️  VISION_PROVIDER is {vision_provider}, expected 'lmstudio'")
            return False

        if not vision_model:
            print("❌ VISION_MODEL is not set")
            return False

        print(f"✅ Qwen3-VL-4B configuration verified: provider={vision_provider}, model={vision_model}")
        return True
    except Exception as e:
        print(f"❌ Configuration verification error: {e}")
        return False


def main() -> int:
    """Main configuration script."""
    print("🔧 Configuring Qwen3-VL-4B Vision Lane")
    write_env_defaults()

    print("🔍 Verifying configuration...")
    if not verify_config():
        print("⚠️  Configuration verification failed")
        return 1

    print("✅ Qwen3-VL-4B Vision Lane configuration complete")
    print()
    print("Next steps:")
    print("  1. Ensure Qwen3-VL-4B model is loaded in LM Studio")
    print("  2. Verify LM Studio is running on http://localhost:1234")
    print("  3. Test vision endpoint: curl -X POST http://localhost:8000/api/inference/vision ...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
