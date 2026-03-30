"""
retry_handler.py — Exponential backoff retry decorator for all external API calls.

Usage:
    from retry_handler import with_retry, TransientError

    @with_retry(max_attempts=3, base_delay=1, max_delay=60)
    def call_gmail_api():
        ...

    # Or raise TransientError to trigger a retry:
    def my_function():
        try:
            response = requests.get(url)
            if response.status_code == 429:
                raise TransientError("Rate limited")
        except requests.Timeout:
            raise TransientError("Request timed out")

This matches the pattern shown in the hackathon docs (Section 7.2).
"""

import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class TransientError(Exception):
    """
    Raise this for errors that should trigger a retry.

    Examples:
    - Network timeouts
    - API rate limits (HTTP 429)
    - Temporary server errors (HTTP 503)
    - Connection resets

    Do NOT raise this for:
    - Authentication failures (401, 403) — these need human intervention
    - Not found (404) — won't be fixed by retrying
    - Bad request (400) — won't be fixed by retrying
    - Payment/financial errors — always require fresh human approval
    """
    pass


class AuthenticationError(Exception):
    """Raised when credentials are invalid/expired. Requires human intervention."""
    pass


class PermanentError(Exception):
    """Raised for errors that should NOT be retried."""
    pass


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (TransientError,),
    on_retry: callable = None,
):
    """
    Decorator that retries a function on TransientError with exponential backoff.

    Args:
        max_attempts:   Maximum number of attempts (including first try)
        base_delay:     Initial delay in seconds before first retry
        max_delay:      Maximum delay cap in seconds
        backoff_factor: Multiplier for delay after each attempt (default: 2x)
        exceptions:     Tuple of exception types that trigger a retry
        on_retry:       Optional callback(attempt, error, delay) called before each retry

    Example:
        @with_retry(max_attempts=3, base_delay=2, max_delay=30)
        def fetch_emails():
            # Will retry up to 3 times: delays 2s, 4s
            return gmail_service.users().messages().list(userId='me').execute()

    Delay schedule (base=1, factor=2):
        Attempt 1: runs immediately
        Attempt 2: waits 1s after failure
        Attempt 3: waits 2s after failure
        Attempt 4: waits 4s after failure  (if max_attempts allows)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__}: All {max_attempts} attempts failed. "
                            f"Last error: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor ** (attempt - 1)), max_delay)

                    logger.warning(
                        f"{func.__name__}: Attempt {attempt}/{max_attempts} failed — "
                        f"{type(e).__name__}: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    if on_retry:
                        try:
                            on_retry(attempt, e, delay)
                        except Exception:
                            pass  # Don't let the callback break the retry

                    time.sleep(delay)

                except (AuthenticationError, PermanentError):
                    # Never retry these
                    raise

            # Should never reach here, but just in case
            raise last_exception

        return wrapper
    return decorator


def retry_on_status(status_codes: list = None):
    """
    Utility to check if an HTTP response should trigger a TransientError.

    Usage:
        response = requests.get(url)
        retry_on_status([429, 503])(response)  # Raises TransientError if matched
    """
    if status_codes is None:
        status_codes = [429, 500, 502, 503, 504]

    def check(response):
        if hasattr(response, 'status_code') and response.status_code in status_codes:
            raise TransientError(
                f"HTTP {response.status_code} — transient error, will retry"
            )
        return response

    return check


# ─── Pre-configured retry decorators for common use cases ─────────────────────

# For Gmail API calls (rate limited, occasional 503s)
gmail_retry = with_retry(max_attempts=3, base_delay=2, max_delay=30)

# For general HTTP calls
http_retry = with_retry(max_attempts=3, base_delay=1, max_delay=15)

# For file operations (rare but possible on network shares)
file_retry = with_retry(max_attempts=2, base_delay=0.5, max_delay=5)

# For long-running operations (more patience)
long_retry = with_retry(max_attempts=5, base_delay=5, max_delay=120)


# ─── Example usage ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import random

    @with_retry(max_attempts=4, base_delay=0.1, max_delay=1)
    def flaky_function():
        """Simulates a flaky API call that sometimes fails."""
        if random.random() < 0.6:
            raise TransientError("Simulated network timeout")
        return "Success!"

    print("Testing retry handler...")
    try:
        result = flaky_function()
        print(f"Result: {result}")
    except TransientError as e:
        print(f"All retries exhausted: {e}")
