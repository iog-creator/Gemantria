# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Audit script for LM Studio model quantization and residency.

Checks which models are loaded and their quantization levels.
"""

import requests


def audit_model_on_port(port: int, name: str) -> dict[str, str]:
    """Audit a model server on a specific port."""
    try:
        response = requests.get(f"http://127.0.0.1:{port}/v1/models", timeout=5)
        response.raise_for_status()
        models = response.json().get("data", [])

        if models:
            model_id = models[0].get("id", "unknown")
            # LM Studio doesn't expose quant info via API, so we note it's loaded
            quant = "LOADED" if model_id != "unknown" else "UNKNOWN"
            return {"name": model_id, "quant": quant, "status": "running"}
        else:
            return {"name": "none", "quant": "none", "status": "no_models"}
    except Exception as e:
        return {
            "name": "error",
            "quant": "error",
            "status": f"connection_failed: {e!s}",
        }


def main():
    """Main audit function."""
    print("LM Studio Model Audit")
    print("=" * 50)

    servers = [(9994, "embed"), (9991, "llm"), (9993, "critic")]

    for port, role in servers:
        result = audit_model_on_port(port, role)
        print(f"{role:8} {result['name']:30} {result['quant']:8} {result['status']}")


if __name__ == "__main__":
    main()
