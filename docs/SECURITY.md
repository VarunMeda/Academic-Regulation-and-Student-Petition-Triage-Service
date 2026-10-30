# Security and privacy

The service accepts synthetic petitions only. Petition descriptions and retrieved passages are untrusted data; injection markers such as requests to ignore instructions, reveal prompts or bypass tools produce escalation. Tool selection is controlled by application code, not petition text.

Validation occurs before queueing. Idempotency keys prevent duplicate enqueueing. Queue payloads contain only the run ID, correlation ID, validated fields and retry attempt. Routine logs do not include petition descriptions. Secrets are runtime configuration only; `.env` files and credentials are ignored.

Known limitations: there is no authentication, per-client rate limit, payload-size middleware, or production secret manager. Compose is a local demonstration boundary, not an internet-facing deployment.
