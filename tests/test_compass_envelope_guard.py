import json, pathlib, pytest


def has_unified_envelope_structure(path):
    """Check if path contains a unified envelope with required COMPASS fields."""
    try:
        d = json.loads(pathlib.Path(path).read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return False

    # Must have temporal_patterns and edges
    if not all(k in d for k in ["temporal_patterns", "edges"]):
        return False

    # Edges must have correlation_weight
    edges = d.get("edges", [])
    if edges and "correlation_weight" not in edges[0]:
        return False

    return True


def test_envelope_has_required_compass_structure():
    """Test that share/exports/envelope.json has unified envelope structure for COMPASS."""
    p = pathlib.Path("share/exports/envelope.json")
    if not p.exists():
        pytest.skip("no envelope in share/exports yet")

    assert has_unified_envelope_structure(p), (
        "share/exports/envelope.json lacks required COMPASS structure (temporal_patterns, edges, correlation_weight)"
    )
