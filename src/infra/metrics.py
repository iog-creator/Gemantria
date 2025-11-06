from statistics import median


def summarize_latencies(samples_ms):
    s = sorted(samples_ms)
    return {"p50": median(s), "p95": s[int(len(s) * 0.95) - 1] if s else 0}
