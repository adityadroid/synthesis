"""Web search service for real-time information."""

import os
import json
from typing import Any
import httpx

from ..config import Settings


settings = Settings()


class SearchResult:
    """A single search result."""

    def __init__(
        self,
        title: str,
        url: str,
        snippet: str,
        source: str | None = None,
    ):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
        }


class SearchResponse:
    """Response from a web search."""

    def __init__(
        self,
        query: str,
        results: list[SearchResult],
        total_results: int | None = None,
    ):
        self.query = query
        self.results = results
        self.total_results = total_results

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_results": self.total_results,
        }


class SearchService:
    """Service for web search."""

    def __init__(self):
        self.serper_api_key = os.environ.get("SERPER_API_KEY", "")
        self.search_api_key = os.environ.get("SEARCH_API_KEY", "")

    def is_available(self) -> bool:
        """Check if search is configured."""
        return bool(self.serper_api_key or self.search_api_key)

    async def search(
        self,
        query: str,
        num_results: int = 10,
        source: str = "web",
    ) -> SearchResponse:
        """
        Perform a web search.

        Args:
            query: Search query
            num_results: Number of results to return (max 20)
            source: 'web', 'news', or 'images'
        """
        if not self.is_available():
            return SearchResponse(
                query=query,
                results=[],
            )

        num_results = min(num_results, 20)

        # Try Serper API first (better for AI use cases)
        if self.serper_api_key:
            return await self._search_serper(query, num_results, source)

        # Fallback to DuckDuckGo or similar
        return await self._search_fallback(query, num_results)

    async def _search_serper(
        self,
        query: str,
        num_results: int,
        source: str,
    ) -> SearchResponse:
        """Search using Serper API."""
        url = "https://google.serper.dev/search"

        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "q": query,
            "num": num_results,
        }

        if source == "news":
            url = "https://google.serper.dev/news"
        elif source == "images":
            url = "https://google.serper.dev/images"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()

                results = []
                items = (
                    data.get("organic", [])
                    or data.get("news", [])
                    or data.get("images", [])
                )

                for item in items[:num_results]:
                    if "title" in item and "link" in item:
                        results.append(
                            SearchResult(
                                title=item.get("title", ""),
                                url=item.get("link", ""),
                                snippet=item.get("snippet", ""),
                                source="Serper",
                            )
                        )

                return SearchResponse(
                    query=query,
                    results=results,
                    total_results=data.get("total", len(results)),
                )
        except Exception as e:
            return SearchResponse(
                query=query,
                results=[],
            )

    async def _search_fallback(
        self,
        query: str,
        num_results: int,
    ) -> SearchResponse:
        """Fallback search using DuckDuckGo HTML (no API key required)."""
        try:
            async with httpx.AsyncClient() as client:
                # DuckDuckGo Instant Answer API
                url = "https://api.duckduckgo.com/"
                params = {
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                    "skip_disambig": 1,
                }

                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                results = []

                # Add related topics
                for topic in data.get("RelatedTopics", [])[:num_results]:
                    if "Text" in topic and "FirstURL" in topic:
                        results.append(
                            SearchResult(
                                title=topic.get("Text", "").split(" - ")[0][:100],
                                url=topic.get("FirstURL", ""),
                                snippet=topic.get("Text", ""),
                                source="DuckDuckGo",
                            )
                        )

                return SearchResponse(
                    query=query,
                    results=results,
                    total_results=len(results),
                )
        except Exception:
            return SearchResponse(
                query=query,
                results=[],
            )

    def format_results_for_llm(self, response: SearchResponse) -> str:
        """Format search results for LLM consumption."""
        if not response.results:
            return "No search results found."

        formatted = [f"Search results for '{response.query}':\n"]

        for i, result in enumerate(response.results, 1):
            formatted.append(f"{i}. {result.title}")
            formatted.append(f"   URL: {result.url}")
            formatted.append(f"   {result.snippet}")
            formatted.append("")

        return "\n".join(formatted)


search_service = SearchService()
