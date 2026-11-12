# Retrieval and orchestration milestone

The ingestion command reads local text fixtures, keeps document/version/page/section/clause/passage identifiers, and writes a JSON index. A run can rebuild the index independently of the API. If `sentence-transformers` is installed, `--model-name` stores normalized local embeddings; `RegulationIndex` uses cosine similarity. `faiss-cpu` is an optional acceleration path for larger corpora. Without the optional packages, the service explicitly reports `embedding_backend=lexical` and uses deterministic token overlap for offline tests.

`RETRIEVAL_BACKEND` is explicit: `lexical` is the deterministic offline default and `semantic` requires a matching embedding index, Sentence Transformers model and FAISS index. API and worker construct `RegulationIndex` from the same `Settings` values, so semantic mode is not silently downgraded. A missing model, incompatible FAISS dimension, missing vector index or absent embeddings causes readiness/worker startup failure rather than a false semantic status. Set `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` when using a populated local model cache.

`RegulationIndex.as_langchain_retriever()` adapts returned passages into LangChain `Document` objects with complete metadata. `TriageGraph` builds a real two-node `StateGraph` when LangGraph is installed. The offline fallback preserves the same node boundaries and state hand-off, but is not claimed to be LangGraph execution.

The semantic integration test explicitly enables semantic mode and asserts model loading, embedding generation, FAISS persistence/reload, vector search and retrieval of clauses 4.1 and 7.3. It is skipped unless `TRIAGE_SEMANTIC_TEST=1` is set. The repository's supplied index is synthetic and must not be treated as official university policy.

The Research and Verification Agent chooses search queries, performs a second modifier search, and can use search, clause lookup, and validated petition-field tools. Calls and retries are bounded. Failures, injection markers, missing provisions, and failed citation verification produce `refer-to-committee` escalation.
