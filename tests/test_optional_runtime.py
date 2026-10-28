import os
import pytest
import sys
import time
import types

def test_semantic_runtime_is_not_mistaken_for_fallback(tmp_path):
    try:
        __import__("sentence_transformers")
    except Exception as exc:
        pytest.skip(f"sentence-transformers import is unavailable: {type(exc).__name__}")
    pytest.importorskip("faiss")
    if os.getenv("TRIAGE_SEMANTIC_TEST") != "1":
        pytest.skip("set TRIAGE_SEMANTIC_TEST=1 to download/use the configured embedding model")
    from app.corpus import ingest, RegulationIndex
    index_path=tmp_path / "semantic.json"
    meta=ingest("corpus/synthetic", str(index_path), os.getenv("TRIAGE_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    assert meta["embedding_backend"] == "sentence-transformers"
    assert meta["vector_index"] == "faiss"
    loaded=RegulationIndex(str(index_path), os.getenv("TRIAGE_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    assert loaded.vector_index is not None
    assert loaded.search("medical grounds attendance exception", 2)

def test_real_langgraph_runtime_executes_state_graph():
    pytest.importorskip("langgraph")
    from app.corpus import ingest, RegulationIndex
    from app.agents import TriageGraph
    from app.models import PetitionRequest
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        index_path=f"{directory}/index.json"; ingest("corpus/synthetic", index_path)
        graph=TriageGraph(RegulationIndex(index_path))
        assert graph.langgraph_available is True
        petition=PetitionRequest(category="attendance", description="Medical attendance shortfall", attendance_percentage=70, prescribed_minimum=75, medical_documented=True, condonation_requested=True)
        result=graph.invoke(petition)
        assert result.routing == "refer-to-committee" and len(result.citations) == 2

def test_ingestion_duration_includes_embedding_and_index_work(tmp_path, monkeypatch):
    import numpy as np
    from app.corpus import ingest
    class FakeModel:
        def __init__(self, name): pass
        def encode(self, texts, normalize_embeddings=True):
            time.sleep(0.02)
            return np.ones((len(texts), 4), dtype="float32")
    class FakeIndex:
        def __init__(self, dimension): self.dimension=dimension
        def add(self, matrix): self.count=len(matrix)
    fake_faiss=types.SimpleNamespace(IndexFlatIP=FakeIndex, write_index=lambda index, path: open(path, "wb").write(b"fake"))
    monkeypatch.setitem(sys.modules, "sentence_transformers", types.SimpleNamespace(SentenceTransformer=FakeModel))
    monkeypatch.setitem(sys.modules, "faiss", fake_faiss)
    metadata=ingest("corpus/synthetic", str(tmp_path / "index.json"), "fake-model")
    assert metadata["embedding_backend"] == "sentence-transformers"
    assert metadata["vector_index"] == "faiss"
    assert metadata["duration_seconds"] >= 0.02
