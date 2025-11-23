#!/usr/bin/env python3
"""
PLAN-072 M3: MCP Status Cards Generator

Generates JSON status cards for E21-E25 proofs to feed Atlas dashboards.
Outputs to share/atlas/control_plane/mcp_status_cards.json.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARE_ATLAS = ROOT / "share" / "atlas" / "control_plane"
SHARE_MCP = ROOT / "share" / "mcp"
OUTPUT_PATH = SHARE_ATLAS / "mcp_status_cards.json"

# Proof file paths
PROOF_FILES = {
    "e21_por": SHARE_MCP / "por_proof.json",
    "e22_schema": SHARE_MCP / "schema_proof.json",
    "e23_gatekeeper": SHARE_MCP / "gatekeeper_proof.json",
    "e24_tagproof": SHARE_MCP / "tagproof_proof.json",
    "e25_bundle": SHARE_MCP / "bundle_proof.json",
}


def load_proof(path: Path) -> dict | None:
    """Load a proof JSON file, returning None if missing or invalid."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def generate_status_card(name: str, proof: dict | None) -> dict:
    """Generate a status card from a proof."""
    if proof is None:
        return {
            "name": name,
            "status": "unknown",
            "ok": False,
            "label": f"{name.upper()}: Missing",
            "color": "grey",
            "icon": "status-offline",
            "details": {"error": "proof file missing"},
        }

    ok = proof.get("ok", False)
    method = proof.get("method", "unknown")

    # Determine status and styling
    if ok:
        status = "ok"
        color = "green"
        icon = "status-healthy"
        label = f"{name.upper()}: OK"
    else:
        status = "failed"
        color = "red"
        icon = "status-error"
        label = f"{name.upper()}: Failed"

    # Extract relevant details
    details: dict = {"method": method}
    if "generated_at" in proof:
        details["generated_at"] = proof["generated_at"]

    # Add proof-specific details
    if name == "e21_por":
        details["steps_count"] = proof.get("steps_count", 0)
        details["all_steps_ok"] = proof.get("all_steps_ok", False)
    elif name == "e22_schema":
        details["tables_count"] = proof.get("tables_count", 0)
        details["schema"] = proof.get("schema", "unknown")
    elif name == "e23_gatekeeper":
        details["violation_codes_count"] = proof.get("violation_codes_count", 0)
        details["all_covered"] = proof.get("all_covered", False)
    elif name == "e24_tagproof":
        details["components_count"] = proof.get("components_count", 0)
        details["required_present"] = proof.get("required_present", False)
        details["mode"] = proof.get("mode", "unknown")
    elif name == "e25_bundle":
        details["proofs_count"] = proof.get("proofs_count", 0)
        details["all_ok"] = proof.get("all_ok", False)

    return {
        "name": name,
        "status": status,
        "ok": ok,
        "label": label,
        "color": color,
        "icon": icon,
        "details": details,
    }


def main() -> int:
    """Generate MCP status cards JSON."""
    SHARE_ATLAS.mkdir(parents=True, exist_ok=True)

    cards: dict[str, dict] = {}
    all_ok = True

    # Generate cards for each proof
    for name, path in PROOF_FILES.items():
        proof = load_proof(path)
        card = generate_status_card(name, proof)
        cards[name] = card
        if not card["ok"]:
            all_ok = False

    # Create output structure
    output = {
        "schema": "mcp_status_cards_v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "ok": all_ok,
        "cards": cards,
        "summary": {
            "total_cards": len(cards),
            "ok_count": sum(1 for c in cards.values() if c["ok"]),
            "failed_count": sum(1 for c in cards.values() if not c["ok"]),
        },
    }

    # Write output
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Generated MCP status cards: {OUTPUT_PATH}")
    print(json.dumps(output, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
