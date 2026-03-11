from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.web_search import WebSearchTool


@dataclass
class ResearchAgent:
    role: str = "Internet researcher"
    goal: str = "Find information about a topic"

    def __post_init__(self) -> None:
        self.tool = WebSearchTool()

    def run(self, query: str, retrieved_context: list[dict[str, Any]]) -> dict[str, Any]:
        search_results = self.tool.run(query=query)
        notes = [
            f"Retrieved context count: {len(retrieved_context)}",
            f"Search results count: {len(search_results)}",
        ]
        summary = (
            f"Research findings for '{query}'. "
            f"Key evidence collected from vector memory and web search."
        )
        return {
            "agent": "Research Agent",
            "role": self.role,
            "goal": self.goal,
            "summary": summary,
            "notes": notes,
            "sources": search_results,
            "context": retrieved_context,
        }

