# Retrieval and orchestration milestone

The ingestion command reads local text fixtures, keeps document/version/page/section/clause/passage identifiers, and writes a JSON index. A run can rebuild the index independently of the API. If `sentence-transformers` is installed, `--model-name` stores normalized local embeddings; `RegulationIndex` uses cosine similarity. `faiss-cpu` is an optional acceleration path for larger corpora. Without the optional packages, the service explicitly reports `embedding_backend=lexical` and uses deterministic token overlap for offline tests.

`RegulationIndex.as_langchain_retriever()` adapts returned passages into LangChain `Document` objects with complete metadata. `TriageGraph` builds a real two-node `StateGraph` when LangGraph is installed. The offline fallback preserves the same node boundaries and state hand-off, but is not claimed to be LangGraph execution.

Verification on 2026-10-28: the real LangGraph integration test passed. Semantic retrieval was not marked successful because FAISS was unavailable and the available Sentence Transformers import failed under the installed Transformers/Keras stack (`Keras 3` requires `tf-keras` for that version). The explicit embedding command therefore records the failure and retains the lexical backend. The project virtual environment could not install `.[full]` because the package index was unreachable.

The Research and Verification Agent chooses search queries, performs a second modifier search, and can use search, clause lookup, and validated petition-field tools. Calls and retries are bounded. Failures, injection markers, missing provisions, and failed citation verification produce `refer-to-committee` escalation.
