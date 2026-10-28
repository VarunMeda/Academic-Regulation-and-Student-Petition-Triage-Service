from app.corpus import chunk_text, RegulationIndex, ingest
from app.models import PetitionRequest
from app.agents import TriageGraph

def test_chunk_preserves_clause_context():
    chunks = chunk_text("Clause 4.1 Minimum Attendance. Attendance is 75 percent.", "x.txt")
    assert chunks[0].clause == "4.1" and "75" in chunks[0].text

def test_critical_case(tmp_path):
    corpus = tmp_path / "corpus"; corpus.mkdir()
    source = open("corpus/synthetic/attendance_rules.txt", encoding="utf-8").read()
    (corpus / "rules.txt").write_text(source, encoding="utf-8")
    index = tmp_path / "index.json"; ingest(str(corpus), str(index))
    graph = TriageGraph(RegulationIndex(str(index)))
    petition = PetitionRequest(category="attendance", description="Medical attendance shortfall", attendance_percentage=70, prescribed_minimum=75, medical_documented=True, condonation_requested=True)
    result = graph.invoke(petition)
    assert result.routing == "refer-to-committee" and len(result.citations) == 2
    assert result.verification.startswith("verified")

def test_validation_requires_attendance_fields():
    import pytest
    with pytest.raises(Exception): PetitionRequest(category="attendance", description="shortfall")

def test_unknown_citation_fails():
    from app.verification import verify
    from app.models import Citation
    citation = Citation(source_id="unknown", document="x", page=1, clause="1", passage="attendance")
    assert verify([citation], [{"source_id": "real", "text": "attendance"}], "attendance")[0] is False

def test_api_quarantines_malformed_request():
    from fastapi.testclient import TestClient
    from app.main import app
    response = TestClient(app).post("/api/petitions", json={"category": "attendance", "description": "bad"})
    assert response.status_code == 422
    assert response.json()["error"] == "validation_failed"
    assert "correlation_id" in response.json()

