"""Redis-backed queue with an explicit in-process test fallback."""
import json, queue as local_queue
from dataclasses import dataclass
from .config import settings
from .metrics import queue_depth, retries
from .reliability import CircuitBreaker

try:
    import redis
    REDIS_TRANSIENT_ERRORS = (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError)
except ImportError:
    redis = None
    REDIS_TRANSIENT_ERRORS = (TimeoutError, ConnectionError, OSError)

def is_redis_poll_error(exc: BaseException) -> bool:
    return isinstance(exc, REDIS_TRANSIENT_ERRORS) or (isinstance(exc, RuntimeError) and str(exc) == "circuit breaker is open")

@dataclass
class Job:
    run_id: str
    correlation_id: str
    payload: dict
    attempt: int = 0
    traceparent: str | None = None

class QueueClient:
    def __init__(self, url: str | None = None, backend: str | None = None):
        self.backend=backend or getattr(settings, "queue_backend", "memory")
        self.url=url or getattr(settings, "redis_url", "redis://localhost:6379/0")
        self._local=local_queue.Queue()
        self._redis=None
        self._breaker=CircuitBreaker(settings.circuit_failure_threshold, settings.circuit_recovery_seconds)
        if self.backend == "redis":
            try:
                import redis
                self._redis=redis.Redis.from_url(self.url, decode_responses=True, socket_timeout=settings.queue_socket_timeout_seconds, socket_connect_timeout=settings.queue_operation_timeout_seconds, retry_on_timeout=True)
            except ImportError as exc: raise RuntimeError("Redis queue requires the redis package") from exc
    def ping(self):
        if self.backend == "redis": self._breaker.call(self._redis.ping); return True
        return True
    def enqueue(self, job: Job):
        raw=json.dumps(job.__dict__)
        if self.backend == "redis": self._breaker.call(lambda: self._redis.rpush("triage:jobs", raw))
        else: self._local.put(raw)
        self._update_depth_best_effort()
    def dequeue(self, timeout: int = 1) -> Job | None:
        if self.backend == "redis":
            item=self._breaker.call(lambda: self._redis.blpop("triage:jobs", timeout=timeout))
            raw=item[1] if item else None
        else:
            try: raw=self._local.get(timeout=timeout)
            except local_queue.Empty: return None
        if not raw: return None
        self._update_depth_best_effort(); return Job(**json.loads(raw))
    def depth(self):
        return int(self._breaker.call(lambda: self._redis.llen("triage:jobs"))) if self.backend == "redis" else self._local.qsize()
    def retry(self, job: Job):
        retries.inc(); self.enqueue(Job(job.run_id,job.correlation_id,job.payload,job.attempt+1,job.traceparent))
    def close(self):
        if self._redis is not None: self._redis.close()
    def _update_depth_best_effort(self):
        try: queue_depth.set(self.depth())
        except Exception as exc:
            if not is_redis_poll_error(exc): raise
