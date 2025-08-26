"""
MCP (Model Context Protocol) client for tool integrations.
"""

import asyncio
import json
import subprocess
from typing import Any, Dict, List, Optional

from ..config import Config
from ..llm_client import LLMClient


class MCPToolError(Exception):
    """Exception for MCP tool errors."""

    pass


class MCPClient:
    """MCP client for tool integrations."""

    def __init__(self, config: Config, node_name: str = None):
        self.config = config
        self.node_name = node_name
        self.node_config = config.get_node_config(node_name) if node_name else {}
        self.available_tools = self._check_available_tools()
        self.mcp_tools = self.node_config.get("mcp_tools", [])
        # Initialize LLM client for this node
        self.llm_client = LLMClient(config, node_name)

    def _check_available_tools(self) -> Dict[str, bool]:
        """Check which MCP tools are available."""
        # Check if we have any LLM provider that can be used for web search
        has_llm_provider = len(self.config.get_available_providers()) > 0

        tools = {
            "web_search": has_llm_provider,  # Any LLM provider can do web search via MCP
            "github": bool(self.config.github_token),
            "tavily": bool(self.config.tavily_api_key),
            "filesystem": True,  # Always available
        }
        return tools

    def get_available_tool_names(self) -> List[str]:
        """Get list of available tool names for this client."""
        if self.node_name:
            # Return only tools configured for this specific node
            return self.mcp_tools
        return [tool for tool, available in self.available_tools.items() if available]

    def has_tool(self, tool_name: str) -> bool:
        """Check if a specific tool is available to this client."""
        if self.node_name:
            return tool_name in self.mcp_tools and self.available_tools.get(tool_name, False)
        return self.available_tools.get(tool_name, False)

    async def _run_mcp_tool(self, tool_name: str, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run an MCP tool via subprocess."""
        try:
            # Check if this client has access to the tool
            if not self.has_tool(tool_name):
                raise MCPToolError(f"Tool '{tool_name}' not available to this client (node: {self.node_name})")

            # Construct the MCP tool call
            mcp_command = {"method": method, "params": params}

            # For now, simulate MCP calls - in a real implementation,
            # you would use the actual MCP protocol
            if tool_name == "web_search" and self.available_tools["web_search"]:
                return await self._simulate_web_search(params.get("query", ""))
            elif tool_name == "github" and self.config.github_token:
                return await self._simulate_github_search(params.get("query", ""))
            elif tool_name == "tavily" and self.config.tavily_api_key:
                return await self._simulate_tavily_search(params.get("query", ""))
            elif tool_name == "filesystem":
                return await self._simulate_filesystem_operation(params)

            return None

        except Exception as e:
            print(f"MCP tool {tool_name} failed: {e}")
            return None

    async def _simulate_web_search(self, query: str) -> Dict[str, Any]:
        """Simulate web search for MCP integration."""
        # In real implementation, this would call the actual web search MCP server
        provider_info = self.llm_client.get_provider_info()
        return {
            "results": [
                {
                    "title": f"Web search results for: {query}",
                    "url": "https://example.com/search",
                    "content": (
                        f"Simulated search results for query: {query}. "
                        f"Using {provider_info['provider']} ({provider_info['model']}) via MCP server. "
                        f"In production, this would use a real web search MCP server."
                    ),
                    "source": f"{provider_info['provider']}_mcp_simulated",
                }
            ]
        }

    async def _simulate_github_search(self, query: str) -> Dict[str, Any]:
        """Simulate GitHub search for MCP integration."""
        # In real implementation, this would call the actual GitHub MCP server
        return {
            "items": [
                {
                    "name": f"example-{query}.py",
                    "path": f"src/{query}/strategy.py",
                    "repository": {
                        "full_name": "example/quant-strategy",
                        "language": "Python",
                    },
                    "html_url": f"https://github.com/example/quant-strategy/blob/main/src/{query}/strategy.py",
                    "score": 1.0,
                }
            ]
        }

    async def _simulate_tavily_search(self, query: str) -> Dict[str, Any]:
        """Simulate Tavily search for MCP integration."""
        # In real implementation, this would call the actual Tavily MCP server
        return {
            "results": [
                {
                    "title": f"Research paper on {query}",
                    "url": f"https://example.com/research/{query}",
                    "content": (
                        f"Academic research findings related to {query}. "
                        f"In production, this would use Tavily's MCP server."
                    ),
                    "source": "tavily_mcp_simulated",
                }
            ]
        }

    async def _simulate_filesystem_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate filesystem operations for MCP integration."""
        operation = params.get("operation", "read")
        path = params.get("path", "/tmp/research.txt")

        return {
            "operation": operation,
            "path": path,
            "success": True,
            "message": f"Filesystem {operation} operation simulated for path: {path}",
        }

    async def web_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform web search via MCP."""
        if not self.available_tools["web_search"]:
            return []

        result = await self._run_mcp_tool("web_search", "search", {"query": query})
        if result and "results" in result:
            return result["results"]
        return []

    async def github_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search GitHub repositories via MCP."""
        if not self.available_tools["github"]:
            return []

        result = await self._run_mcp_tool("github", "search_code", {"query": query, "per_page": min(max_results, 100)})

        if result and "items" in result:
            github_results = []
            for item in result["items"]:
                github_results.append(
                    {
                        "name": item.get("name"),
                        "path": item.get("path"),
                        "repository": item.get("repository", {}).get("full_name"),
                        "html_url": item.get("html_url"),
                        "score": item.get("score"),
                        "language": item.get("repository", {}).get("language"),
                    }
                )
            return github_results
        return []

    async def tavily_search(self, query: str) -> List[Dict[str, Any]]:
        """Search via Tavily MCP server."""
        if not self.available_tools["tavily"]:
            return []

        result = await self._run_mcp_tool("tavily", "search", {"query": query, "max_results": 5})

        if result and "results" in result:
            return result["results"]
        return []

    async def generate_proposal(self, system_prompt: str, user_prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured proposal via LLM with multiple provider support."""
        if not self.available_tools["web_search"]:
            raise MCPToolError("No LLM provider available for proposal generation")

        try:
            # Use the unified LLM client for JSON completion
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            result = await self.llm_client.json_completion(messages=messages, json_schema=schema)

            return result

        except Exception as e:
            raise MCPToolError(f"Proposal generation failed: {str(e)}")

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the LLM provider being used."""
        return self.llm_client.get_provider_info()

    async def close(self):
        """Close MCP client resources."""
        # In a real MCP implementation, this would close active connections
        pass
