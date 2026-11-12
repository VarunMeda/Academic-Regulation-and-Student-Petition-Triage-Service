# Project Requirements Audit

Audit refreshed: 2026-11-12, from the supplied `feature/petition-triage-core` project archive. Git branch metadata was not included in the archive. Evidence below is based on the repository contents and commands actually run in this workspace. The synthetic corpus is development-only and is not an official university regulation.

| Requirement | Existing implementation | Status | Missing work | Files involved | Tests/evidence |
|---|---|---|---|---|---|
| REST contract and validation | FastAPI/Pydantic petition contract, category/range/cross-field validation | COMPLETE AND VERIFIED | Publish formal OpenAPI examples | `app/main.py`, `app/models.py` | `pytest -q` |
| Quarantine malformed petitions | Validation handler persists field errors and correlation ID before queueing | COMPLETE AND VERIFIED | Quarantine inspection endpoint | `app/main.py`, `app/store.py` | API validation test |
| Async execution | Redis queue path, worker process, memory test fallback, SQLite status/result persistence | IMPLEMENTED BUT NOT VERIFIED | Docker/Redis execution requires Docker | `app/queue.py`, `app/worker.py`, `compose.yaml` | Memory queue integration test; Docker unavailable |
| Semantic retrieval | Sentence Transformers, FAISS persistence, metadata-preserving chunks | COMPLETE AND VERIFIED | Official PDF corpus | `app/corpus.py`, `app/ingest.py` | Semantic integration test with cached model |
| Official corpus | Synthetic attendance fixture only | BLOCKED BY EXTERNAL INPUT | Obtain and validate university regulations/bye-laws | `corpus/synthetic`, `docs/CORPUS_PROVENANCE.md` | No official source supplied |
| LangGraph agents | Real StateGraph path, analyst/research-verifier hand-off, bounded tools | COMPLETE AND VERIFIED | More conditional branches and provider abstraction | `app/agents.py` | LangGraph integration test |
| Citation verification | Retrieved-source IDs and passage grounding checked before verified result | COMPLETE AND VERIFIED | Conflict detector for real corpus versions | `app/verification.py` | Unsupported citation tests |
| Safe routing | `grant-under-provision`, `refer-to-committee`, `reject`; advisory notice | COMPLETE AND VERIFIED | More category-specific official provisions | `app/models.py`, `app/agents.py` | Critical scenario test |
| Redis retries/dead letter | Bounded retry counters and worker failure states | PARTIALLY IMPLEMENTED | Redis dead-letter runtime and restart test | `app/worker.py`, `app/queue.py` | Memory failure tests pending |
| Prometheus metrics | API, queue, worker, latency, agent and ingestion metrics | PARTIALLY IMPLEMENTED | Verify scrape targets in running Compose | `app/metrics.py`, `infra/prometheus.yml` | Endpoint smoke test; Docker unavailable |
| OpenTelemetry/tracing | Optional FastAPI instrumentation, OTLP exporter and W3C trace-context propagation helpers | IMPLEMENTED BUT NOT VERIFIED | Confirm runtime spans arrive in Jaeger | `app/tracing.py`, `app/main.py`, `app/worker.py`, `compose.yaml` | Code inspection; Docker/Jaeger runtime unavailable |
| Grafana dashboard | Compose service and provisioned Prometheus dashboard | IMPLEMENTED BUT NOT VERIFIED | Start and inspect Grafana | `compose.yaml`, `infra/grafana/` | Docker unavailable |
| 20-scenario evaluation | 22 deterministic JSONL scenarios and runner | COMPLETE AND VERIFIED | Expand after official corpus | `evaluation/` | Runner produced 22 cases and metrics |
| Load testing | Locust workload and declared SLO | IMPLEMENTED BUT NOT VERIFIED | Execute measurements and worker-scaling experiment | `loadtests/`, `docs/LOAD_TEST_REPORT.md` | No benchmark claimed |
| Token/cost accounting | No billable provider in default deterministic path | PARTIALLY IMPLEMENTED | Provider adapter and token hooks | `app/agents.py`, `docs/TECHNICAL_REPORT.md` | Cost is explicitly not applicable offline |
| Feedback | Validated run-linked feedback persistence | COMPLETE AND VERIFIED | Aggregate quality dashboard | `app/main.py`, `app/store.py` | Feedback API tests |
| Security/privacy | Synthetic-only policy, injection guard, no routine petition logging | PARTIALLY IMPLEMENTED | Payload-size/rate-limit/dependency audit | `docs/SECURITY.md`, `app/` | Injection and validation tests |
| Docker deployment | API/worker/Redis/Prometheus Compose definitions | IMPLEMENTED BUT NOT VERIFIED | Build and startup require Docker | `Dockerfile`, `compose.yaml` | YAML parse only; Docker unavailable |
| Documentation/reporting | README and architecture/retrieval docs | PARTIALLY IMPLEMENTED | Final report, runbook, incident/evaluation/load docs | `docs/` | Documentation files added in this milestone |

## Verification commands

```powershell
pytest -q
python evaluation/run_evaluation.py
python -c "import yaml; yaml.safe_load(open('compose.yaml')); print('compose YAML parsed')"
docker compose config
docker compose up --build
```

The last two commands require Docker and are not reported as passing unless Docker is available and the services actually start.


## Follow-up patch verification (2026-11-02)

- Fixed clean-start API initialization so a missing local index is built from the configured corpus automatically.
- Added a simple browser client at `/`, a feedback summary endpoint, a quarantine inspection endpoint, and a basic per-process API rate limit.
- Added regression tests for the browser client and quarantine/feedback endpoints.
- Refreshed local verification (2026-11-12): `python -m compileall -q app evaluation tests` passed; `pytest -q --ignore=tests/test_redis_resilience.py` reported **27 passed, 2 skipped**. The Redis resilience module could not be collected because the `redis` package is not installed in this environment and package installation was blocked by unavailable network access. Evaluation runner completed 22 synthetic scenarios: context relevance 1.0000, groundedness 0.5000, faithfulness 0.5000, citation correctness 1.0000, routing correctness 1.0000, human-review correctness 1.0000, unsupported claim 0.0000, hallucination 0.0000, injection resistance 1.0000.
- Docker CLI is not available in the build workspace; Docker Compose build/startup, Redis execution, Grafana/Jaeger runtime, and scaled-worker measurements remain unverified. Frontend dependencies were absent and `npm ci` could not reach the package registry, so the Next.js production build/type-check is not verified here. The UI source was updated, but run `npm ci` and `npm run build` on the presentation machine before claiming a successful frontend build.
