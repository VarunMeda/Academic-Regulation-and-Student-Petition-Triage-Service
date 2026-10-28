import logging, time
from .agents import TriageGraph
from .config import settings
from .corpus import RegulationIndex
from .metrics import escalations, processing_latency, worker_tasks
from .queue import QueueClient
from .store import Store

logging.basicConfig(format='{"level":"%(levelname)s","message":"%(message)s"}', level=logging.INFO)
store=Store(settings.database_path); queue=QueueClient(settings.redis_url, settings.queue_backend)
try: graph=TriageGraph(RegulationIndex(settings.index_path), settings.max_graph_steps)
except FileNotFoundError: graph=None

def handle(job):
    started=time.perf_counter(); store.update(job.run_id,"running")
    try:
        if graph is None: raise RuntimeError("corpus index unavailable")
        from .models import PetitionRequest
        result=graph.invoke(PetitionRequest.model_validate(job.payload))
        status="escalated" if result.human_review_required else "completed"
        store.update(job.run_id,status,result.model_dump()); worker_tasks.inc("escalated" if result.human_review_required else "success")
        if result.human_review_required: escalations.inc("human_review")
        return True
    except Exception as exc:
        if job.attempt < settings.max_retries:
            store.update(job.run_id,"pending",{"retrying":True,"attempt":job.attempt+1,"error":str(exc)}); queue.retry(job); worker_tasks.inc("retry"); return False
        store.update(job.run_id,"failed",{"error":str(exc),"routing":"refer-to-committee","human_review_required":True}); worker_tasks.inc("failed"); return False
    finally: processing_latency.observe(time.perf_counter()-started)

def run_forever():
    from prometheus_client import start_http_server
    start_http_server(9101)
    queue.ping(); logging.info("worker_started queue_backend=%s",settings.queue_backend)
    while True:
        job=queue.dequeue(timeout=2)
        if job: handle(job)

if __name__ == "__main__": run_forever()
