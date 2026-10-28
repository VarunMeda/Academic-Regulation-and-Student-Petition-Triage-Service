# Academic Regulation and Student Petition Triage Service

Production-style mini-project core for evidence-backed, advisory petition triage. The repository currently uses a clearly labelled synthetic corpus; it must not be presented as an official university rule.

## Run locally

```powershell
python -m app.ingest
uvicorn app.main:app --reload
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

The core is dependency-light for offline development. Optional production integrations are declared in the `full` extra: LangGraph/LangChain, sentence-transformers, FAISS, Redis and PDF extraction. The current lexical index is a deterministic fallback; real corpus ingestion and vector re-embedding remain the next milestone.

## Status

Implemented: F1-F2, F4-F8 core path; A2-A4 core path; D1-D3 foundation; synthetic critical scenario, citation verification, async status persistence, health endpoints and tests.

Partial/deferred: real PDF/OCR ingestion, sentence-transformers/FAISS retrieval, Redis-backed worker queue, full LangGraph runtime, prompt variants/evaluation, OpenTelemetry/Grafana, rate limiting, feedback aggregation, Locust measurements, and real university corpus confirmation.

