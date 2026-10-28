"""Corpus ingestion and local-first semantic retrieval."""
import json, re, time
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class Chunk:
    source_id: str
    document: str
    version: str
    page: int
    section: str
    clause: str
    passage_id: str
    topic: str
    text: str

def chunk_text(text: str, document: str, page: int = 1, version: str = "synthetic-v1") -> list[Chunk]:
    chunks=[]
    for i, block in enumerate(re.split(r"\n\s*\n", text.strip())):
        if not block.strip(): continue
        m=re.search(r"(?:Clause|Section)\s+([\w.-]+)", block, re.I)
        clause=m.group(1) if m else f"paragraph-{i+1}"
        normalized=" ".join(block.split()); passage_id=f"passage-{i+1}"
        topic="attendance" if "attendance" in normalized.lower() else "general"
        source_id=f"{document}:{version}:p{page}:c{clause}:{passage_id}"
        chunks.append(Chunk(source_id, document, version, page, "Academic Regulations", clause, passage_id, topic, normalized))
    return chunks

def ingest(corpus_dir: str, index_path: str, model_name: str | None = None) -> dict:
    start=time.perf_counter(); chunks=[]; errors=[]; root=Path(corpus_dir)
    for path in sorted(root.glob("*.txt")):
        try: chunks.extend(chunk_text(path.read_text(encoding="utf-8"), path.name))
        except Exception as exc: errors.append({"file": path.name, "error": str(exc)})
    metadata={"built_at": time.time(), "documents": sorted({c.document for c in chunks}), "versions": sorted({c.version for c in chunks}), "chunks": len(chunks), "duration_seconds": round(time.perf_counter()-start,4), "errors": errors, "synthetic": True, "embedding_backend":"lexical"}
    payload={"metadata": metadata, "chunks": [asdict(c) for c in chunks]}
    if model_name:
        try:
            from sentence_transformers import SentenceTransformer
            model=SentenceTransformer(model_name)
            payload["embeddings"] = model.encode([c.text for c in chunks], normalize_embeddings=True).tolist()
            metadata["embedding_backend"]="sentence-transformers"; metadata["embedding_model"]=model_name
        except ImportError:
            errors.append({"embedding":"sentence-transformers unavailable; retained lexical index"}); metadata["errors"]=errors
    Path(index_path).parent.mkdir(parents=True, exist_ok=True)
    Path(index_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return metadata

class RegulationIndex:
    def __init__(self, index_path: str, model_name: str | None = None):
        p=Path(index_path)
        if not p.exists(): raise FileNotFoundError(f"No corpus index at {index_path}; run python -m app.ingest")
        self.data=json.loads(p.read_text(encoding="utf-8")); self.chunks=self.data["chunks"]; self.model=None
        if self.data.get("embeddings") and model_name:
            try:
                from sentence_transformers import SentenceTransformer
                self.model=SentenceTransformer(model_name)
            except ImportError: pass
    def search(self, query: str, limit: int = 5, filters: dict | None = None) -> list[dict]:
        candidates=[c for c in self.chunks if not filters or all(c.get(k)==v for k,v in filters.items())]
        if self.model and self.data.get("embeddings"):
            import numpy as np
            q=self.model.encode([query],normalize_embeddings=True)[0]
            scores=[(float(np.dot(q,e)),c) for e,c in zip(self.data["embeddings"],self.chunks) if c in candidates]
        else:
            terms=set(re.findall(r"[a-z0-9]+", query.lower())); scores=[]
            for c in candidates:
                words=set(re.findall(r"[a-z0-9]+", c["text"].lower())); score=len(terms & words)/max(1,len(terms))
                if score: scores.append((score,c))
        return [c for _,c in sorted(scores,key=lambda x:x[0],reverse=True)[:limit]]
    def lookup(self, clause_id: str) -> dict | None:
        return next((c for c in self.chunks if c["source_id"] == clause_id or c["clause"] == clause_id), None)

    def as_langchain_retriever(self):
        """Expose the index through LangChain when the optional package is installed."""
        try:
            from langchain_core.documents import Document
            from langchain_core.retrievers import BaseRetriever
            from pydantic import ConfigDict, PrivateAttr
        except ImportError as exc:
            raise RuntimeError("Install the full extra to use the LangChain retriever adapter") from exc
        owner=self
        class LocalRetriever(BaseRetriever):
            model_config=ConfigDict(arbitrary_types_allowed=True)
            _owner=PrivateAttr(default=owner)
            def _get_relevant_documents(self, query, *, run_manager=None):
                return [Document(page_content=c["text"], metadata={k:c[k] for k in ("source_id","document","version","page","section","clause","passage_id","topic")}) for c in self._owner.search(query)]
        return LocalRetriever()
