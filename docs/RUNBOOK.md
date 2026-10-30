# Runbook

## Redis or worker unavailable

Symptom: `/health/ready` returns 503 or runs remain pending. Confirm Redis with `docker compose ps` and `docker compose logs redis worker`. Restart the affected service and inspect the shared `run-data` volume. Do not mark pending jobs completed manually; retry or escalate them after confirming queue contents.

## Missing or stale corpus index

Symptom: readiness reports an unavailable index or results escalate for every category. Confirm `INDEX_PATH`, inspect ingestion metadata and compare document versions/checksums. Re-run `python -m app.ingest` for the configured corpus, then restart API and worker. Never replace an official corpus with the synthetic fixture silently.

No production incident is claimed in this repository; development failures are recorded in command output and commit history rather than fabricated as incidents.
