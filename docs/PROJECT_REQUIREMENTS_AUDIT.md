# Project Requirements Audit

Audit baseline: 2026-10-30, branch `feature/petition-triage-core`. Evidence below is based on the repository contents and commands actually run in this workspace. The synthetic corpus is development-only and is not an official university regulation.

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
| OpenTelemetry/tracing | Architecture leaves extension points only | NOT IMPLEMENTED | Add OTEL spans and Jaeger/Tempo | `compose.yaml`, `app/` | No runtime evidence |
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
