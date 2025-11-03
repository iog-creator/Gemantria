#!/usr/bin/env python3
"""
COMPASS: Comprehensive Pipeline Assessment Scoring System

Evaluates unified envelopes for mathematical correctness and data integrity.
Uses sympy for symbolic math validation of correlation weights, temporal patterns,
and edge strength calculations.

Gates: >80% correctness threshold for envelope acceptance.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
# import sympy as sp  # Hermetic: using stdlib math for now
# from sympy import symbols, simplify, Abs


def load_envelope(path: str) -> Dict[str, Any]:
    """Load unified envelope from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def validate_correlation_weights(envelope: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Validate correlation weights using symbolic math (>0.5 threshold)."""
    issues = []
    score = 1.0

    if "edges" not in envelope:
        issues.append("No edges found in envelope")
        return 0.0, issues

    edges = envelope["edges"]
    if not edges:
        issues.append("Empty edges array")
        return 0.0, issues

    # Validation of correlation weights using basic math
    invalid_weights = 0
    for i, edge in enumerate(edges):
        if "correlation_weight" not in edge:
            issues.append(f"Edge {i}: missing correlation_weight")
            invalid_weights += 1
            continue

        weight = edge["correlation_weight"]

        # Check range using sympy
        if not (0 <= weight <= 1):
            issues.append(f"Edge {i}: correlation_weight {weight} not in [0,1]")
            invalid_weights += 1

        # Check >0.5 threshold
        if weight <= 0.5:
            issues.append(f"Edge {i}: correlation_weight {weight} <= 0.5 threshold")
            invalid_weights += 1

    if len(edges) > 0:
        score = 1.0 - (invalid_weights / len(edges))

    return score, issues


def validate_edge_strength_blend(envelope: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Validate edge strength blend calculation: α*cos + (1-α)*rerank."""
    issues = []
    score = 1.0

    if "edges" not in envelope:
        issues.append("No edges found for blend validation")
        return 0.0, issues

    edges = envelope["edges"]
    if not edges:
        return 1.0, []  # Empty is valid

    # Blend validation using basic math
    invalid_blends = 0
    for i, edge in enumerate(edges):
        if "cosine" not in edge or "rerank_score" not in edge or "edge_strength" not in edge:
            issues.append(f"Edge {i}: missing cosine/rerank_score/edge_strength for blend check")
            invalid_blends += 1
            continue

        cos_val = edge["cosine"]
        rerank_val = edge["rerank_score"]
        strength_val = edge["edge_strength"]

        # Expected: 0.5*cos + 0.5*rerank (α=0.5)
        expected = 0.5 * cos_val + 0.5 * rerank_val
        tolerance = 0.005  # BLEND_TOL from rules

        if abs(strength_val - expected) > tolerance:
            issues.append(
                f"Edge {i}: edge_strength {strength_val:.3f} != expected {expected:.3f} (cos={cos_val:.3f}, rerank={rerank_val:.3f})"
            )
            invalid_blends += 1

    if len(edges) > 0:
        score = 1.0 - (invalid_blends / len(edges))

    return score, issues


def validate_temporal_patterns(envelope: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Validate temporal pattern data integrity."""
    issues = []
    score = 1.0

    if "temporal_patterns" not in envelope:
        issues.append("No temporal_patterns found in envelope")
        return 0.0, issues

    patterns = envelope["temporal_patterns"]
    if not patterns:
        return 1.0, []  # Empty is valid

    # Check for required temporal fields
    required_fields = ["series", "timestamps", "values"]
    invalid_patterns = 0

    for i, pattern in enumerate(patterns):
        missing_fields = [f for f in required_fields if f not in pattern]
        if missing_fields:
            issues.append(f"Temporal pattern {i}: missing fields {missing_fields}")
            invalid_patterns += 1
            continue

        # Validate data consistency
        timestamps = pattern["timestamps"]
        values = pattern["values"]

        if len(timestamps) != len(values):
            issues.append(f"Temporal pattern {i}: timestamps ({len(timestamps)}) != values ({len(values)})")
            invalid_patterns += 1

        # Check for monotonic timestamps (should be sorted)
        if timestamps != sorted(timestamps):
            issues.append(f"Temporal pattern {i}: timestamps not monotonic")
            invalid_patterns += 1

    if len(patterns) > 0:
        score = 1.0 - (invalid_patterns / len(patterns))

    return score, issues


def score_envelope(envelope_path: str, verbose: bool = False) -> Tuple[float, Dict[str, Any]]:
    """Score envelope for mathematical correctness and data integrity."""
    try:
        envelope = load_envelope(envelope_path)
    except Exception as e:
        return 0.0, {"error": f"Failed to load envelope: {e}"}

    results = {}

    # Run all validations
    corr_score, corr_issues = validate_correlation_weights(envelope)
    results["correlation_weights"] = {"score": corr_score, "issues": corr_issues}

    blend_score, blend_issues = validate_edge_strength_blend(envelope)
    results["edge_strength_blend"] = {"score": blend_score, "issues": blend_issues}

    temporal_score, temporal_issues = validate_temporal_patterns(envelope)
    results["temporal_patterns"] = {"score": temporal_score, "issues": temporal_issues}

    # Overall score (weighted average)
    weights = {"correlation_weights": 0.4, "edge_strength_blend": 0.4, "temporal_patterns": 0.2}
    overall_score = sum(results[k]["score"] * weights[k] for k in weights.keys())

    results["overall"] = {
        "score": overall_score,
        "threshold": 0.8,  # >80% correctness required
        "passed": overall_score >= 0.8,
    }

    if verbose:
        print(f"COMPASS Score: {overall_score:.1%}")
        print(f"Threshold: {results['overall']['threshold']:.0%}")
        print(f"Status: {'PASS' if results['overall']['passed'] else 'FAIL'}")

        for category, data in results.items():
            if category != "overall":
                print(f"\n{category}: {data['score']:.1%}")
                if data["issues"]:
                    for issue in data["issues"][:5]:  # Limit output
                        print(f"  - {issue}")

    return overall_score, results


def main():
    """CLI entry point for COMPASS scoring."""
    if len(sys.argv) < 2:
        print("Usage: python scorer.py <envelope.json> [--verbose]")
        sys.exit(1)

    envelope_path = sys.argv[1]
    verbose = "--verbose" in sys.argv

    score, results = score_envelope(envelope_path, verbose)

    if results.get("error"):
        print(f"ERROR: {results['error']}")
        sys.exit(1)

    # Exit code based on threshold
    passed = results["overall"]["passed"]
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
