"""Bounded, tool-using agent graph with an optional LangGraph runtime."""
import re, time
from typing import Any, TypedDict
from .corpus import RegulationIndex
from .models import Citation, PetitionRequest, TriageResult
from .verification import verify

class GraphState(TypedDict, total=False):
    petition: PetitionRequest
    analysis: dict[str, Any]
    result: TriageResult
    steps: int
    tool_calls: int
    handoff: str

class PetitionTools:
    def __init__(self, index: RegulationIndex, petition: PetitionRequest): self.index=index; self.petition=petition; self.calls=0
    def _call(self):
        self.calls += 1
        if self.calls > 8: raise RuntimeError("tool-call limit exceeded")
    def search_regulations(self, query: str, filters: dict | None = None) -> list[dict]:
        self._call(); return self.index.search(query, limit=5, filters=filters)
    def lookup_clause(self, clause_id: str) -> dict | None:
        self._call(); return self.index.lookup(clause_id)
    def get_petition_fields(self, run_id: str = "local") -> dict:
        self._call(); return self.petition.model_dump(exclude_none=True)

def _injection(text: str) -> bool:
    lowered=text.lower()
    return any(x in lowered for x in ("ignore previous", "ignore all instructions", "system prompt", "call this tool"))

class PetitionAnalyst:
    def analyze(self, petition: PetitionRequest, tools: PetitionTools) -> dict:
        if _injection(petition.description):
            return {"unsafe": True, "facts": petition.model_dump(exclude_none=True), "handoff": "blocked"}
        facts=tools.get_petition_fields()
        return {"category": petition.category.value, "facts": facts, "query": f"{petition.category.value} {petition.description}", "tool_plan":["search_regulations","lookup_clause","get_petition_fields"], "handoff":"Research and Verification Agent"}

class ResearchVerificationAgent:
    def run(self, petition: PetitionRequest, analysis: dict, tools: PetitionTools, max_retries: int = 2) -> TriageResult:
        if analysis.get("unsafe"):
            return TriageResult(petition_facts=analysis["facts"], proposed_eligibility="Untrusted petition text requires human review.", routing="refer-to-committee", human_review_required=True, verification="escalated: prompt-injection guardrail", citations=[])
        if petition.category.value != "attendance":
            return TriageResult(petition_facts=analysis["facts"], proposed_eligibility="Insufficient verified corpus evidence.", routing="refer-to-committee", human_review_required=True, verification="escalated: category is not covered by the synthetic corpus", citations=[])
        retrieved=[]
        for attempt in range(max_retries + 1):
            try:
                query=analysis["query"] + (" prescribed minimum attendance" if attempt == 0 else " attendance eligibility minimum rule")
                base=tools.search_regulations(query)
                modifier=tools.search_regulations("medical condonation shortfall committee discretion" if attempt == 0 else "attendance medical grounds exception")
                retrieved=list({c["source_id"]: c for c in base + modifier}.values())
                break
            except Exception:
                if attempt == max_retries: return self._escalated(analysis, "tool failure after bounded retries")
        def cite(c): return Citation(source_id=c["source_id"],document=c["document"],page=c["page"],clause=c["clause"],passage=c["text"])
        base_raw=next((c for c in retrieved if "minimum attendance" in c["text"].lower() and re.search(r"\bat least\s+\d+(?:\.\d+)?\s*percent", c["text"], re.I)), None)
        base_c=cite(base_raw) if base_raw else None
        mod_c=next((cite(c) for c in retrieved if "condon" in c["text"].lower()), None)
        if not base_c: return self._escalated(analysis, "governing base provision not found")
        minimum_match=re.search(r"\bat least\s+(\d+(?:\.\d+)?)\s*percent", base_c.passage, re.I)
        retrieved_minimum=float(minimum_match.group(1)) if minimum_match else None
        supplied_minimum=petition.prescribed_minimum
        if retrieved_minimum is None or supplied_minimum is None or petition.attendance_percentage is None:
            return self._escalated(analysis, "attendance threshold could not be established from verified evidence", base_c=base_c)
        conflicts=[]
        if abs(supplied_minimum - retrieved_minimum) > 1e-6:
            conflicts.append(f"supplied prescribed minimum {supplied_minimum:g}% conflicts with retrieved clause {base_c.clause} minimum {retrieved_minimum:g}%")
        below_ordinary=petition.attendance_percentage < retrieved_minimum
        if conflicts:
            citations=[base_c]
            if petition.medical_documented and petition.condonation_requested and mod_c:
                citations.append(mod_c)
            claim=(f"Attendance meets the supplied threshold of {supplied_minimum:g}%, but the supplied minimum conflicts with "
                   f"retrieved clause {base_c.clause} ({retrieved_minimum:g}%). No final eligibility determination is made.")
            return TriageResult(petition_facts=analysis["facts"],base_provision=base_c,modifying_provision=mod_c if len(citations) == 2 else None,
                proposed_eligibility=claim,routing="refer-to-committee",human_review_required=True,verification="escalated: conflicting attendance thresholds",
                conflicts=conflicts,citations=citations)
        if not below_ordinary:
            claim=(f"Attendance of {petition.attendance_percentage:g}% meets the retrieved ordinary minimum of "
                   f"{retrieved_minimum:g}%; this is an advisory threshold assessment and not a final institutional decision.")
            ok,msg=verify([base_c],retrieved,claim)
            if not ok: return self._escalated(analysis, "citation verification failed", base_c=base_c)
            return TriageResult(petition_facts=analysis["facts"],base_provision=base_c,proposed_eligibility=claim,
                routing="grant-under-provision",human_review_required=False,verification=msg,citations=[base_c])
        if petition.medical_documented and petition.condonation_requested and mod_c:
            modifier_match=re.search(r"not below\s+(\d+(?:\.\d+)?)\s*percent", mod_c.passage, re.I)
            condonation_floor=float(modifier_match.group(1)) if modifier_match else None
            citations=[base_c,mod_c]
            if condonation_floor is not None and petition.attendance_percentage < condonation_floor:
                claim=(f"Attendance is below the retrieved medical-condonation threshold of {condonation_floor:g}%; "
                       "the supplied evidence does not establish condonation eligibility and committee review is required.")
            else:
                claim="Attendance shortfall may be considered under the medical condonation provision, subject to committee review."
            ok,msg=verify(citations,retrieved,claim)
            if ok: return TriageResult(petition_facts=analysis["facts"],base_provision=base_c,modifying_provision=mod_c,proposed_eligibility=claim,routing="refer-to-committee",human_review_required=True,verification=msg,citations=citations)
            return self._escalated(analysis, "citation verification failed")
        claim=(f"Attendance of {petition.attendance_percentage:g}% is below the retrieved ordinary minimum of "
               f"{retrieved_minimum:g}% and no documented medical-condonation basis was supplied.")
        ok,msg=verify([base_c],retrieved,claim)
        if not ok: return self._escalated(analysis, "citation verification failed", base_c=base_c)
        return TriageResult(petition_facts=analysis["facts"],base_provision=base_c,proposed_eligibility=claim,routing="reject",human_review_required=False,verification=msg,citations=[base_c])
    def _escalated(self, analysis, reason, base_c=None):
        return TriageResult(petition_facts=analysis["facts"], base_provision=base_c, proposed_eligibility="Cannot determine safely.", routing="refer-to-committee", human_review_required=True, verification="escalated: " + reason, citations=[base_c] if base_c else [])

class TriageGraph:
    def __init__(self,index, max_steps: int = 8):
        self.index=index; self.analyst=PetitionAnalyst(); self.researcher=ResearchVerificationAgent(); self.max_steps=max_steps
        self.langgraph_available=False
        try:
            from langgraph.graph import StateGraph, START, END
            graph=StateGraph(GraphState)
            graph.add_node("petition_analyst", self._analyst_node); graph.add_node("research_verification", self._research_node)
            graph.add_edge(START,"petition_analyst"); graph.add_edge("petition_analyst","research_verification"); graph.add_edge("research_verification",END)
            self._compiled=graph.compile(); self.langgraph_available=True
        except ImportError: self._compiled=None
    def _analyst_node(self, state):
        tools=PetitionTools(self.index,state["petition"]); analysis=self.analyst.analyze(state["petition"],tools)
        return {"analysis":analysis,"handoff":"Petition Analyst -> Research and Verification Agent","steps":state.get("steps",0)+1}
    def _research_node(self, state):
        tools=PetitionTools(self.index,state["petition"]); result=self.researcher.run(state["petition"],state["analysis"],tools)
        return {"result":result,"steps":state.get("steps",0)+1,"tool_calls":tools.calls}
    def invoke(self, petition):
        if self._compiled:
            state=self._compiled.invoke({"petition":petition,"steps":0,"tool_calls":0})
            return state["result"]
        state={"petition":petition,"steps":0}; state.update(self._analyst_node(state)); state.update(self._research_node(state)); return state["result"]
