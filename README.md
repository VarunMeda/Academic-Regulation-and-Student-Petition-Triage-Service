# Academic Regulation and Student Petition Triage Service

A production-style, local Docker Compose mini-project for **advisory** student-petition triage. It validates petitions, runs a two-role agent workflow, retrieves regulation passages, verifies citations and escalates unsupported or discretionary cases to a human examination officer.

> **Important corpus limitation:** `corpus/synthetic/attendance_rules.txt` contains synthetic demonstration clauses only. It is not an official PESU regulation or legal/academic authority. Replace it with the selected university's current academic regulations and examination bye-laws, record their source URLs/version/date, and rebuild the index before making claims about real eligibility.

## Quick start (Windows / VS Code)

Requirements: Docker Desktop with WSL2 backend, Git, and at least 6 GB free memory.

1. Extract the ZIP and open the project root in VS Code.
2. Copy `.env.example` to `.env` (the defaults are suitable for local demo).
3. In the VS Code terminal run:

```powershell
docker compose up --build
```

4. Open:
   - Web client: http://localhost:8000/
   - API docs: http://localhost:8000/docs
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000
   - Jaeger UI: http://localhost:16686

The Compose stack contains API, worker, Redis, Prometheus, Grafana and Jaeger. API submission is asynchronous: it returns a `run_id`; poll `/api/runs/{run_id}` until `completed`, `escalated` or `failed`, then read `/api/runs/{run_id}/result`. The worker uses Redis in Compose. Run data is stored in a named Docker volume.

To stop:

```powershell
docker compose down
```

To remove demo data too:

```powershell
docker compose down -v
```

## Local development without Docker

Use Python 3.11 or newer:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python -m app.ingest
uvicorn app.main:app --reload
```

This uses the in-process queue fallback. In another terminal, run tests:

```powershell
python -m pip install -e ".[test]"
pytest -q
python evaluation/run_evaluation.py
```

## Demonstration petition

The browser form defaults to the required difficult synthetic scenario: attendance 70%, prescribed minimum 75%, medical evidence present, condonation requested. It should be routed to committee review with both the base attendance clause and the separate medical-condonation clause cited. The system does not grant or reject a real student's petition.

Equivalent API request:

```powershell
$body = @{
  category = "attendance"
  description = "Documented medical attendance shortfall"
  attendance_percentage = 70
  prescribed_minimum = 75
  medical_documented = $true
  condonation_requested = $true
} | ConvertTo-Json
$response = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/petitions -ContentType "application/json" -Body $body
$response.run_id
Invoke-RestMethod "http://localhost:8000/api/runs/$($response.run_id)"
Invoke-RestMethod "http://localhost:8000/api/runs/$($response.run_id)/result"
```

## API surface

| Endpoint | Purpose |
|---|---|
| `POST /api/petitions` | Validate and enqueue a petition; returns 202 and run ID |
| `GET /api/runs/{run_id}` | Poll run state |
| `GET /api/runs/{run_id}/result` | Read terminal advisory result |
| `POST /api/feedback` | Store caller feedback linked to a run |
| `GET /api/feedback/summary` | Aggregate feedback counts/rates |
| `GET /api/quarantine` | Inspect malformed requests and field errors |
| `GET /health/live` | Liveness probe |
| `GET /health/ready` | Readiness probe |
| `GET /metrics` | Prometheus metrics |
| `GET /docs` | OpenAPI/Swagger documentation |

`Idempotency-Key` prevents duplicate submissions. `X-Correlation-ID` can be supplied by clients and is returned with the run. API input validation occurs before a job is enqueued; rejected payloads are quarantined with field-level errors. A basic per-process API rate limit is configurable with `RATE_LIMIT_PER_MINUTE`; for multi-replica production use a shared gateway or Redis-backed limiter.

## Architecture

- **Petition Analyst**: validates/normalises the facts, classifies the request, and selects retrieval queries.
- **Research & Verification Agent**: searches base and modifying provisions, checks citation IDs/passages against retrieved text, and escalates if evidence is missing.
- **Tools**: corpus search, clause lookup, and lookup of petition fields.
- **Queue**: Redis separates API submission from worker execution.
- **Persistence**: SQLite stores run state, quarantine records and feedback.
- **Retrieval**: explicit `RETRIEVAL_BACKEND=lexical|semantic`; lexical is the offline default, while semantic mode loads the configured Sentence Transformers model and validates the FAISS artifact in both API and worker paths.
- **Monitoring**: Prometheus scrape config, provisioned Grafana dashboard, and Jaeger service are included.

## Corpus ingestion

Place `.txt` files in `corpus/synthetic/` (or set `CORPUS_DIR` to your source directory) and run:

```powershell
python -m app.ingest
```

To build a local embedding index (requires model download and the optional ML dependencies):

```powershell
python -m pip install -e ".[semantic]"
python -m app.ingest --model-name sentence-transformers/all-MiniLM-L6-v2
```

The index records document names, versions, chunk counts and build time. Keep the official source PDFs and their provenance in the repository only if redistribution is permitted. The supplied CLI's deterministic text ingestion is the tested default; PDF/OCR ingestion is not included in this baseline.

## Tests and evaluation

```powershell
pytest -q
python evaluation/run_evaluation.py
```

The evaluation runner includes 22 synthetic scenarios. In the prepared workspace, the latest deterministic evaluation reported context relevance 1.0000, groundedness 0.5455, faithfulness 0.5455, citation correctness 1.0000, routing correctness 1.0000, human-review correctness 1.0000, unsupported claim 0.0000, hallucination 0.0000 and injection resistance 1.0000. These are synthetic-rule test results, not evidence of accuracy on real university regulations. Investigate low groundedness/faithfulness before presenting quality claims.

## Known limitations — do not claim these are complete

- No official university regulation corpus has been supplied or validated. The included corpus is synthetic.
- Docker image build, Redis worker execution, `docker compose up`, service health and `docker compose --scale worker=3` must be run on the user's machine; they have not been verified in this workspace.
- OpenTelemetry OTLP export and W3C queue context propagation are wired when the runtime extra is installed; Jaeger trace ingestion remains deployment-dependent and is not verified in this workspace.
- PDF/OCR ingestion is not implemented in this baseline.
- Locust scripts are included, but no measured throughput/p50/p95 or scaling benchmark is claimed. Run the tests and record the output on your machine.
- The deterministic baseline does not call a paid LLM provider; per-call token/cost accounting and a live model circuit breaker are therefore not applicable yet.
- Prompt-variant comparison and before/after TruLens-style evaluation need additional implementation and real corpus-grounded expected answers.
- The in-memory rate limiter is per process; use a shared gateway/Redis implementation for multiple API replicas.

Do not edit evaluation reports to claim measurements you have not run. Keep incident logs to genuine development incidents only.
