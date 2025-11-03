import pytest, time
from scripts.extract.extract_all import gen_unified_envelope  # Stub import


@pytest.mark.timeout(3)  # <3s thresh
def test_100k_extract_perf():
    start = time.time()
    env = gen_unified_envelope(100000)
    dt = time.time() - start
    assert len(env["nodes"]) == 100000
    assert dt < 3.0, f"Extract too slow: {dt}s >3s"
    print(f"✅ 100k envelope: {dt:.2f}s, {len(env['edges'])} edges")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
