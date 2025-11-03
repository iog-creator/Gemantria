import pytest
import time
import tempfile
import subprocess
import json
from pathlib import Path


@pytest.mark.timeout(3)  # <3s thresh
def test_100k_extract_perf():
    """Test 100k node extraction performance with COMPASS validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Run extract_all.py
        start = time.time()
        cmd = ["python3", "scripts/extract/extract_all.py", "--size", "100000", "--outdir", tmpdir]
        result = subprocess.run(cmd, capture_output=True, text=True)
        dt = time.time() - start

        assert result.returncode == 0, f"Extract failed: {result.stderr}"
        assert dt < 3.0, ".2f"

        # Load and validate envelope
        envelope_path = Path(tmpdir) / "unified_envelope_100000.json"
        assert envelope_path.exists(), "Envelope file not created"

        with open(envelope_path) as f:
            env = json.load(f)

        assert len(env["nodes"]) == 100000, f"Expected 100000 nodes, got {len(env['nodes'])}"
        assert "edges" in env, "Missing edges in envelope"
        assert "temporal_patterns" in env, "Missing temporal_patterns in envelope"
        assert "correlations" in env, "Missing correlations in envelope"

        print(f"✅ 100k envelope: {dt:.2f}s, {len(env['edges'])} edges")

        # COMPASS validation gate
        compass_cmd = ["python3", "scripts/compass/scorer.py", str(envelope_path), "--verbose"]
        compass_result = subprocess.run(compass_cmd, capture_output=True, text=True)

        assert compass_result.returncode == 0, f"COMPASS failed: {compass_result.stderr}"
        assert (
            "PASS" in compass_result.stdout
        ), f"COMPASS validation failed:\n{compass_result.stdout}"

        print("✅ COMPASS validation: PASS")


@pytest.mark.timeout(10)  # Allow more time for smaller extracts
def test_10k_extract_with_compass():
    """Test 10k node extraction with full COMPASS validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = ["python3", "scripts/extract/extract_all.py", "--size", "10000", "--outdir", tmpdir]
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Extract failed: {result.stderr}"

        envelope_path = Path(tmpdir) / "unified_envelope_10000.json"
        assert envelope_path.exists()

        # Run COMPASS with verbose output
        compass_cmd = ["python3", "scripts/compass/scorer.py", str(envelope_path), "--verbose"]
        compass_result = subprocess.run(compass_cmd, capture_output=True, text=True)

        assert compass_result.returncode == 0
        assert "PASS" in compass_result.stdout

        # Check for specific COMPASS components
        output = compass_result.stdout
        assert "correlation_weights:" in output
        assert "edge_strength_blend:" in output
        assert "temporal_patterns:" in output

        print("✅ 10k extract with COMPASS validation: PASS")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
