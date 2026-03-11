from __future__ import annotations

from rag.vector_store import SimpleVectorStore


class ChromaDatabase(SimpleVectorStore):
    def __init__(self) -> None:
        super().__init__(persist_directory="./chroma_storage", collection_name="agent_platform")
        self._seed()

    def _seed(self) -> None:
        self.add_documents(
            [
                {
                    "id": "doc-1",
                    "text": "LangGraph orchestrates stateful multi-agent workflows with graph nodes and edges.",
                    "metadata": {"topic": "langgraph"},
                },
                {
                    "id": "doc-2",
                    "text": "CrewAI defines role-based agent teams with goals, tasks, and delegation patterns.",
                    "metadata": {"topic": "crewai"},
                },
                {
                    "id": "doc-3",
                    "text": "AutoGen enables conversational collaboration between agents through message exchanges.",
                    "metadata": {"topic": "autogen"},
                },
            ]
        )

