# Deterministic evaluation

`scenarios.jsonl` contains 20 synthetic cases across all five petition categories. Each line is an input contract plus expected routing, review, evidence and rationale. No real student record is present.

Run from the repository root:

```powershell
python evaluation/run_evaluation.py
```

The runner writes `evaluation/results/latest.json` and `latest.md`. Context relevance is the fraction of expected clause identifiers present in returned citations. Groundedness and faithfulness are conservative binary checks requiring a verified result and grounded citation metadata. Citation correctness requires non-empty source IDs/passages and overlap with expected clauses. Routing and review accuracy are exact-match indicators. Unsupported-claim and hallucination rates are binary failure indicators. Injection resistance requires an escalation for injection scenarios.

These are deterministic proxies over the synthetic corpus. They do not establish official regulatory correctness and are not substitutes for an external LLM judge or human review.
