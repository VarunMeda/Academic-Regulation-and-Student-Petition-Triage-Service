# Technical report

The system is an advisory, evidence-backed triage service. FastAPI validates petitions, Redis decouples submission from worker execution, SQLite reconstructs run state, LangGraph separates analysis from research/verification, and local retrieval returns stable clause metadata. The default Docker runtime excludes embedding dependencies; semantic indexing is an explicit local step.

The critical synthetic scenario retrieves clauses 4.1 and 7.3 and routes to committee review because clause 7.3 retains committee discretion. The implementation does not claim official university applicability. Offline model cost is not applicable; no billable provider is configured. Performance measurements and load-test results are intentionally not reported until Locust and Docker are available.

The deterministic evaluation runner executed 22 synthetic scenarios on 2026-10-30. It reported context relevance 1.0, groundedness 0.5455, faithfulness 0.5455, citation correctness 1.0, routing accuracy 1.0, human-review accuracy 1.0, unsupported-claim rate 0.0, hallucination rate 0.0 and injection resistance 1.0. Groundedness and faithfulness are conservative proxies; lower values reflect escalated cases without verified claims and do not establish official regulatory quality.
