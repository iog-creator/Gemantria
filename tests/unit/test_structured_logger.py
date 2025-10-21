from src.infra.structured_logger import get_logger, log_json
def test_json_logger_emits_minimal_payload(capsys):
    log = get_logger("t")
    log_json(log, 20, "hello", foo="bar")
    out = capsys.readouterr().out
    assert '"msg": "hello"' in out
    assert '"foo": "bar"' in out
