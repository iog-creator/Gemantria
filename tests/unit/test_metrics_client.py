import os
from src.infra.metrics import MetricsClient
def test_metrics_disabled_no_crash(monkeypatch):
    monkeypatch.setenv("METRICS_ENABLED","0")
    mc = MetricsClient(dsn=None)
    mc.emit({"run_id":"00000000-0000-0000-0000-000000000000", "workflow":"w", "thread_id":"t",
             "node":"n","event":"node_start","status":"ok",
             "started_at":None,"finished_at":None,"duration_ms":None,
             "items_in":None,"items_out":None,"error_json":None,"meta":None})
    assert True
