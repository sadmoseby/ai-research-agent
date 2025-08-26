"""
Tavily search tool for fallback web search.
"""

from typing import Any, Dict, List, Optional

import httpx

from ..config import Config


class TavilyTool:
    """Tavily search tool wrapper using direct API calls."""

    def __init__(self, config: Config):
        self.api_key = config.tavily_api_key
        self.base_url = "https://api.tavily.com"

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Perform web search using Tavily API directly."""
        if not self.api_key:
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "max_results": 5,
                        "search_depth": "basic",
                        "include_answer": True,
                        "include_raw_content": False,
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    results = []

                    for result in data.get("results", []):
                        results.append(
                            {
                                "title": result.get("title", ""),
                                "url": result.get("url", ""),
                                "content": result.get("content", ""),
                                "source": "tavily",
                            }
                        )

                    return results
                else:
                    print(f"Tavily API error: {response.status_code}")
                    return []

        except httpx.RequestError as e:
            print(f"Tavily search request failed: {e}")
            return []
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []
