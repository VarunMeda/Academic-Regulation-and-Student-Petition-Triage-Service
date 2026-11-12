import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("DATABASE_PATH", "data/triage.db")
    corpus_dir: str = os.getenv("CORPUS_DIR", "corpus/synthetic")
    index_path: str = os.getenv("INDEX_PATH", "data/index.json")
    model_provider: str = os.getenv("MODEL_PROVIDER", "deterministic")
    retrieval_backend: str = os.getenv("RETRIEVAL_BACKEND", "lexical").lower()
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    hf_hub_offline: bool = os.getenv("HF_HUB_OFFLINE", "0").lower() in {"1", "true", "yes"}
    transformers_offline: bool = os.getenv("TRANSFORMERS_OFFLINE", "0").lower() in {"1", "true", "yes"}
    max_graph_steps: int = int(os.getenv("MAX_GRAPH_STEPS", "8"))
    max_tool_calls: int = int(os.getenv("MAX_TOOL_CALLS", "8"))
    run_timeout_seconds: int = int(os.getenv("RUN_TIMEOUT_SECONDS", "20"))
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    queue_backend: str = os.getenv("QUEUE_BACKEND", "memory")
    max_retries: int = int(os.getenv("MAX_RETRIES", "2"))
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    def __post_init__(self):
        if self.retrieval_backend not in {"lexical", "semantic"}:
            raise ValueError("RETRIEVAL_BACKEND must be lexical or semantic")

settings = Settings()

