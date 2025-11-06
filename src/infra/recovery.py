import time, json, pathlib


def with_retries(fn, *, max_tries=3, base=0.5, evidence_path=None):
    tries = 0
    while True:
        try:
            return fn()
        except Exception as e:
            tries += 1
            if evidence_path:
                pathlib.Path(evidence_path).write_text(json.dumps({"error": str(e), "tries": tries, "ts": time.time()}))
            if tries >= max_tries:
                raise
            time.sleep(base * (2 ** (tries - 1)))
