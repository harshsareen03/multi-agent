from __future__ import annotations

import os
from typing import Any

import httpx
from langchain_core.tools import tool


@tool
def web_search(query: str) -> list[dict[str, Any]]:
    """Search the web for a query and return compact results."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [
            {
                "title": "Offline search result",
                "url": "https://example.com/search",
                "snippet": f"No search API key configured. Placeholder search result for: {query}",
            }
        ]
    response = httpx.post(
        "https://api.tavily.com/search",
        json={"api_key": api_key, "query": query, "max_results": 5},
        timeout=20.0,
    )
    response.raise_for_status()
    payload = response.json()
    return [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", ""),
        }
        for item in payload.get("results", [])
    ]


class WebSearchTool:
    def run(self, query: str) -> list[dict[str, Any]]:
        return web_search.invoke({"query": query})

