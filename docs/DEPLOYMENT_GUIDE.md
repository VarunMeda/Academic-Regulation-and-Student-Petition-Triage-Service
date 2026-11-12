# Deployment guide

## Local application

Run `python -m app.ingest`, then `uvicorn app.main:app --reload`. Run `pytest -q` and `python evaluation/run_evaluation.py` from the repository root.

## Compose

Run `docker compose config`, then `docker compose up --build`.

The standard image installs `.[runtime]`, uses `RETRIEVAL_BACKEND=lexical`, builds a synthetic lexical index, and runs API/worker/Redis/Prometheus. The named `run-data` volume persists SQLite run state. For semantic containers, install `.[semantic]`, set `RETRIEVAL_BACKEND=semantic` and `EMBEDDING_MODEL`, and supply a local model cache explicitly. Model weights are not downloaded implicitly at startup. If semantic artifacts or the model are unavailable, readiness does not claim the service is ready.

For local semantic verification:

```powershell
$env:RETRIEVAL_BACKEND="semantic"
$env:EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
python -m app.ingest --model-name $env:EMBEDDING_MODEL
python -m pytest -q tests/test_optional_runtime.py::test_semantic_runtime_is_not_mistaken_for_fallback
```
