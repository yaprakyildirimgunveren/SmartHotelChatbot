import os
from typing import List, Dict, Any
import chromadb

from .embedding import get_model


def _get_client() -> chromadb.PersistentClient:
    path = os.getenv("CHROMA_PATH", "chroma_db")
    return chromadb.PersistentClient(path=path)


def get_collection():
    client = _get_client()
    return client.get_or_create_collection(name="faq")


def ensure_seeded(items: List[Dict[str, Any]]) -> None:
    collection = get_collection()
    existing = collection.count()
    if existing > 0:
        return

    model = get_model()
    texts = [item["question"] + " " + item["answer"] for item in items]
    embeddings = model.encode(texts).tolist()
    ids = [f"faq-{index}" for index in range(len(items))]
    metadatas = [{"answer": item["answer"], "tags": item.get("tags", [])} for item in items]

    collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)


def query_faq(question: str, n_results: int = 1):
    collection = get_collection()
    model = get_model()
    embedding = model.encode([question]).tolist()[0]
    return collection.query(query_embeddings=[embedding], n_results=n_results)
