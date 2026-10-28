import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("DATABASE_PATH", "data/triage.db")
    corpus_dir: str = os.getenv("CORPUS_DIR", "corpus/synthetic")
    index_path: str = os.getenv("INDEX_PATH", "data/index.json")
    model_provider: str = os.getenv("MODEL_PROVIDER", "deterministic")
    max_graph_steps: int = int(os.getenv("MAX_GRAPH_STEPS", "8"))
    max_tool_calls: int = int(os.getenv("MAX_TOOL_CALLS", "8"))
    run_timeout_seconds: int = int(os.getenv("RUN_TIMEOUT_SECONDS", "20"))

settings = Settings()

