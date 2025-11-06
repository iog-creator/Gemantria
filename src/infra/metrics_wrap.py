"""
Metrics wrapper for timing model calls and tracking performance.

Provides drop-in timing wrapper for LLM calls with automatic
latency tracking and integration into evidence summaries.
"""

import time
from typing import Any, Callable, List, Tuple


def timed_call(
    call_fn: Callable[[], Any], *, log_samples: List[int], token_samples: List[dict] | None = None
) -> Tuple[Any, int]:
    """
    Time a function call and append milliseconds to log_samples.
    Optionally track token usage if token_samples provided.

    Args:
        call_fn: Function to call (no args)
        log_samples: List to append timing result (modified in-place)
        token_samples: Optional list to append token usage dicts

    Returns:
        (result, milliseconds_taken)
    """
    t0 = time.time()
    result = call_fn()
    dt_ms = int((time.time() - t0) * 1000)
    log_samples.append(dt_ms)

    # Track token usage if requested
    if token_samples is not None and hasattr(result, "usage"):
        usage = result.usage
        tokens_in = getattr(usage, "prompt_tokens", 0)
        tokens_out = getattr(usage, "completion_tokens", 0)
        total_tokens = getattr(usage, "total_tokens", tokens_in + tokens_out)

        token_samples.append(
            {"tokens_in": tokens_in, "tokens_out": tokens_out, "tokens_total": total_tokens, "latency_ms": dt_ms}
        )

    return result, dt_ms


def calculate_percentiles(samples: List[int], token_samples: List[dict] | None = None) -> dict:
    """
    Calculate p50, p95, p99 percentiles from timing samples.
    If token_samples provided, also compute token stats and TPS.

    Args:
        samples: List of millisecond timings
        token_samples: Optional list of token usage dicts

    Returns:
        Dict with percentile values and optional token stats
    """
    result = {}

    # Timing percentiles
    if not samples:
        result.update({"p50": 0, "p95": 0, "p99": 0})
    else:
        sorted_samples = sorted(samples)
        n = len(sorted_samples)

        def percentile(p: float) -> int:
            idx = int(p * (n - 1))
            return sorted_samples[idx]

        result.update(
            {
                "p50": percentile(0.50),
                "p95": percentile(0.95),
                "p99": percentile(0.99),
            }
        )

    # Token statistics and TPS
    if token_samples:
        total_tokens_in = sum(t.get("tokens_in", 0) for t in token_samples)
        total_tokens_out = sum(t.get("tokens_out", 0) for t in token_samples)
        total_tokens = sum(t.get("tokens_total", 0) for t in token_samples)
        total_latency_ms = sum(t.get("latency_ms", 1) for t in token_samples)  # avoid div by zero

        # TPS = tokens per second (total tokens / total time in seconds)
        tps = (total_tokens / max(total_latency_ms / 1000, 0.001)) if total_latency_ms > 0 else 0

        result.update(
            {
                "tokens_in": total_tokens_in,
                "tokens_out": total_tokens_out,
                "tokens_total": total_tokens,
                "tps": round(tps, 2),
            }
        )

    return result
