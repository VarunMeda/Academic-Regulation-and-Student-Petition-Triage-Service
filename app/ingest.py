import argparse
from .config import settings
from .corpus import ingest
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Build or rebuild the regulation index")
    parser.add_argument("--model-name", default=None, help="Optional sentence-transformers model; omit for deterministic offline index")
    args=parser.parse_args()
    print(ingest(settings.corpus_dir, settings.index_path, args.model_name))

