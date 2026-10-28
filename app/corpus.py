import json, re, time
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class Chunk:
    source_id: str
    document: str
    page: int
    section: str
    clause: str
    topic: str
    text: str

def chunk_text(text: str, document: str, page: int = 1) -> list[Chunk]:
    chunks=[]
    for i, block in enumerate(re.split(r"\n\s*\n", text.strip())):
        if not block.strip(): continue
        m=re.search(r"(?:Clause|Section)\s+([\w.-]+)", block, re.I)
        clause=m.group(1) if m else f"paragraph-{i+1}"
        topic="attendance" if "attendance" in block.lower() else "general"
        chunks.append(Chunk(f"{document}:p{page}:c{clause}", document, page, "Academic Regulations", clause, topic, " ".join(block.split())))
    return chunks

def ingest(corpus_dir: str, index_path: str) -> dict:
    start=time.perf_counter(); chunks=[]; errors=[]; root=Path(corpus_dir)
    for path in sorted(root.glob("*.txt")):
        try: chunks.extend(chunk_text(path.read_text(encoding="utf-8"), path.name))
        except Exception as exc: errors.append({"file": path.name, "error": str(exc)})
    Path(index_path).parent.mkdir(parents=True, exist_ok=True)
    metadata={"built_at": time.time(), "documents": sorted({c.document for c in chunks}), "chunks": len(chunks), "duration_seconds": round(time.perf_counter()-start,4), "errors": errors, "synthetic": True}
    Path(index_path).write_text(json.dumps({"metadata": metadata, "chunks": [asdict(c) for c in chunks]}, indent=2), encoding="utf-8")
    return metadata

class RegulationIndex:
    def __init__(self, index_path: str):
        p=Path(index_path)
        if not p.exists(): raise FileNotFoundError(f"No corpus index at {index_path}; run python -m app.ingest")
        self.data=json.loads(p.read_text(encoding="utf-8")); self.chunks=self.data["chunks"]
    def search(self, query: str, limit: int = 5) -> list[dict]:
        terms=set(re.findall(r"[a-z0-9]+", query.lower()))
        scored=[]
        for c in self.chunks:
            words=set(re.findall(r"[a-z0-9]+", c["text"].lower()))
            score=len(terms & words)/max(1,len(terms))
            if score: scored.append((score,c))
        return [c for _,c in sorted(scored,key=lambda x:x[0],reverse=True)[:limit]]
    def lookup(self, clause_id: str) -> dict | None:
        return next((c for c in self.chunks if c["source_id"] == clause_id or c["clause"] == clause_id), None)

