import asyncio, uuid
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from .config import settings
from .models import PetitionRequest
from .corpus import RegulationIndex
from .agents import TriageGraph
from .store import Store

app=FastAPI(title="Academic Petition Triage Service", version="0.1.0")
store=Store(settings.database_path)
try: graph=TriageGraph(RegulationIndex(settings.index_path))
except FileNotFoundError: graph=None

@app.exception_handler(RequestValidationError)
async def quarantine_invalid(request: Request, exc: RequestValidationError):
    cid=request.headers.get("x-correlation-id") or str(uuid.uuid4())
    store.quarantine(exc.errors(), cid)
    return JSONResponse(status_code=422, content={"error":"validation_failed","correlation_id":cid,"field_errors":exc.errors()})

@app.get("/health/live")
def live(): return {"status":"ok"}
@app.get("/health/ready")
def ready():
    if graph is None: raise HTTPException(503,"corpus index unavailable; run python -m app.ingest")
    return {"status":"ready","synthetic_corpus":True}
@app.get("/metrics", response_class=PlainTextResponse)
def metrics(): return "# HELP triage_runs_total Total submitted runs\n# TYPE triage_runs_total counter\ntriage_runs_total 0\n"

async def process(rid, petition):
    store.update(rid,"running")
    try:
        if graph is None: raise RuntimeError("corpus index unavailable")
        result=await asyncio.wait_for(asyncio.to_thread(graph.invoke,petition),settings.run_timeout_seconds)
        store.update(rid,"completed",result.model_dump())
    except Exception as exc: store.update(rid,"escalated",{"error":str(exc),"routing":"refer-to-committee","human_review_required":True})

@app.post("/api/petitions", status_code=202)
async def submit(petition: PetitionRequest, x_correlation_id: str | None = Header(default=None)):
    cid=x_correlation_id or str(uuid.uuid4()); rid=store.create(petition.model_dump(),cid); asyncio.create_task(process(rid,petition)); return {"run_id":rid,"status":"pending","correlation_id":cid}

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
@app.post("/api/feedback")
def feedback(payload: dict): return {"accepted":True,"message":"feedback endpoint available; persistence is deferred to the evaluation milestone"}

