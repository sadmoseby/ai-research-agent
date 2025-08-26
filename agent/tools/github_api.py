"""
GitHub API tools for prior art checking.
"""

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from ..config import Config


class GitHubAPI:
    """GitHub API client for code search."""

    def __init__(self, config: Config):
        self.token = config.github_token
        self.base_url = "https://api.github.com"

    async def search_code(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for code on GitHub."""
        if not self.token:
            return []

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "lean-research-agent",
        }

        params = {"q": query, "per_page": min(max_results, 100)}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/search/code",
                    headers=headers,
                    params=params,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("items", []):
                    results.append(
                        {
                            "name": item.get("name"),
                            "path": item.get("path"),
                            "repository": item.get("repository", {}).get("full_name"),
                            "html_url": item.get("html_url"),
                            "score": item.get("score"),
                            "language": item.get("repository", {}).get("language"),
                        }
                    )

                return results

            except httpx.HTTPError as e:
                print(f"GitHub API error: {e}")
                return []
            except Exception as e:
                print(f"Unexpected error in GitHub search: {e}")
                return []
