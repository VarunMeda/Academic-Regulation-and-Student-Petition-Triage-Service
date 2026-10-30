# Load-test report

`loadtests/locustfile.py` provides a synthetic submit/poll/result workload. Install `pip install -e ".[loadtest]"`, start the API/worker, and run `locust -f loadtests/locustfile.py --headless -u 5 -r 1 -t 60s --host http://localhost:8000`.

The declared initial complete-run SLO is p95 <= 10 seconds for the local deterministic worker path, chosen because the demonstration is an asynchronous workflow that should remain responsive under modest local concurrency. This is a target, not a measurement. No throughput, p50, p95, p99 or scaling result is reported until a repeatable Locust run is executed with Docker or a documented equivalent.
