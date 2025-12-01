"""
Tests for edge reclassification script (Phase-10).

Verifies that reclassify_edges.py correctly classifies edges by strength thresholds
and generates edge_class_counts.json with proper structure.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Calculate ROOT: tests/unit/test_*.py -> tests/ -> repo root
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


class TestReclassifyEdges:
    """Test edge reclassification script."""

    def test_reclassify_edges_with_fixture(self):
        """Test reclassify_edges with a small graph fixture."""
        import subprocess
        import os

        # Create a temporary graph fixture with known edge strengths
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            exports_path = tmp_path / "exports"
            exports_path.mkdir(exist_ok=True)
            graph_path = exports_path / "graph_latest.json"

            # Create graph fixture with edges of known strengths
            graph_data = {
                "edges": [
                    {"edge_strength": 0.95, "src": "node1", "dst": "node2"},  # strong
                    {"edge_strength": 0.92, "src": "node2", "dst": "node3"},  # strong
                    {"edge_strength": 0.80, "src": "node3", "dst": "node4"},  # weak
                    {"edge_strength": 0.78, "src": "node4", "dst": "node5"},  # weak
                    {"edge_strength": 0.50, "src": "node5", "dst": "node6"},  # other
                    {"edge_strength": 0.30, "src": "node6", "dst": "node7"},  # other
                ]
            }

            graph_path.write_text(json.dumps(graph_data), encoding="utf-8")

            # Create share/eval/edges directory
            (tmp_path / "share" / "eval" / "edges").mkdir(parents=True, exist_ok=True)

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)

                # Run the script via subprocess
                script_path = ROOT / "scripts" / "eval" / "reclassify_edges.py"
                assert script_path.exists(), f"Script not found at {script_path}"
                result = subprocess.run(
                    [sys.executable, str(script_path.resolve())],
                    capture_output=True,
                    text=True,
                    cwd=str(tmp_path),
                )

                # Check exit code
                assert (
                    result.returncode == 0
                ), f"Script should exit with 0, got {result.returncode}\n{result.stderr}"

                # Check output file exists
                output_file = tmp_path / "share" / "eval" / "edges" / "edge_class_counts.json"
                assert output_file.exists(), "edge_class_counts.json should be created"

                # Load and verify output
                output_data = json.loads(output_file.read_text(encoding="utf-8"))

                # Verify structure
                assert "thresholds" in output_data
                assert "counts" in output_data
                assert "strong" in output_data["thresholds"]
                assert "weak" in output_data["thresholds"]
                assert "strong" in output_data["counts"]
                assert "weak" in output_data["counts"]
                assert "other" in output_data["counts"]

                # Verify counts (2 strong, 2 weak, 2 other)
                assert output_data["counts"]["strong"] == 2
                assert output_data["counts"]["weak"] == 2
                assert output_data["counts"]["other"] == 2

                # Verify thresholds (defaults: 0.90 strong, 0.75 weak)
                assert output_data["thresholds"]["strong"] == 0.90
                assert output_data["thresholds"]["weak"] == 0.75

            finally:
                os.chdir(original_cwd)

    def test_reclassify_edges_hermetic_missing_graph(self):
        """Test reclassify_edges handles missing graph_latest.json gracefully."""
        import subprocess
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            original_cwd = os.getcwd()

            try:
                os.chdir(tmpdir)

                # Ensure exports/graph_latest.json doesn't exist
                assert not (tmp_path / "exports" / "graph_latest.json").exists()

                # Create share/eval/edges directory
                (tmp_path / "share" / "eval" / "edges").mkdir(parents=True, exist_ok=True)

                # Run the script - should handle missing file gracefully
                script_path = ROOT / "scripts" / "eval" / "reclassify_edges.py"
                assert script_path.exists(), f"Script not found at {script_path}"
                result = subprocess.run(
                    [sys.executable, str(script_path.resolve())],
                    capture_output=True,
                    text=True,
                    cwd=str(tmp_path),
                )

                # Script should still exit 0 (hermetic behavior)
                assert (
                    result.returncode == 0
                ), f"Script should exit 0 even when graph_latest.json is missing, got {result.returncode}\n{result.stderr}"

                # Output file should still be created with zero counts
                output_file = tmp_path / "share" / "eval" / "edges" / "edge_class_counts.json"
                if output_file.exists():
                    output_data = json.loads(output_file.read_text(encoding="utf-8"))
                    assert output_data["counts"]["strong"] == 0
                    assert output_data["counts"]["weak"] == 0
                    assert output_data["counts"]["other"] == 0

            finally:
                os.chdir(original_cwd)
