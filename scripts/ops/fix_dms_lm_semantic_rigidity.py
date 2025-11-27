#!/usr/bin/env python3
"""
OPS Script: Fix DMS LM Semantic Rigidity (BUG-5)
================================================
Addresses Coherence Agent rigidity by:
1. Refining the system prompt to explicitly exclude semantic variations.
2. Ensuring `model_slot="local_agent"` is used for faster/better inference.

Usage: python scripts/ops/fix_dms_lm_semantic_rigidity.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AGENT_FILE = REPO_ROOT / "agentpm/dms/coherence_agent.py"

NEW_SYSTEM_PROMPT = 'system_prompt="""You are a documentation coherence validator.\\nAnalyze the two text snippets for LOGICAL contradictions.\\n- Semantic variations (e.g. "DSN" vs "connection string") are NOT contradictions.\\n- Different phrasing of the same fact is NOT a contradiction.\\n- Only flag direct factual conflicts (e.g. "Port 5432" vs "Port 8000").\\nProvide JSON responses only.""",'


def fix_coherence_agent():
    if not AGENT_FILE.exists():
        print(f"❌ Error: {AGENT_FILE} not found")
        return False

    content = AGENT_FILE.read_text()

    # 1. Check/Fix Model Slot
    if 'model_slot="local_agent"' in content:
        print(f"✓ {AGENT_FILE.name} already uses 'local_agent' slot")
    else:
        print(f"🛠 Fixing {AGENT_FILE.name}: Adding model_slot='local_agent'")
        # This is a bit fragile with string replacement, but we know the context from previous edits
        # We look for the generate_text call
        if "model_slot=" not in content and "generate_text(" in content:
            # Try to insert it after system_prompt line
            content = content.replace(
                'system_prompt="You are a documentation coherence validator. Provide JSON responses only.",',
                'system_prompt="You are a documentation coherence validator. Provide JSON responses only.",\n            model_slot="local_agent",',
            )
            AGENT_FILE.write_text(content)
            print("  -> Applied model_slot fix")
            # Reload content for next step
            content = AGENT_FILE.read_text()

    # 2. Check/Fix System Prompt
    if "Semantic variations" in content:
        print(f"✓ {AGENT_FILE.name} already has refined system prompt")
        return True

    print(f"🛠 Fixing {AGENT_FILE.name}: Refining system prompt")
    # Replace the old simple prompt with the new detailed one
    old_prompt = 'system_prompt="You are a documentation coherence validator. Provide JSON responses only.",'
    if old_prompt in content:
        new_content = content.replace(old_prompt, NEW_SYSTEM_PROMPT)
        AGENT_FILE.write_text(new_content)
        print("  -> Applied system prompt refinement")
        return True

    # Fallback: maybe it has the model_slot line after it now?
    # Let's try to find the block and replace it carefully
    # Or just warn if we can't find the exact string
    print(f"⚠ Could not find exact system prompt string to replace in {AGENT_FILE.name}")
    return False


def main():
    print("OPS Script: Fix DMS LM Semantic Rigidity (BUG-5)")
    print("================================================")

    fixed = fix_coherence_agent()

    if fixed:
        print("\n✓ SUCCESS: Coherence Agent logic refined.")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Could not apply fixes automatically.")
        sys.exit(1)


if __name__ == "__main__":
    main()
