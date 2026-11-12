import uuid, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response, HTMLResponse
from .config import settings
from .models import FeedbackRequest, PetitionRequest
from .corpus import RegulationIndex, ingest
from .agents import TriageGraph
from .metrics import api_requests, api_errors, render_metrics
from .queue import Job, QueueClient
from .store import Store
from .tracing import configure as configure_tracing, inject as inject_traceparent

app=FastAPI(title="Academic Petition Triage Service", version="0.2.0")
store=Store(settings.database_path); queue=QueueClient(settings.redis_url, settings.queue_backend)
request_windows={}
local_executor=ThreadPoolExecutor(max_workers=4, thread_name_prefix="local-queue-worker")
def load_graph():
    # A clean clone is runnable without a separate manual indexing step.
    if not __import__("pathlib").Path(settings.index_path).exists():
        ingest(settings.corpus_dir, settings.index_path)
    model_name = settings.embedding_model if settings.retrieval_backend == "semantic" else None
    return TriageGraph(RegulationIndex(settings.index_path, model_name, settings.retrieval_backend), settings.max_graph_steps)

try: graph=load_graph()
except Exception: graph=None

def process_local(job):
    try:
        if graph is None: raise RuntimeError("corpus index unavailable")
        result=graph.invoke(PetitionRequest.model_validate(job.payload))
        store.update(job.run_id,"escalated" if result.human_review_required else "completed",result.model_dump())
    except Exception as exc:
        store.update(job.run_id,"failed",{"error":str(exc),"routing":"refer-to-committee","human_review_required":True})

@app.middleware("http")
async def observe(request: Request, call_next):
    # Lightweight per-process guardrail. Use a shared gateway for multi-replica deployments.
    if request.url.path.startswith("/api/") and settings.rate_limit_per_minute > 0:
        client=request.client.host if request.client else "unknown"
        now=time.monotonic(); window=request_windows.setdefault(client, [])
        window[:]=[stamp for stamp in window if now-stamp < 60]
        if len(window) >= settings.rate_limit_per_minute:
            api_errors.labels(request.url.path).inc()
            return JSONResponse(status_code=429,content={"error":"rate_limit_exceeded","retry_after_seconds":60-int(now-window[0])})
        window.append(now)
    response=await call_next(request)
    api_requests.labels(request.method,request.url.path,response.status_code).inc()
    return response

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def web_client():
    page=Path(__file__).parent/"static"/"index.html"
    return HTMLResponse(page.read_text(encoding="utf-8"))

@app.exception_handler(RequestValidationError)
async def quarantine_invalid(request: Request, exc: RequestValidationError):
    cid=request.headers.get("x-correlation-id") or str(uuid.uuid4()); store.quarantine(exc.errors(),cid); api_errors.labels(request.url.path).inc()
    return JSONResponse(status_code=422, content={"error":"validation_failed","correlation_id":cid,"field_errors":exc.errors()})

@app.get("/health/live")
def live(): return {"status":"ok"}
@app.get("/health/ready")
def ready():
    if graph is None: raise HTTPException(503,"corpus index unavailable; run python -m app.ingest")
    try: queue.ping()
    except Exception as exc: raise HTTPException(503,f"queue unavailable: {exc}")
    return {"status":"ready","synthetic_corpus":True,"queue_backend":settings.queue_backend,
            "retrieval_backend":settings.retrieval_backend,"embedding_model":settings.embedding_model if settings.retrieval_backend == "semantic" else None}
@app.get("/metrics")
def metrics():
    body, content_type=render_metrics(); return Response(body,media_type=content_type)

@app.post("/api/petitions", status_code=202)
async def submit(petition: PetitionRequest, x_correlation_id: str | None = Header(default=None), idempotency_key: str | None = Header(default=None)):
    cid=x_correlation_id or str(uuid.uuid4()); rid, duplicate=store.create(petition.model_dump(),cid,idempotency_key)
    if not duplicate:
        job=Job(rid,cid,petition.model_dump(),traceparent=inject_traceparent()); queue.enqueue(job)
        if settings.queue_backend != "redis":
            local_executor.submit(process_local,queue.dequeue(timeout=0))
    saved=store.get(rid); return {"run_id":rid,"status":saved["status"],"correlation_id":saved["correlation_id"],"duplicate":duplicate}

@app.get("/api/runs/{run_id}")
def status(run_id):
    r=store.get(run_id)
    if not r: raise HTTPException(404,"run not found")
    return {k:v for k,v in r.items() if k!="result"}
@app.get("/api/runs/{run_id}/result")
def result(run_id):
    r=store.get(run_id)
    if not r: raise HTTPException(404,"run not found")
    if r["status"] not in {"completed","escalated","failed"}: raise HTTPException(409,"run not terminal")
    return r["result"]
@app.post("/api/feedback", status_code=201)
def feedback(payload: FeedbackRequest):
    run=store.get(payload.run_id)
    if not run: raise HTTPException(404,"run not found")
    store.feedback(payload.model_dump()); return {"accepted":True,"run_id":payload.run_id}

@app.get("/api/feedback/summary")
def feedback_summary():
    return store.feedback_summary()

@app.get("/api/quarantine")
def quarantine_records(limit: int = 50):
    return {"items": store.quarantine_items(max(1,min(limit,200)))}

tracing_enabled = configure_tracing(app, settings.otel_service_name, settings.otel_exporter_endpoint)
