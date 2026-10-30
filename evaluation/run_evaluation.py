import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.agents import TriageGraph
from app.corpus import RegulationIndex
from app.models import PetitionRequest
from evaluation.metrics import aggregate, score

def main():
    index=RegulationIndex(str(ROOT/"data/index.json")); graph=TriageGraph(index)
    rows=[]
    for line in (ROOT/"evaluation/scenarios.jsonl").read_text(encoding="utf-8").splitlines():
        scenario=json.loads(line); fields={k:v for k,v in scenario.items() if k in PetitionRequest.model_fields}
        actual=graph.invoke(PetitionRequest.model_validate(fields)).model_dump()
        rows.append({"scenario_id":scenario["scenario_id"],"metrics":score(scenario,actual),"actual":actual,"expected":scenario})
    report={"scenario_count":len(rows),"synthetic":True,"metrics":aggregate(rows),"scenarios":rows}
    out=ROOT/"evaluation/results"; out.mkdir(parents=True,exist_ok=True)
    (out/"latest.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    lines=["# Evaluation Summary", "", f"Scenarios: {len(rows)}", "", "All cases use the synthetic development corpus. Metrics are deterministic proxies; they are not LLM-judge scores.", "", "| Metric | Value |", "|---|---:|"]
    lines += [f"| {k} | {v} |" for k,v in report["metrics"].items()]
    (out/"latest.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"scenario_count":len(rows),"metrics":report["metrics"]},indent=2))
if __name__ == "__main__": main()
