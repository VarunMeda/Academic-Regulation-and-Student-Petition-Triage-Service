# Academic Regulation and Student Petition Triage Service

Production-style mini-project core for evidence-backed, advisory petition triage. The repository currently uses a clearly labelled synthetic corpus; it must not be presented as an official university rule.

## Run locally

```powershell
python -m app.ingest
uvicorn app.main:app --reload
```

For a local semantic index when the optional packages and model are available:

```powershell
pip install -e ".[full]"
python -m app.ingest --model-name sentence-transformers/all-MiniLM-L6-v2
```

Submit a synthetic attendance case:

```powershell
curl -X POST http://localhost:8000/api/petitions -H "Content-Type: application/json" -d '{"category":"attendance","description":"Documented medical attendance shortfall","attendance_percentage":70,"prescribed_minimum":75,"medical_documented":true,"condonation_requested":true}'
```

Poll `/api/runs/{run_id}` and then `/api/runs/{run_id}/result`. The critical case returns `refer-to-committee` with both synthetic clauses and a verification result. The system never makes the institution's final determination.

## Tests and Docker

```powershell
pytest -q
docker compose config
docker compose up --build
```

Compose runs four services: `api` validates and enqueues petitions, `worker` consumes Redis jobs and persists LangGraph results, `redis` provides the queue, and `prometheus` scrapes API/worker metrics. Run state is stored in the named `run-data` volume. The image builds the documented synthetic lexical index; semantic model weights are not downloaded during container startup. To use semantic retrieval in a container, build/provide the model cache explicitly and run the ingestion command against the mounted cache before demonstration.

For the local fallback queue, leave `QUEUE_BACKEND=memory`. Compose sets `QUEUE_BACKEND=redis`. Redis jobs contain only the run ID, correlation ID, validated petition fields, and retry attempt. Failures retry twice, then become `failed`; committee/discretion results are `escalated`. `Idempotency-Key` repeats return the original run ID without enqueueing a duplicate.

Health and metrics:

```powershell
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
curl http://localhost:8000/metrics
```

The core is dependency-light for offline development. The `full` extra provides LangGraph/LangChain and sentence-transformers/FAISS integrations. `python -m app.ingest` is idempotent and rebuilds only the index artifact; re-run it with a different model to re-embed without changing API or agent code. In this environment those optional packages were unavailable, so the tested index uses the explicit deterministic lexical fallback and the LangGraph runtime falls back to the same bounded two-node graph semantics.

## Status

Implemented and tested: F1-F2, F4-F8 core path; A1-A4 core path; D1-D3 foundation; metadata-preserving idempotent ingestion; optional semantic/LangChain adapters; bounded tool calls; injection escalation; synthetic critical scenario and citation verification.

Runtime verification: the real LangGraph `StateGraph` and semantic Sentence Transformers/FAISS paths passed in the configured local environment. Redis/Docker execution remains environment-dependent and must be verified with `docker compose up --build`. Deferred: real PDF/OCR ingestion, prompt variants/evaluation, OpenTelemetry/Grafana, rate limiting, feedback aggregation, Locust measurements, and real university corpus confirmation.

