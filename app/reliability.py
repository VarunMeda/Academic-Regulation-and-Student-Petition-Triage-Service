"""Small, dependency-free reliability primitives used by the queue and worker."""
import random
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from typing import Callable, TypeVar

T = TypeVar("T")

class ExecutionTimeout(RuntimeError):
    """Raised when a bounded application operation exceeds its deadline."""

def run_with_timeout(fn: Callable[[], T], timeout_seconds: float) -> T:
    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="triage-deadline")
    future = executor.submit(fn)
    try:
        return future.result(timeout=timeout_seconds)
    except TimeoutError as exc:
        future.cancel()
        raise ExecutionTimeout(f"operation exceeded {timeout_seconds:g}s deadline") from exc
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

def retry_delay(attempt: int, base: float, maximum: float, jitter: float = 0.1) -> float:
    exponential = min(maximum, base * (2 ** max(0, attempt)))
    return exponential + random.uniform(0, exponential * jitter)

@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_seconds: float = 10.0
    state: str = "CLOSED"
    failures: int = 0
    opened_at: float | None = None

    def allow(self) -> bool:
        if self.state == "CLOSED": return True
        if self.state == "OPEN" and self.opened_at is not None and time.monotonic() - self.opened_at >= self.recovery_seconds:
            self.state = "HALF_OPEN"; return True
        return self.state == "HALF_OPEN"

    def success(self) -> None:
        self.state = "CLOSED"; self.failures = 0; self.opened_at = None

    def failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"; self.opened_at = time.monotonic()

    def call(self, fn: Callable[[], T]) -> T:
        if not self.allow(): raise RuntimeError("circuit breaker is open")
        try: value = fn()
        except Exception:
            self.failure(); raise
        self.success(); return value
