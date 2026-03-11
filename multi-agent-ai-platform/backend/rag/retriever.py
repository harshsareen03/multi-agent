from __future__ import annotations

from database.chroma_db import ChromaDatabase


class RAGRetriever:
    def __init__(self, database: ChromaDatabase) -> None:
        self.database = database

    def retrieve(self, query: str) -> list[dict[str, object]]:
        return self.database.search(query)

