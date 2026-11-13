# Load-test report

`loadtests/locustfile.py` provides a synthetic submit/poll/result workload. Install `pip install -e ".[loadtest]"`, start the API/worker, and run:

```powershell
locust -f loadtests/locustfile.py --headless -u 5 -r 1 -t 60s --host http://localhost:8000
```

Latest synthetic run: 5 users for 60 seconds produced **505 requests** and **445 failures** (**88.12%**), primarily HTTP 429 responses from the configured API rate limiter. Aggregate HTTP request p95 was **24 ms**. The aggregate HTTP p95 is not the end-to-end petition completion latency.

The declared complete-run SLO is p95 <= 10 seconds for the local deterministic worker path. This run did **not** establish that SLO: the high failure rate means it is not a successful load benchmark, and no complete-run p50/p95/p99 or throughput claim should be made from it. Worker scaling with `docker compose --scale worker=3` remains unverified.
