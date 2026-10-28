# Architecture and implementation status

```mermaid
flowchart LR
  Client --> API[FastAPI API]
  API --> Store[(SQLite run store)]
  API --> Worker[Async worker / agent graph]
  Worker --> Analyst[Petition Analyst]
  Analyst --> Research[Research + Verification Agent]
  Research --> Search[Regulation search tool]
  Search --> Index[(Synthetic indexed corpus)]
  Worker --> Store
  Prom[Prometheus] --> API
  Redis[(Redis, compose boundary)] -.future queue.-> Worker
```

The explicit hand-off is Analyst -> Research + Verification Agent. Tool calls are selected by the research worker, bounded by the graph policy, and every citation must resolve to a passage returned for the same run. Committee discretion produces escalation, not a fabricated grant.

