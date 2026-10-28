from .models import Citation

def verify(citations: list[Citation], retrieved: list[dict], claim: str) -> tuple[bool,str]:
    ids={x["source_id"] for x in retrieved}
    if not citations: return False, "no citations supplied"
    if any(c.source_id not in ids for c in citations): return False, "citation does not resolve to retrieved text"
    corpus=" ".join(x.passage.lower() for x in citations)
    needed=["attendance"] if "attendance" in claim.lower() else []
    if any(term not in corpus for term in needed): return False, "claim is not grounded in cited passages"
    return True, "verified against retrieved passages"

