#!/usr/bin/env python3
"""Test script for Ollama Monitor endpoint."""

import sys
import requests

API_BASE = "http://localhost:8000"


def test_monitor_endpoint():
    """Test the /api/ollama/monitor endpoint."""
    print("Testing Ollama Monitor endpoint...")
    print(f"  URL: {API_BASE}/api/ollama/monitor")

    try:
        response = requests.get(f"{API_BASE}/api/ollama/monitor", timeout=5)
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("  ✅ Success!")
            print(f"  Keys: {list(data.keys())}")
            print(f"  Active requests: {len(data.get('activeRequests', []))}")
            print(f"  Recent requests: {len(data.get('recentRequests', []))}")
            print(f"  Last updated: {data.get('lastUpdated', 'N/A')}")
            return True
        else:
            print(f"  ❌ Error: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False

    except requests.exceptions.ConnectionError:
        print("  ❌ Connection error: API server not running on port 8000")
        print("  Start it with: python3 -m uvicorn src.services.api_server:app --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_monitor_endpoint()
    sys.exit(0 if success else 1)
