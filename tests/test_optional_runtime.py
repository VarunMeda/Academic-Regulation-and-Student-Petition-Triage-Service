import os
import pytest

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
