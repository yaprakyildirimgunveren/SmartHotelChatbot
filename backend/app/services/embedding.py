import os
from functools import lru_cache
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    model_name = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
    return SentenceTransformer(model_name)
