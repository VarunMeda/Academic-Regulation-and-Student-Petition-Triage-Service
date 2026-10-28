from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

api_requests = Counter("triage_api_requests_total", "API requests", ["method", "path", "status"])
api_errors = Counter("triage_api_errors_total", "API errors", ["path"])
queue_depth = Gauge("triage_queue_depth", "Queued petition jobs")
worker_tasks = Counter("triage_worker_tasks_total", "Worker task outcomes", ["outcome"])
processing_latency = Histogram("triage_processing_seconds", "Complete processing latency")
agent_steps = Counter("triage_agent_steps_total", "Agent graph steps")
tool_calls = Counter("triage_tool_calls_total", "Agent tool calls")
escalations = Counter("triage_escalations_total", "Escalated runs", ["reason"])
retries = Counter("triage_retries_total", "Retried jobs")
ingestion_duration = Gauge("triage_ingestion_duration_seconds", "Last corpus ingestion duration")
ingestion_chunks = Gauge("triage_ingestion_chunks", "Last corpus chunk count")

def render_metrics():
    return generate_latest(), CONTENT_TYPE_LATEST
