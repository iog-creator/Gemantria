#!/usr/bin/env python3
"""
E2E Test: BibleScholar Passage Flow
===================================
End-to-end test for BibleScholar passage retrieval and commentary generation.

Tests:
1. API endpoint /api/bible/passage with DB+LM
2. Verse retrieval from bible_db
3. Commentary generation using theology LM slot
4. Graceful degradation when LM is offline
"""

import argparse
import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

import requests
from agentpm.biblescholar.passage import get_passage_and_commentary


def test_api_endpoint(reference: str, use_lm: bool = True, base_url: str = "http://localhost:8000"):
    """Test the API endpoint directly."""
    print(f"\n{'=' * 70}")
    print(f"Testing API Endpoint: {base_url}/api/bible/passage")
    print(f"{'=' * 70}")
    print(f"Reference: {reference}")
    print(f"Use LM: {use_lm}")

    try:
        url = f"{base_url}/api/bible/passage"
        params = {"reference": reference, "use_lm": use_lm}
        response = requests.get(url, params=params, timeout=30)

        print(f"\nHTTP Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n✓ API Response received:")
            print(f"  Reference: {data.get('reference', 'N/A')}")
            print(f"  Verses: {len(data.get('verses', []))}")
            print(f"  Commentary source: {data.get('commentary', {}).get('source', 'N/A')}")
            if data.get("errors"):
                print(f"  ⚠ Errors: {data.get('errors')}")

            # Verify structure
            assert "reference" in data, "Missing 'reference' field"
            assert "verses" in data, "Missing 'verses' field"
            assert "commentary" in data, "Missing 'commentary' field"

            if data.get("verses"):
                print("\n✓ First verse:")
                verse = data["verses"][0]
                print(f"  Book: {verse.get('book', 'N/A')}")
                print(f"  Chapter: {verse.get('chapter', 'N/A')}")
                print(f"  Verse: {verse.get('verse', 'N/A')}")
                print(f"  Text: {verse.get('text', 'N/A')[:100]}...")

            commentary = data.get("commentary", {})
            print("\n✓ Commentary:")
            print(f"  Source: {commentary.get('source', 'N/A')}")
            print(f"  Text: {commentary.get('text', 'N/A')[:200]}...")

            return True, data
        else:
            print(f"\n✗ API Error: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return False, None

    except requests.exceptions.ConnectionError:
        print(f"\n✗ Connection Error: API server not running at {base_url}")
        print("  Start server with: python3 -m uvicorn src.services.api_server:app --host 0.0.0.0 --port 8000")
        return False, None
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False, None


def test_direct_function(reference: str, use_lm: bool = True):
    """Test the passage function directly (bypassing API)."""
    print(f"\n{'=' * 70}")
    print("Testing Direct Function: get_passage_and_commentary()")
    print(f"{'=' * 70}")
    print(f"Reference: {reference}")
    print(f"Use LM: {use_lm}")

    try:
        result = get_passage_and_commentary(reference, use_lm=use_lm)

        print("\n✓ Function call successful:")
        print(f"  Reference: {result.get('reference', 'N/A')}")
        print(f"  Text: {result.get('text', 'N/A')[:100]}...")
        print(f"  Commentary source: {result.get('commentary', {}).get('source', 'N/A')}")
        print(f"  Commentary text: {result.get('commentary', {}).get('text', 'N/A')[:200]}...")

        # Verify structure
        assert "reference" in result, "Missing 'reference' field"
        assert "text" in result, "Missing 'text' field"
        assert "commentary" in result, "Missing 'commentary' field"

        return True, result

    except RuntimeError as e:
        print(f"\n⚠ LM Unavailable (expected if LM offline): {e}")
        print("  This is expected behavior - function fails-closed when LM unavailable")
        return False, None
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False, None


def main():
    parser = argparse.ArgumentParser(description="E2E test for BibleScholar passage flow")
    parser.add_argument("--reference", default="John 3:16", help="Bible reference (default: John 3:16)")
    parser.add_argument("--use-lm", action="store_true", default=True, help="Use LM commentary (default: True)")
    parser.add_argument("--no-lm", dest="use_lm", action="store_false", help="Disable LM commentary")
    parser.add_argument("--api-only", action="store_true", help="Test API endpoint only")
    parser.add_argument("--function-only", action="store_true", help="Test function directly only")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")

    args = parser.parse_args()

    print("=" * 70)
    print("BibleScholar Passage E2E Test")
    print("=" * 70)

    results = {}

    # Test API endpoint
    if not args.function_only:
        api_ok, api_data = test_api_endpoint(args.reference, args.use_lm, args.base_url)
        results["api"] = {"ok": api_ok, "data": api_data}

    # Test direct function
    if not args.api_only:
        func_ok, func_data = test_direct_function(args.reference, args.use_lm)
        results["function"] = {"ok": func_ok, "data": func_data}

    # Summary
    print(f"\n{'=' * 70}")
    print("E2E Test Summary")
    print(f"{'=' * 70}")

    all_ok = True
    if "api" in results:
        status = "✓ PASS" if results["api"]["ok"] else "✗ FAIL"
        print(f"API Endpoint: {status}")
        all_ok = all_ok and results["api"]["ok"]

    if "function" in results:
        status = "✓ PASS" if results["function"]["ok"] else "✗ FAIL"
        print(f"Direct Function: {status}")
        all_ok = all_ok and results["function"]["ok"]

    if all_ok:
        print("\n✓ All E2E tests passed")
        return 0
    else:
        print("\n✗ Some E2E tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
