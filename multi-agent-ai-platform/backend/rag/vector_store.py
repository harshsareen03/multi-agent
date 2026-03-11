from __future__ import annotations

import hashlib
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings


def simple_embedding(text: str, dimensions: int = 128) -> list[float]:
    vector = [0.0] * dimensions
    tokens = text.lower().split()
    if not tokens:
        return vector
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        vector[index] += 1.0
    magnitude = sum(item * item for item in vector) ** 0.5 or 1.0
    return [item / magnitude for item in vector]


class SimpleVectorStore:
    def __init__(self, persist_directory: str = "./chroma_storage", collection_name: str = "documents") -> None:
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_documents(self, documents: list[dict[str, Any]]) -> None:
        if not documents:
            return
        self.collection.upsert(
            ids=[doc["id"] for doc in documents],
            documents=[doc["text"] for doc in documents],
            embeddings=[simple_embedding(doc["text"]) for doc in documents],
            metadatas=[doc.get("metadata", {}) for doc in documents],
        )

    def search(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        results = self.collection.query(query_embeddings=[simple_embedding(query)], n_results=limit)
        return [
            {
                "id": doc_id,
                "text": text,
                "metadata": metadata,
            }
            for doc_id, text, metadata in zip(
                results.get("ids", [[]])[0],
                results.get("documents", [[]])[0],
                results.get("metadatas", [[]])[0],
                strict=False,
            )
        ]

