import json
import threading

import pytest
from redis.exceptions import ConnectionError, TimeoutError

from app.queue import Job, QueueClient, is_redis_poll_error
from app.reliability import CircuitBreaker


def fake_redis_client(fake):
    client = QueueClient.__new__(QueueClient)
    client.backend = "redis"
    client._redis = fake
    client._local = None
    client._breaker = CircuitBreaker(failure_threshold=3, recovery_seconds=0.01)
    return client


def test_empty_redis_queue_is_a_successful_blocking_poll():
    class EmptyRedis:
        def blpop(self, key, timeout):
            assert key == "triage:jobs" and timeout == 2
            return None

    queue = fake_redis_client(EmptyRedis())
    assert queue.dequeue(timeout=2) is None
    assert queue._breaker.state == "CLOSED"
    assert queue._breaker.failures == 0


def test_socket_timeout_is_classified_as_transient_poll_failure():
    class TimeoutRedis:
        def blpop(self, key, timeout):
            raise TimeoutError("poll timed out")

    queue = fake_redis_client(TimeoutRedis())
    with pytest.raises(TimeoutError):
        queue.dequeue(timeout=2)
    assert is_redis_poll_error(TimeoutError("poll timed out"))
    assert queue._breaker.failures == 1


def test_redis_recovers_after_temporary_connection_failure():
    class RecoveringRedis:
        def __init__(self): self.calls = 0
        def blpop(self, key, timeout):
            self.calls += 1
            if self.calls == 1: raise ConnectionError("temporary outage")
            return (key, json.dumps(Job("run-1", "corr-1", {"category": "attendance"}).__dict__))
        def llen(self, key): return 0

    queue = fake_redis_client(RecoveringRedis())
    with pytest.raises(ConnectionError): queue.dequeue(timeout=2)
    job = queue.dequeue(timeout=2)
    assert job.run_id == "run-1"
    assert queue._breaker.state == "CLOSED"


def test_depth_metric_failure_does_not_drop_consumed_job():
    class MetricFailureRedis:
        def blpop(self, key, timeout):
            return (key, json.dumps(Job("run-3", "corr-3", {"category": "attendance"}).__dict__))
        def llen(self, key): raise TimeoutError("metric read timed out")

    queue = fake_redis_client(MetricFailureRedis())
    job = queue.dequeue(timeout=2)
    assert job.run_id == "run-3"


def test_socket_timeout_configuration_exceeds_poll_timeout():
    from app.config import settings
    assert settings.queue_socket_timeout_seconds > settings.queue_poll_timeout_seconds


def test_worker_continues_processing_after_redis_recovery(monkeypatch):
    import prometheus_client
    import app.worker as worker

    class RecoveringQueue:
        def __init__(self): self.calls = 0; self.closed = False
        def ping(self): return True
        def dequeue(self, timeout):
            self.calls += 1
            if self.calls == 1: raise TimeoutError("temporary outage")
            stop.set()
            return Job("run-2", "corr-2", {"category": "attendance"})
        def close(self): self.closed = True

    stop = threading.Event()
    queue = RecoveringQueue()
    handled = []
    monkeypatch.setattr(prometheus_client, "start_http_server", lambda port: None)
    monkeypatch.setattr(worker, "queue", queue)
    monkeypatch.setattr(worker, "handle", lambda job: handled.append(job))
    monkeypatch.setattr(worker, "retry_delay", lambda *args, **kwargs: 0)

    worker.run_forever(stop)
    assert [job.run_id for job in handled] == ["run-2"]
    assert queue.closed is True
