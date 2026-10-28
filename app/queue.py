"""Redis-backed queue with an explicit in-process test fallback."""
import json, queue as local_queue
from dataclasses import dataclass
from .config import settings
from .metrics import queue_depth, retries

@dataclass
class Job:
    run_id: str
    correlation_id: str
    payload: dict
    attempt: int = 0

class QueueClient:
    def __init__(self, url: str | None = None, backend: str | None = None):
        self.backend=backend or getattr(settings, "queue_backend", "memory")
        self.url=url or getattr(settings, "redis_url", "redis://localhost:6379/0")
        self._local=local_queue.Queue()
        self._redis=None
        if self.backend == "redis":
            try:
                import redis
                self._redis=redis.Redis.from_url(self.url, decode_responses=True)
            except ImportError as exc: raise RuntimeError("Redis queue requires the redis package") from exc
    def ping(self):
        if self.backend == "redis": self._redis.ping(); return True
        return True
    def enqueue(self, job: Job):
        raw=json.dumps(job.__dict__)
        if self.backend == "redis": self._redis.rpush("triage:jobs", raw)
        else: self._local.put(raw)
        queue_depth.set(self.depth())
    def dequeue(self, timeout: int = 1) -> Job | None:
        if self.backend == "redis":
            item=self._redis.blpop("triage:jobs", timeout=timeout)
            raw=item[1] if item else None
        else:
            try: raw=self._local.get(timeout=timeout)
            except local_queue.Empty: return None
        if not raw: return None
        queue_depth.set(self.depth()); return Job(**json.loads(raw))
    def depth(self):
        return int(self._redis.llen("triage:jobs")) if self.backend == "redis" else self._local.qsize()
    def retry(self, job: Job):
        retries.inc(); self.enqueue(Job(job.run_id,job.correlation_id,job.payload,job.attempt+1))
