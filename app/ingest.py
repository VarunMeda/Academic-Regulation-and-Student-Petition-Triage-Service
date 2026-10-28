from .config import settings
from .corpus import ingest
if __name__ == "__main__":
    print(ingest(settings.corpus_dir, settings.index_path))

