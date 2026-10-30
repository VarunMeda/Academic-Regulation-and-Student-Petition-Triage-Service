# Deployment guide

## Local application

Run `python -m app.ingest`, then `uvicorn app.main:app --reload`. Run `pytest -q` and `python evaluation/run_evaluation.py` from the repository root.

## Compose

Run `docker compose config`, then `docker compose up --build`.

The standard image installs `.[runtime]`, builds a synthetic lexical index, and runs API/worker/Redis/Prometheus. The named `run-data` volume persists SQLite run state. Install `.[semantic]` and supply a local model cache explicitly when a containerized semantic index is required. Model weights are not downloaded implicitly at startup.
