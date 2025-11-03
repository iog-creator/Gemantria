"""
Retry utilities with exponential backoff for Gemantria.

Provides decorator-based retry logic for HTTP requests with LM Studio
error handling and exponential backoff per governance requirements.
"""

from functools import wraps
import time
import requests


class QwenUnavailableError(Exception):
    """Raised when Qwen Live service is unavailable after retries."""

    pass


def with_http_retry(attempts: int = 3, delay: float = 2.0, backoff: float = 2.0):
    """
    Decorator for HTTP requests with exponential backoff and LM Studio error handling.

    Args:
        attempts: Maximum number of retry attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 2.0)
        backoff: Backoff multiplier for exponential delay (default: 2.0)

    Returns:
        Decorated function with retry logic

    Raises:
        QwenUnavailableError: If all retry attempts fail
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            current_delay = delay

            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, ConnectionError) as e:
                    last_error = e
                    if attempt < attempts - 1:  # Don't sleep on last attempt
                        time.sleep(current_delay)
                        current_delay *= backoff
                    continue

            # All attempts failed
            raise QwenUnavailableError(f"Qwen Live service unavailable after {attempts} attempts: {last_error}")

        return wrapper

    return decorator
