# Project Presentation & Live Demo Guide

## 1. Opening (30 seconds)

“Our project is an Academic Regulation and Student Petition Triage Service. It accepts a student petition, retrieves relevant regulation passages, verifies citations, and returns an advisory triage result. Cases involving missing evidence, conflicting information or committee discretion are routed for human review. It supports decision-making; it does not replace university authorities.”

## 2. Explain the architecture (60–90 seconds)

- **Next.js student portal:** petition form, dashboard, tracking and evidence display.
- **FastAPI backend:** validates requests, applies API guardrails and exposes the REST endpoints.
- **Petition Analyst:** extracts the submitted facts and prepares the retrieval request.
- **Research & Verification Agent:** retrieves base and modifying provisions, checks citation passages and selects a safe routing outcome.
- **Redis + worker:** decouple API acceptance from background processing in Docker Compose. The local development fallback uses an in-process queue.
- **SQLite:** stores run status, results, quarantine records and feedback.
- **Prometheus/Grafana/Jaeger:** provide metrics dashboards and optional distributed tracing when the Compose stack and runtime dependencies are running.

## 3. Live demo sequence (3–4 minutes)

1. Open `http://localhost:3001` and show the dashboard and API connection indicator.
2. Select **Submit petition**. Keep the default attendance category.
3. Enter a short description such as “Documented medical attendance shortfall; requesting review.”
4. Enter **70** for attendance and **75** for the supplied prescribed minimum.
5. Select both medical evidence and condonation request. Explain that this is a synthetic test case.
6. Review the details and submit. Explain that HTTP 202 means accepted for asynchronous processing, not approved.
7. On the tracking page, show the run reference and processing timeline.
8. Show the result: the system should retrieve synthetic Clause 4.1 (ordinary 75% minimum) and Clause 7.3 (medical condonation between 65% and the ordinary minimum), verify the passages, and route the case to committee review because the committee retains discretion.
9. Expand the citation panel to show source, page, clause and passage.
10. If time permits, show `/docs` for the API and Prometheus/Grafana for monitoring.

## 4. What to say about the result

“The submitted attendance is below the ordinary threshold. The retrieval step finds a modifying medical-condonation clause. The verifier checks that the cited clause exists in the retrieved corpus. Because the synthetic clause leaves the decision to a committee, the service does not approve the petition; it recommends authorised human review.”

## 5. Important honest limitations

- The included attendance rules are **synthetic demonstration clauses**, not official PES University or other university regulations.
- The current rule-based research/verification workflow only has specific regulation logic for attendance. Other accepted categories are safely escalated because the corpus does not cover them.
- The portal has no authentication. “My Petitions” displays run IDs saved in the current browser, not a secure student account history.
- PDF/OCR ingestion, production-grade shared rate limiting, measured load/scaling benchmarks and live LLM token/cost accounting are not part of the verified baseline.
- Groundedness and faithfulness in the 22-case synthetic evaluation are each 0.50. Do not claim perfect AI accuracy.
- Docker/Redis/Grafana/Jaeger deployment and the frontend production build must be verified on the presentation machine.

## 6. Before presenting

- [ ] Start Docker Desktop and wait until it is fully running.
- [ ] From the project root, run `docker compose up --build`.
- [ ] Wait for API, frontend, Redis and worker services to become healthy.
- [ ] Open `http://localhost:3001` and check the API indicator says connected.
- [ ] Open `http://localhost:8000/health/ready` and confirm it returns `ready`.
- [ ] Open `http://localhost:8000/docs` to confirm Swagger UI loads.
- [ ] Submit the 70% / 75% medical-condonation demo petition and confirm committee escalation plus both citations.
- [ ] Keep the result page open for the panel; have the architecture diagram and this guide ready.

## 7. Closing (20 seconds)

“The main contribution is a traceable and cautious workflow: validated input, asynchronous processing, retrieval of relevant provisions, citation verification, and explicit human-review routing. The prototype demonstrates the engineering workflow; real deployment requires an approved official regulation corpus, authentication, and operational validation.”
