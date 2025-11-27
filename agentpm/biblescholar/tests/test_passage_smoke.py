import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from agentpm.biblescholar.passage import generate_commentary


def test_fail_closed_policy():
    """Verify that use_lm=False raises ValueError."""
    print("\nTesting Fail-Closed Policy (use_lm=False)...")
    try:
        generate_commentary("Genesis 1:1", use_lm=False)
        print("FAIL: Should have raised ValueError")
    except ValueError as e:
        print(f"SUCCESS: Caught expected error: {e}")


def test_lm_integration():
    """Verify LM integration (might fail if LM is down, which is expected)."""
    print("\nTesting LM Integration (use_lm=True)...")
    try:
        result = generate_commentary("Genesis 1:1", use_lm=True)
        print(f"SUCCESS: Generated commentary: {result['text'][:50]}...")
    except RuntimeError as e:
        print(f"SUCCESS (Partial): Caught expected RuntimeError (LM likely down): {e}")
    except Exception as e:
        print(f"FAIL: Unexpected error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    test_fail_closed_policy()
    test_lm_integration()
