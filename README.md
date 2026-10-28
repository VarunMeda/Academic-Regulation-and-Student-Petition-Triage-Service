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

The core is dependency-light for offline development. The `full` extra provides LangGraph/LangChain and sentence-transformers/FAISS integrations. `python -m app.ingest` is idempotent and rebuilds only the index artifact; re-run it with a different model to re-embed without changing API or agent code. In this environment those optional packages were unavailable, so the tested index uses the explicit deterministic lexical fallback and the LangGraph runtime falls back to the same bounded two-node graph semantics.

## Status

Implemented and tested: F1-F2, F4-F8 core path; A1-A4 core path; D1-D3 foundation; metadata-preserving idempotent ingestion; optional semantic/LangChain adapters; bounded tool calls; injection escalation; synthetic critical scenario and citation verification.

Runtime verification: the real LangGraph `StateGraph` path passed its integration test. The semantic path was not counted as passed: FAISS is unavailable, and the globally visible Sentence Transformers stack fails import with a Keras 3 / `tf-keras` compatibility error, so explicit model ingestion reports lexical fallback. Installing `.[full]` into `.venv` was blocked by unavailable package-index access. Deferred: real PDF/OCR ingestion, Redis-backed worker queue, prompt variants/evaluation, OpenTelemetry/Grafana, rate limiting, feedback aggregation, Locust measurements, and real university corpus confirmation.

