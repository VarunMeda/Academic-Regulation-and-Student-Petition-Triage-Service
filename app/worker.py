import logging, signal, threading, time
from .agents import TriageGraph
from .config import settings
from .corpus import RegulationIndex
from .metrics import escalations, processing_latency, timeouts, worker_tasks
from .queue import QueueClient, is_redis_poll_error
from .store import Store
from .reliability import ExecutionTimeout, retry_delay, run_with_timeout
from .tracing import consume as consume_trace

logging.basicConfig(format='{"level":"%(levelname)s","message":"%(message)s"}', level=logging.INFO)
logger=logging.getLogger(__name__)
store=Store(settings.database_path); queue=QueueClient(settings.redis_url, settings.queue_backend)
try:
    model_name = settings.embedding_model if settings.retrieval_backend == "semantic" else None
    graph=TriageGraph(RegulationIndex(settings.index_path, model_name, settings.retrieval_backend), settings.max_graph_steps)
except FileNotFoundError: graph=None

def _handle(job):
    started=time.perf_counter(); store.update(job.run_id,"running")
    try:
        if graph is None: raise RuntimeError("corpus index unavailable")
        from .models import PetitionRequest
        result=run_with_timeout(lambda: graph.invoke(PetitionRequest.model_validate(job.payload)), settings.run_timeout_seconds)
        status="escalated" if result.human_review_required else "completed"
        store.update(job.run_id,status,result.model_dump()); worker_tasks.labels(outcome="escalated" if result.human_review_required else "success").inc()
        if result.human_review_required: escalations.labels(reason="human_review").inc()
        return True
    except ExecutionTimeout as exc:
        timeouts.labels(operation="worker_graph").inc()
        if job.attempt < settings.max_retries:
            time.sleep(retry_delay(job.attempt, settings.retry_backoff_seconds, settings.retry_backoff_max_seconds))
            store.update(job.run_id,"pending",{"retrying":True,"attempt":job.attempt+1,"error":str(exc)}); queue.retry(job); worker_tasks.labels(outcome="retry").inc(); return False
        store.update(job.run_id,"failed",{"error":str(exc),"routing":"refer-to-committee","human_review_required":True}); worker_tasks.labels(outcome="failed").inc(); return False
    except Exception as exc:
        if job.attempt < settings.max_retries:
            time.sleep(retry_delay(job.attempt, settings.retry_backoff_seconds, settings.retry_backoff_max_seconds))
            store.update(job.run_id,"pending",{"retrying":True,"attempt":job.attempt+1,"error":str(exc)}); queue.retry(job); worker_tasks.labels(outcome="retry").inc(); return False
        store.update(job.run_id,"failed",{"error":str(exc),"routing":"refer-to-committee","human_review_required":True}); worker_tasks.labels(outcome="failed").inc(); return False
    finally: processing_latency.observe(time.perf_counter()-started)

def handle(job):
    with consume_trace(job.traceparent, "triage.worker.consume"):
        return _handle(job)

def run_forever(stop_event=None):
    from prometheus_client import start_http_server
    stop_event = stop_event or threading.Event()
    def request_stop(signum, _frame):
        logger.info("worker_shutdown signal=%s", signum)
        stop_event.set()
    for signal_name in (signal.SIGINT, signal.SIGTERM):
        try: signal.signal(signal_name, request_stop)
        except (ValueError, OSError): pass
    start_http_server(9101)
    poll_attempt=0
    logger.info("worker_started queue_backend=%s",settings.queue_backend)
    while not stop_event.is_set():
        try:
            queue.ping()
            job=queue.dequeue(timeout=int(settings.queue_poll_timeout_seconds))
            poll_attempt=0
            if job: handle(job)
        except Exception as exc:
            if not is_redis_poll_error(exc): raise
            poll_attempt += 1
            logger.warning("redis_poll_failed error_type=%s retry_attempt=%s", type(exc).__name__, poll_attempt)
            stop_event.wait(retry_delay(poll_attempt - 1, settings.retry_backoff_seconds, settings.retry_backoff_max_seconds))
    queue.close()
    logger.info("worker_stopped")

if __name__ == "__main__": run_forever()


