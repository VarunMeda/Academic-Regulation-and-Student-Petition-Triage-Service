import argparse
from .config import settings
from .corpus import ingest
from .metrics import ingestion_duration, ingestion_chunks
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Build or rebuild the regulation index")
    parser.add_argument("--model-name", default=None, help="Optional sentence-transformers model; omit for deterministic offline index")
    args=parser.parse_args()
    metadata=ingest(settings.corpus_dir, settings.index_path, args.model_name)
    ingestion_duration.set(metadata["duration_seconds"]); ingestion_chunks.set(metadata["chunks"])
    print(metadata)

