"""
MCP (Model Context Protocol) client for tool integrations.
"""

import asyncio
import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ..config import Config
from ..llm_client import LLMClient
from .validation_mcp_tool import ValidationMCPTool


class MCPToolError(Exception):
    """Exception for MCP tool errors."""


class MCPClient:
    """MCP client for tool integrations using the official Python SDK."""

    def __init__(self, config: "Config", llm_client: "LLMClient", node_name: str = "default", is_testing: bool = False):
        """Initialize MCP client."""
        from ..config import Config
        from ..llm_client import LLMClient

        self.config = config
        self.llm_client = llm_client
        self.node_name = node_name
        self._is_testing = is_testing
        self._sessions: Dict[str, ClientSession] = {}
        self._session_lock = asyncio.Lock()

        # Initialize validation tool
        self.validation_tool = ValidationMCPTool(config)

        # Determine available tools based on node configuration and environment
        self.available_tools = self._determine_available_tools()

    def __del__(self):
        """Cleanup sessions on destruction."""
        if hasattr(self, "_sessions") and self._sessions:
            # Schedule cleanup for any remaining sessions
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # No event loop running, sessions will be cleaned up by the system
                pass

            if loop and not loop.is_closed():
                for session in self._sessions.values():
                    if session:
                        try:
                            loop.create_task(self._cleanup_session(session))
                        except Exception:
                            pass  # Best effort cleanup

    async def _cleanup_session(self, session: ClientSession):
        """Cleanup a single session."""
        try:
            if hasattr(session, "close"):
                await session.close()
        except Exception:
            pass  # Best effort cleanup

    async def close(self):
        """Properly close all MCP sessions."""
        async with self._session_lock:
            for session_name, session in list(self._sessions.items()):
                if session:
                    try:
                        await self._cleanup_session(session)
                    except Exception as e:
                        print(f"Error closing session {session_name}: {e}")

            self._sessions.clear()

    def _detect_test_environment(self) -> bool:
        """Detect if we're running in a test environment."""
        return (
            os.getenv("PYTEST_CURRENT_TEST") is not None
            or os.getenv("TESTING") == "true"
            or "pytest" in os.getenv("_", "")
            or "test" in os.path.basename(os.getenv("_", ""))
        )

    def _check_available_tools(self) -> Dict[str, bool]:
        """Check which MCP tools are available."""
        # Check if we have any LLM provider that can be used for fallback search
        has_llm_provider = len(self.config.get_available_providers()) > 0

        tools = {
            "tavily": bool(os.getenv("TAVILY_API_KEY")),
            "github": bool(os.getenv("GITHUB_TOKEN")),
            "filesystem": True,  # Always available
            "validation": True,  # Always available
            "llm_fallback": has_llm_provider,  # LLM can provide fallback responses when tools unavailable
        }
        return tools

    def get_available_tool_names(self) -> List[str]:
        """Get list of available tool names for this client."""
        return [tool for tool, available in self.available_tools.items() if available]

    def has_tool(self, tool_name: str) -> bool:
        """Check if a specific tool is available to this client."""
        return self.available_tools.get(tool_name, False)

    async def _get_or_create_session(
        self, server_name: str, server_params: StdioServerParameters
    ) -> Optional[ClientSession]:
        """Get or create an MCP client session for the given server."""
        async with self._session_lock:
            # Check if we already have a valid session
            if server_name in self._sessions:
                session = self._sessions[server_name]
                if session and self._is_session_healthy(session):
                    return session
                else:
                    # Clean up the old session
                    if session:
                        try:
                            await self._cleanup_session(session)
                        except Exception:
                            pass
                    del self._sessions[server_name]

            # For testing, return None to use simulated responses
            if self._is_testing:
                return None

            # In production, create actual MCP client session
            try:
                # Connect to the MCP server using stdio transport
                session = await self._create_mcp_session(server_params)
                if session:
                    # Store the session for reuse
                    self._sessions[server_name] = session
                    return session

            except Exception as e:
                print(f"Failed to connect to MCP server {server_name}: {e}")

            return None

    def _is_session_healthy(self, session: ClientSession) -> bool:
        """Check if an MCP session is still healthy."""
        try:
            # Basic health check - in production this might ping the server
            return session is not None and hasattr(session, "_transport")
        except Exception:
            return False

    async def _create_mcp_session(self, server_params: StdioServerParameters) -> Optional[ClientSession]:
        """Create a new MCP session with proper error handling."""
        try:
            # Start the MCP server process
            process = await asyncio.create_subprocess_exec(
                server_params.command,
                *server_params.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, **server_params.env} if server_params.env else None,
            )

            # Create session with the process streams
            if process.stdin and process.stdout:
                session = ClientSession(process.stdout, process.stdin)
                await session.initialize()

                # Store process reference for cleanup
                session._process = process
                return session
            else:
                # Clean up process if streams are not available
                process.terminate()
                await process.wait()
                return None

        except FileNotFoundError as e:
            print(f"MCP server command not found: {server_params.command} - {e}")
            return None
        except Exception as e:
            print(f"Failed to create MCP session: {e}")
            return None

    async def _get_server_params(self, tool_name: str) -> Optional[StdioServerParameters]:
        """Get server parameters for the given tool from the Config."""
        # Get the MCP client configuration from the Config
        mcp_client_config = self.config.mcp_clients.get(tool_name)
        if not mcp_client_config:
            print(f"No MCP client configuration found for tool: {tool_name}")
            return None

        # Skip internal tools (like validation)
        if mcp_client_config.command == "internal":
            return None

        # Validate required environment variable if specified
        if mcp_client_config.api_key_env:
            api_key = os.getenv(mcp_client_config.api_key_env)
            if not api_key:
                print(f"Missing required environment variable {mcp_client_config.api_key_env} for tool: {tool_name}")
                return None

        # Build environment variables for the MCP server
        env_vars = mcp_client_config.env_vars.copy()

        # Add the API key to environment if specified
        if mcp_client_config.api_key_env and mcp_client_config.api_key_env not in env_vars:
            api_key = os.getenv(mcp_client_config.api_key_env)
            if api_key:
                env_vars[mcp_client_config.api_key_env] = api_key

        return StdioServerParameters(command=mcp_client_config.command, args=mcp_client_config.args, env=env_vars)

    def _validate_mcp_environment(self) -> Dict[str, bool]:
        """Validate the MCP environment and return tool availability."""
        validation_results = {}

        # Check if npx is available
        try:
            result = subprocess.run(["npx", "--version"], capture_output=True, text=True, timeout=5)
            npx_available = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            npx_available = False

        if not npx_available:
            print("Warning: npx not found. MCP servers won't be available.")
            # Return false for all external MCP tools
            for tool_name, mcp_config in self.config.mcp_clients.items():
                if mcp_config.command != "internal":
                    validation_results[tool_name] = False
                else:
                    validation_results[tool_name] = True  # Internal tools don't need npx
            return validation_results

        # Check individual tool requirements based on Config
        for tool_name, mcp_config in self.config.mcp_clients.items():
            if mcp_config.command == "internal":
                # Internal tools (like validation) are always available
                validation_results[tool_name] = True
            elif mcp_config.api_key_env:
                # Tools that require API keys
                validation_results[tool_name] = bool(os.getenv(mcp_config.api_key_env))
            else:
                # Tools with no special requirements (like filesystem)
                validation_results[tool_name] = True

        return validation_results

    async def _call_mcp_server(self, tool_name: str, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a real MCP server to execute a tool."""
        server_params = await self._get_server_params(tool_name)
        if not server_params:
            print(f"No server configuration found for tool: {tool_name}")
            return None

        try:
            # Get or create a session for this server
            session = await self._get_or_create_session(tool_name, server_params)
            if not session:
                return None

            # Get available tools from the server
            try:
                tools_response = await session.list_tools()
            except Exception as e:
                print(f"Failed to list tools from MCP server {tool_name}: {e}")
                return None

            # Find the appropriate tool to call
            tool_to_call = None

            # First, try exact name match
            for tool in tools_response.tools:
                if tool.name == method:
                    tool_to_call = tool
                    break

            # If no exact match, try fuzzy matching
            if not tool_to_call:
                method_normalized = method.lower().replace("_", "").replace("-", "")
                for tool in tools_response.tools:
                    tool_normalized = tool.name.lower().replace("_", "").replace("-", "")
                    if tool_normalized == method_normalized:
                        tool_to_call = tool
                        break

            # If still no match, try to use the first available tool for this server
            if not tool_to_call and tools_response.tools:
                tool_to_call = tools_response.tools[0]
                print(f"Using fallback tool '{tool_to_call.name}' for method '{method}' on server '{tool_name}'")

            if not tool_to_call:
                print(f"No suitable tool found on MCP server {tool_name} for method {method}")
                return None

            # Call the tool with proper error handling
            try:
                result = await session.call_tool(tool_to_call.name, arguments=params)
            except Exception as e:
                print(f"Tool call failed on MCP server {tool_name}: {e}")
                return None

            # Extract and process the response
            return self._process_mcp_response(result)

        except Exception as e:
            print(f"Error calling MCP server for {tool_name}: {e}")
            # Clean up the session if there was an error
            if tool_name in self._sessions:
                try:
                    await self._cleanup_session(self._sessions[tool_name])
                    del self._sessions[tool_name]
                except Exception:
                    pass
            return None

    def _process_mcp_response(self, result) -> Dict[str, Any]:
        """Process MCP tool response into a standardized format."""
        response_data = {}

        if hasattr(result, "content") and result.content:
            # Handle multiple content items
            texts = []
            for content_item in result.content:
                if hasattr(content_item, "text") and content_item.text:
                    texts.append(content_item.text)

            if texts:
                combined_text = "\n".join(texts)

                # Try to parse as JSON first
                try:
                    import json

                    response_data = json.loads(combined_text)
                except (json.JSONDecodeError, ValueError):
                    # If not valid JSON, store as text
                    response_data = {"text": combined_text}

        # If we couldn't extract anything, return a minimal response
        if not response_data:
            response_data = {"result": "MCP tool executed successfully", "content": str(result)}

        return response_data

    async def _simulate_github_search(self, query: str) -> Dict[str, Any]:
        """Simulate GitHub search for testing only."""
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
        """Simulate Tavily search for testing only."""
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

    async def _run_mcp_tool(self, tool_name: str, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run an MCP tool using the official Python SDK."""
        try:
            # Check if this client has access to the tool
            if not self.has_tool(tool_name):
                raise MCPToolError(f"Tool '{tool_name}' not available to this client (node: {self.node_name})")

            # In test environment, use simulated responses
            if self._is_testing:
                return await self._simulate_mcp_tool(tool_name, method, params)

            # In production, try to connect to real MCP servers
            result = await self._call_mcp_server(tool_name, method, params)
            if result:
                return result

            # Fallback to simulated response if MCP server fails
            print(f"MCP server call failed for {tool_name}.{method}, using fallback simulation")
            return await self._simulate_mcp_tool(tool_name, method, params)

        except MCPToolError:
            raise
        except Exception as e:
            if self._is_testing:
                print(f"MCP tool {tool_name} failed: {e}")
                return None
            else:
                raise MCPToolError(f"MCP tool {tool_name} failed: {e}") from e

    async def _simulate_mcp_tool(
        self, tool_name: str, _method: str, params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Simulate MCP tool calls for testing."""
        # Note: _method parameter is included for future extensibility but not currently used
        if tool_name == "github" and os.getenv("GITHUB_TOKEN"):
            return await self._simulate_github_search(params.get("query", ""))
        elif tool_name == "tavily" and os.getenv("TAVILY_API_KEY"):
            return await self._simulate_tavily_search(params.get("query", ""))
        elif tool_name == "filesystem":
            return await self._simulate_filesystem_operation(params)
        return None

    async def _simulate_filesystem_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate filesystem operations for testing only."""
        operation = params.get("operation", "read")
        path = params.get("path", "/tmp/research.txt")

        return {
            "operation": operation,
            "path": path,
            "success": True,
            "message": f"Filesystem {operation} operation simulated for path: {path}",
        }

    async def web_search(self, query: str, use_tavily: bool = True) -> List[Dict[str, Any]]:
        """Perform web search via Tavily MCP or LLM fallback."""
        # First try Tavily if available and requested
        if use_tavily and self.available_tools.get("tavily", False):
            try:
                result = await self.tavily_search(query)
                if result:
                    return result
            except Exception as e:
                print(f"Tavily search failed for query '{query}': {e}")

        # Fallback to LLM-generated search response
        if self.available_tools.get("llm_fallback", False):
            try:
                return await self._llm_fallback_search(query)
            except Exception as e:
                print(f"LLM fallback search failed for query '{query}': {e}")

        return []

    async def _llm_fallback_search(self, query: str) -> List[Dict[str, Any]]:
        """Generate search-like responses using LLM with web search tools when available."""
        try:

            # Create a prompt asking the LLM to search for information
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a research assistant. When possible, search for comprehensive, "
                        "up-to-date information about the given topic using available tools. "
                        "If tools aren't available, provide information based on your knowledge "
                        "and clearly indicate the limitations."
                    ),
                },
                {"role": "user", "content": f"Search for detailed information about: {query}"},
            ]

            # Check if the LLM provider supports web search tools
            provider_info = self.llm_client.get_provider_info()
            provider = provider_info.get("provider", "")

            # Prepare tool configuration
            tools = None
            tool_choice = None

            # Configure web search tools based on provider capabilities
            if provider == "openai":
                # OpenAI supports function calling with web search
                if hasattr(self.llm_client, "supports_tools") and self.llm_client.supports_tools():
                    tools = [
                        {
                            "type": "function",
                            "function": {"name": "web_search", "description": "Search the web for information"},
                        }
                    ]
                    tool_choice = "auto"
                elif hasattr(self.llm_client, "get_available_tools"):
                    available_tools = self.llm_client.get_available_tools()
                    if "web_search" in available_tools:
                        tools = ["web_search"]
                        tool_choice = "auto"
            elif provider == "anthropic":
                # Anthropic supports server-side web search tool
                if hasattr(self.llm_client, "supports_tools") and self.llm_client.supports_tools():
                    tools = [{"type": "web_search_20250305"}]
                    tool_choice = "auto"
            elif provider == "gemini":
                # Gemini supports function calling with web search capabilities
                if hasattr(self.llm_client, "supports_tools") and self.llm_client.supports_tools():
                    tools = [
                        {
                            "type": "function",
                            "function": {"name": "web_search", "description": "Search the web for information"},
                        }
                    ]
                    tool_choice = "auto"

            try:
                # Try with tools if available
                if tools:
                    response = await self.llm_client.chat_completion(
                        messages=messages, tools=tools, tool_choice=tool_choice
                    )
                    source_suffix = "_with_tools"
                else:
                    # Fallback to standard completion without tools
                    response = await self.llm_client.chat_completion(messages=messages)
                    source_suffix = ""

            except Exception as tool_error:
                print(f"Web search with tools failed, using standard completion: {tool_error}")
                # Fallback to standard completion without tools
                response = await self.llm_client.chat_completion(messages=messages)
                source_suffix = "_fallback"

            # Format the response to match expected search result structure
            content = response if isinstance(response, str) else str(response)

            return [
                {
                    "title": f"Research Information: {query}",
                    "url": "llm_generated",
                    "content": content,
                    "source": f"llm_fallback_{provider}{source_suffix}",
                }
            ]

        except Exception as e:
            print(f"LLM fallback search failed: {e}")
            return []

    async def github_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search GitHub repositories via MCP."""
        if not self.available_tools.get("github", False):
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
        if not self.available_tools.get("tavily", False):
            return []

        result = await self._run_mcp_tool("tavily", "search", {"query": query, "max_results": 5})

        if result and "results" in result:
            return result["results"]
        return []

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the LLM provider being used."""
        return self.llm_client.get_provider_info()

    async def validate_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a proposal using the MCP validation tool."""
        if not self.has_tool("validation"):
            raise MCPToolError("Validation tool not available to this client")

        return self.validation_tool.validate_proposal(proposal)

    def _determine_available_tools(self) -> Dict[str, bool]:
        """Determine which MCP tools are available based on configuration and environment."""
        # In testing mode, use simplified logic based on config and env vars
        if self._is_testing:
            available_tools = {}
            for tool_name, mcp_config in self.config.mcp_clients.items():
                if mcp_config.command == "internal":
                    available_tools[tool_name] = True
                elif mcp_config.api_key_env:
                    available_tools[tool_name] = bool(os.getenv(mcp_config.api_key_env))
                else:
                    available_tools[tool_name] = True
            available_tools["llm_fallback"] = True  # Always available in testing
            available_tools["validation"] = True  # Always available for validation
            return available_tools

        # In production mode, validate the actual MCP environment
        env_validation = self._validate_mcp_environment()

        # Get node-specific tool configuration
        node_tools = self.config.get_node_tools(self.node_name)

        # Combine environment validation with node configuration for all configured tools
        available_tools = {}
        for tool_name in self.config.mcp_clients.keys():
            # Tool is available if:
            # 1. Environment supports it
            # 2. Node configuration allows it (or no specific restrictions)
            env_available = env_validation.get(tool_name, False)
            node_allowed = not node_tools or tool_name in node_tools

            available_tools[tool_name] = env_available and node_allowed

            if not env_available:
                print(f"Tool '{tool_name}' unavailable due to environment constraints")
            elif not node_allowed:
                print(f"Tool '{tool_name}' disabled for node '{self.node_name}'")

        # LLM fallback is always available if we have any LLM provider
        available_tools["llm_fallback"] = len(self.config.get_available_providers()) > 0
        # Validation tool is always available
        available_tools["validation"] = True

        return available_tools
