import uuid
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from .config import settings
from .models import FeedbackRequest, PetitionRequest
from .corpus import RegulationIndex
from .agents import TriageGraph
from .metrics import api_requests, api_errors, render_metrics
from .queue import Job, QueueClient
from .store import Store

app=FastAPI(title="Academic Petition Triage Service", version="0.2.0")
store=Store(settings.database_path); queue=QueueClient(settings.redis_url, settings.queue_backend)
local_executor=ThreadPoolExecutor(max_workers=4, thread_name_prefix="local-queue-worker")
try: graph=TriageGraph(RegulationIndex(settings.index_path), settings.max_graph_steps)
except FileNotFoundError: graph=None

def process_local(job):
    try:
        if graph is None: raise RuntimeError("corpus index unavailable")
        result=graph.invoke(PetitionRequest.model_validate(job.payload))
        store.update(job.run_id,"escalated" if result.human_review_required else "completed",result.model_dump())
    except Exception as exc:
        store.update(job.run_id,"failed",{"error":str(exc),"routing":"refer-to-committee","human_review_required":True})

@app.middleware("http")
async def observe(request: Request, call_next):
    response=await call_next(request); api_requests.labels(request.method,request.url.path,response.status_code).inc(); return response

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
    return {"status":"ready","synthetic_corpus":True,"queue_backend":settings.queue_backend}
@app.get("/metrics")
def metrics():
    body, content_type=render_metrics(); return Response(body,media_type=content_type)

@app.post("/api/petitions", status_code=202)
async def submit(petition: PetitionRequest, x_correlation_id: str | None = Header(default=None), idempotency_key: str | None = Header(default=None)):
    cid=x_correlation_id or str(uuid.uuid4()); rid, duplicate=store.create(petition.model_dump(),cid,idempotency_key)
    if not duplicate:
        job=Job(rid,cid,petition.model_dump()); queue.enqueue(job)
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
