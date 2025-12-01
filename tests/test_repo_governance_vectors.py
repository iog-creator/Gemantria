"""
Test vectors for pmagent repo commands.

These test vectors validate the repository introspection subsystem per
docs/SSOT/PMAGENT_REPO_INTROSPECTION_PLAN.md and
docs/SSOT/PMAGENT_REPO_ALIGNMENT_GUARD_PLAN.md.

Test vectors are designed to be run manually or in CI to verify:
- Semantic inventory generation
- Reunion plan classification
- Quarantine candidate extraction
- Alignment guard drift detection
"""

from pathlib import Path
import json
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]

# Test Vector Catalog
TEST_VECTORS = {
    "TV-REPO-01": {
        "name": "Semantic Inventory Generation",
        "description": "Verify semantic inventory can scan repo and load DMS data",
        "command": ["python", "-m", "pmagent", "repo", "semantic-inventory"],
        "expected_files": [
            "evidence/repo/repo_semantic_inventory.json",
            "evidence/repo/semantic_inventory_filtered.json",
        ],
        "expected_schema_keys": ["summary", "core_files", "untracked_source_files"],
    },
    "TV-REPO-02": {
        "name": "Reunion Plan Generation",
        "description": "Verify reunion plan can classify integration/quarantine islands",
        "command": ["python", "-m", "pmagent", "repo", "reunion-plan"],
        "expected_files": ["evidence/repo/repo_reunion_plan.json"],
        "expected_schema_keys": ["summary", "dir_labels", "files", "notes"],
    },
    "TV-REPO-03": {
        "name": "Quarantine Candidates Extraction",
        "description": "Verify quarantine candidates can be extracted from reunion plan",
        "command": ["python", "-m", "pmagent", "repo", "quarantine-candidates"],
        "expected_files": ["evidence/repo/repo_quarantine_candidates.json"],
        "expected_schema_keys": ["quarantine_candidates"],
    },
    "TV-REPO-04": {
        "name": "Share Export Flag",
        "description": "Verify --write-share flag creates share exports",
        "command": ["python", "-m", "pmagent", "repo", "semantic-inventory", "--write-share"],
        "expected_files": ["share/exports/repo/semantic_inventory.json"],
    },
    "TV-REPO-05": {
        "name": "Branch Protection Guard",
        "description": "Verify guard-branch blocks work on protected branches",
        "command": ["python", "-m", "pmagent", "repo", "guard-branch"],
        "expected_exit": 0,  # Should pass when NOT on main
    },
    "TV-REPO-06": {
        "name": "Branch Status Check",
        "description": "Verify branch-status shows ahead/behind metrics",
        "command": ["python", "-m", "pmagent", "repo", "branch-status"],
        "expected_exit": 0,
    },
    "TV-REPO-07": {
        "name": "Alignment Guard - Perfect Match",
        "description": "Plan expects X, repo contains X → PASS",
        "command": ["python", "scripts/guards/guard_repo_layer4_alignment.py"],
        "expected_exit": 0,
        "expected_files": ["evidence/repo/guard_layer4_alignment.json  "],
        "validation": lambda data: data["status"] == "pass",
    },
    "TV-REPO-08": {
        "name": "Alignment Guard - Missing Expected",
        "description": "Plan expects X, repo missing X → FAIL (HINT mode)",
        "command": ["python", "scripts/guards/guard_repo_layer4_alignment.py"],
        "expected_exit": 0,  # HINT mode
        "validation": lambda data: "missing_expected_paths" in data,
    },
    "TV-REPO-09": {
        "name": "Alignment Guard - Integration Island Detection",
        "description": "Plan expects scripts/governance, reality has scripts/code_ingest → FAIL",
        "command": ["python", "scripts/guards/guard_repo_layer4_alignment.py"],
        "expected_exit": 0,  # HINT mode
        "validation": lambda data: len(data.get("unexpected_locations", [])) > 0,
    },
    "TV-REPO-10": {
        "name": "Alignment Guard - STRICT Mode",
        "description": "STRICT mode fails on mismatches",
        "command": ["python", "scripts/guards/guard_repo_layer4_alignment.py", "--strict"],
        "expected_exit": 1,  # Should fail in STRICT if mismatches exist
    },
}


def run_test_vector(tv_id: str, tv_spec: dict) -> dict:
    """Run a single test vector and return results."""
    print(f"\n{'=' * 80}")
    print(f"Running {tv_id}: {tv_spec['name']}")
    print(f"Description: {tv_spec['description']}")
    print(f"Command: {' '.join(tv_spec['command'])}")

    result = {
        "tv_id": tv_id,
        "name": tv_spec["name"],
        "passed": False,
        "errors": [],
    }

    try:
        # Run command
        proc = subprocess.run(
            tv_spec["command"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

        # Check exit code
        expected_exit = tv_spec.get("expected_exit")
        if expected_exit is not None:
            if proc.returncode != expected_exit:
                result["errors"].append(f"Exit code mismatch: expected {expected_exit}, got {proc.returncode}")

        # Check expected files exist
        for expected_file in tv_spec.get("expected_files", []):
            file_path = REPO_ROOT / expected_file
            if not file_path.exists():
                result["errors"].append(f"Missing expected file: {expected_file}")
            else:
                # Validate JSON schema if specified
                if expected_file.endswith(".json") and "expected_schema_keys" in tv_spec:
                    try:
                        data = json.loads(file_path.read_text())
                        for key in tv_spec["expected_schema_keys"]:
                            if key not in data:
                                result["errors"].append(f"Missing schema key '{key}' in {expected_file}")
                    except json.JSONDecodeError as e:
                        result["errors"].append(f"Invalid JSON in {expected_file}: {e}")

        # Run custom validation if provided
        if "validation" in tv_spec:
            validation_func = tv_spec["validation"]
            # Load evidence file for validation
            evidence_file = tv_spec.get("expected_files", [None])[0]
            if evidence_file and evidence_file.endswith(".json"):
                evidence_path = REPO_ROOT / evidence_file
                if evidence_path.exists():
                    data = json.loads(evidence_path.read_text())
                    try:
                        if not validation_func(data):
                            result["errors"].append("Custom validation failed")
                    except Exception as e:
                        result["errors"].append(f"Validation error: {e}")

        # Determine pass/fail
        result["passed"] = len(result["errors"]) == 0

    except Exception as e:
        result["errors"].append(f"Exception during test execution: {e}")

    return result


def main():
    """Run all test vectors and report results."""
    print("=" * 80)
    print("Repo Governance Test Vectors")
    print("=" * 80)

    results = []
    for tv_id in sorted(TEST_VECTORS.keys()):
        tv_spec = TEST_VECTORS[tv_id]
        result = run_test_vector(tv_id, tv_spec)
        results.append(result)

        # Print result
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"\n{status}: {tv_id}")
        if result["errors"]:
            for error in result["errors"]:
                print(f"  Error: {error}")

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed < total:
        print("\nFailed tests:")
        for r in results:
            if not r["passed"]:
                print(f"  - {r['tv_id']}: {r['name']}")
        return 1

    print("\n✅ All test vectors passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
