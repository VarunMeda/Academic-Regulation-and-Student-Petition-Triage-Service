import re
from .corpus import RegulationIndex
from .models import Citation, PetitionRequest, TriageResult
from .verification import verify

class PetitionAnalyst:
    def analyze(self, petition: PetitionRequest) -> dict:
        return {"category": petition.category.value, "facts": petition.model_dump(exclude_none=True), "query": f"{petition.category.value} {petition.description}", "handoff": "Research and Verification Agent"}

class ResearchVerificationAgent:
    def __init__(self, index: RegulationIndex): self.index=index
    def run(self, petition: PetitionRequest, analysis: dict) -> TriageResult:
        base=self.index.search(analysis["query"] + " prescribed minimum rule", 3)
        modifier=self.index.search("condonation medical grounds shortfall committee discretion", 3) if petition.category.value == "attendance" else []
        retrieved=[]
        for c in base+modifier:
            if c not in retrieved: retrieved.append(c)
        def cite(c): return Citation(source_id=c["source_id"],document=c["document"],page=c["page"],clause=c["clause"],passage=c["text"])
        base_c=next((cite(c) for c in base if "minimum attendance" in c["text"].lower() and "75 percent" in c["text"].lower()), None)
        mod_c=next((cite(c) for c in modifier if "condon" in c["text"].lower()), None)
        citations=[c for c in [base_c,mod_c] if c]
        if petition.category.value != "attendance":
            return TriageResult(petition_facts=analysis["facts"], proposed_eligibility="Insufficient verified corpus evidence.", routing="refer-to-committee", human_review_required=True, verification="escalated: category is not covered by the synthetic corpus", citations=[])
        if not base_c:
            return TriageResult(petition_facts=analysis["facts"], proposed_eligibility="Cannot determine safely.", routing="refer-to-committee", human_review_required=True, verification="escalated: governing provision not found", citations=[])
        within=petition.attendance_percentage is not None and petition.prescribed_minimum is not None and petition.attendance_percentage < petition.prescribed_minimum
        if within and petition.medical_documented and mod_c:
            claim="Attendance shortfall may be considered under the medical condonation provision, subject to committee review."
            ok,msg=verify(citations,retrieved,claim)
            return TriageResult(petition_facts=analysis["facts"],base_provision=base_c,modifying_provision=mod_c,proposed_eligibility=claim,routing="refer-to-committee",human_review_required=True,verification=msg,citations=citations)
        claim="The prescribed attendance requirement is not met on the supplied facts."
        ok,msg=verify([base_c],retrieved,claim)
        if not ok: return TriageResult(petition_facts=analysis["facts"],proposed_eligibility="Cannot determine safely.",routing="refer-to-committee",human_review_required=True,verification="escalated: verification failed",citations=[])
        return TriageResult(petition_facts=analysis["facts"],base_provision=base_c,proposed_eligibility=claim,routing="reject",human_review_required=False,verification=msg,citations=[base_c])

class TriageGraph:
    def __init__(self,index): self.analyst=PetitionAnalyst(); self.researcher=ResearchVerificationAgent(index)
    def invoke(self, petition):
        analysis=self.analyst.analyze(petition)
        return self.researcher.run(petition, analysis)

