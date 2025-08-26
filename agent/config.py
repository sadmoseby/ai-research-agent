"""
Configuration management for the Lean Research Agent.
"""

import json
import logging
import logging.config
import os
import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

# Try to load dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass

SCHEMA_PATH = pathlib.Path("schema/lean-research-schema.jsonc")

LLMProvider = Literal["openai", "anthropic", "gemini", "ollama"]


@dataclass
class LLMProviderConfig:
    """Configuration for an LLM provider."""

    provider: LLMProvider
    api_key_env: str  # Environment variable name for API key
    model: str
    base_url: Optional[str] = None  # For Ollama or custom endpoints
    temperature: float = 0.7
    max_tokens: int = 4000

    # Provider-specific settings
    extra_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPClientConfig:
    """Configuration for an individual MCP client/server."""

    name: str  # Unique identifier for this MCP client
    server_type: str  # e.g., "web_search", "github", "tavily", "filesystem", "database"
    enabled: bool = True
    # Connection details
    command: Optional[str] = None  # Command to start the MCP server
    args: List[str] = field(default_factory=list)  # Arguments for the server command
    env_vars: Dict[str, str] = field(default_factory=dict)  # Environment variables for the server
    # Configuration
    api_key_env: Optional[str] = None  # Environment variable name for API key
    config_params: Dict[str, Any] = field(default_factory=dict)  # Additional configuration parameters
    # Timeouts and limits
    timeout: int = 30  # Connection timeout in seconds
    max_retries: int = 3


@dataclass
class NodeConfig:
    """Configuration for a specific node."""

    provider: Optional[str] = None  # Which LLM provider to use
    model: Optional[str] = None
    use_mcp: Optional[bool] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    # MCP tools this node has access to (references to global MCP clients by name)
    mcp_tools: List[str] = field(default_factory=list)
    # Additional node-specific settings can be added here


@dataclass
class LoggingConfig:
    """Configuration for logging."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_node_logging: bool = True
    enable_graph_logging: bool = True
    log_to_file: bool = False
    log_file_path: str = "research_agent.log"
    max_log_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 3


@dataclass
class Config:
    """Configuration class for the research agent with global and per-node settings."""

    # LLM Provider configurations
    llm_providers: Dict[str, LLMProviderConfig] = field(default_factory=dict)
    default_provider: str = "openai"

    # Legacy OpenAI support (for backward compatibility)
    openai_api_key: Optional[str] = None

    # Other API keys
    github_token: Optional[str] = None
    tavily_api_key: Optional[str] = None

    # Global defaults (will be applied to default provider)
    model: str = "gpt-4o"
    use_mcp: bool = True  # Enable MCP by default
    temperature: float = 0.7
    max_tokens: int = 4000

    # Logging configuration
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Global MCP client configurations
    mcp_clients: Dict[str, MCPClientConfig] = field(default_factory=dict)
    # Per-node configurations
    node_configs: Dict[str, NodeConfig] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        config = cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),  # For backward compatibility
            github_token=os.getenv("GITHUB_TOKEN"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            model=os.getenv("MODEL", "gpt-4o"),
            default_provider=os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
            use_mcp=os.getenv("USE_MCP", "true").lower() == "true",
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS", "4000")),
        )

        # Load LLM provider configurations
        config._load_llm_providers()

        # Validate that we have at least one working provider
        if not config.llm_providers:
            raise ValueError("No LLM providers configured. Please set at least one provider's API key.")

        # Ensure default provider exists
        if config.default_provider not in config.llm_providers:
            # Fallback to first available provider
            config.default_provider = list(config.llm_providers.keys())[0]
            print(
                f"Warning: Default provider '{config.default_provider}' not available. "
                f"Using '{config.default_provider}'"
            )

        # Load global MCP client configurations
        config._load_global_mcp_clients()
        # Load per-node configurations
        config._load_node_configs()
        return config

    def _load_llm_providers(self) -> None:
        """Load LLM provider configurations from environment variables."""
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.llm_providers["openai"] = LLMProviderConfig(
                provider="openai",
                api_key_env="OPENAI_API_KEY",
                model=os.getenv("OPENAI_MODEL", "gpt-4o"),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", str(self.temperature))),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", str(self.max_tokens))),
            )

        # Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            self.llm_providers["anthropic"] = LLMProviderConfig(
                provider="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", str(self.temperature))),
                max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", str(self.max_tokens))),
            )

        # Google Gemini
        if os.getenv("GOOGLE_API_KEY"):
            self.llm_providers["gemini"] = LLMProviderConfig(
                provider="gemini",
                api_key_env="GOOGLE_API_KEY",
                model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
                temperature=float(os.getenv("GEMINI_TEMPERATURE", str(self.temperature))),
                max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", str(self.max_tokens))),
            )

        # Ollama (local)
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        if os.getenv("OLLAMA_MODEL") or os.getenv("ENABLE_OLLAMA", "false").lower() == "true":
            self.llm_providers["ollama"] = LLMProviderConfig(
                provider="ollama",
                api_key_env="",  # Ollama typically doesn't need API key for local
                model=os.getenv("OLLAMA_MODEL", "llama3.1"),
                base_url=ollama_base_url,
                temperature=float(os.getenv("OLLAMA_TEMPERATURE", str(self.temperature))),
                max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS", str(self.max_tokens))),
            )

        # Maintain backward compatibility
        if self.openai_api_key and "openai" not in self.llm_providers:
            self.llm_providers["openai"] = LLMProviderConfig(
                provider="openai",
                api_key_env="OPENAI_API_KEY",
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

    def _load_global_mcp_clients(self) -> None:
        """Load global MCP client configurations."""
        # Initialize default MCP clients based on available API keys
        if "openai" in self.llm_providers:
            openai_config = self.llm_providers["openai"]
            self.mcp_clients["web_search"] = MCPClientConfig(
                name="web_search",
                server_type="web_search",
                command="npx",
                args=["@modelcontextprotocol/server-web-search"],
                api_key_env=openai_config.api_key_env,
                config_params={"model": openai_config.model},
            )

        if self.github_token:
            self.mcp_clients["github"] = MCPClientConfig(
                name="github",
                server_type="github",
                command="npx",
                args=["@modelcontextprotocol/server-github"],
                api_key_env="GITHUB_TOKEN",
                config_params={"repo_access": "public"},
            )

        if self.tavily_api_key:
            self.mcp_clients["tavily"] = MCPClientConfig(
                name="tavily",
                server_type="tavily",
                command="npx",
                args=["@modelcontextprotocol/server-tavily"],
                api_key_env="TAVILY_API_KEY",
                config_params={"search_depth": "advanced"},
            )

        # Always add filesystem client (no API key required)
        self.mcp_clients["filesystem"] = MCPClientConfig(
            name="filesystem",
            server_type="filesystem",
            command="npx",
            args=["@modelcontextprotocol/server-filesystem"],
            config_params={"allowed_directories": ["/tmp", "/workspace"]},
        )

        # Override with any environment-specific configurations
        self._override_mcp_clients_from_env()

    def _override_mcp_clients_from_env(self) -> None:
        """Override MCP client configurations from environment variables."""
        for client_name, client in self.mcp_clients.items():
            env_prefix = f"MCP_{client_name.upper()}"

            # Check for client-specific overrides
            if os.getenv(f"{env_prefix}_ENABLED"):
                client.enabled = os.getenv(f"{env_prefix}_ENABLED").lower() == "true"

            if os.getenv(f"{env_prefix}_TIMEOUT"):
                client.timeout = int(os.getenv(f"{env_prefix}_TIMEOUT"))

            if os.getenv(f"{env_prefix}_MAX_RETRIES"):
                client.max_retries = int(os.getenv(f"{env_prefix}_MAX_RETRIES"))

            # Load additional config parameters
            config_env = f"{env_prefix}_CONFIG"
            if os.getenv(config_env):
                try:
                    additional_config = json.loads(os.getenv(config_env))
                    client.config_params.update(additional_config)
                except json.JSONDecodeError:
                    print(f"Warning: Invalid JSON in {config_env}")

    def _load_node_configs(self) -> None:
        """Load node-specific configurations from environment or config files."""
        # Example: WEB_RESEARCH_MODEL, SYNTHESIZE_USE_MCP, etc.
        node_names = [
            "plan",
            "web_research",
            "prior_art",
            "criticism",
            "synthesize",
            "validate",
            "persist",
        ]

        for node_name in node_names:
            node_config = NodeConfig()
            env_prefix = node_name.upper()

            # Check for node-specific environment variables
            provider_env = f"{env_prefix}_PROVIDER"
            if os.getenv(provider_env):
                node_config.provider = os.getenv(provider_env)

            model_env = f"{env_prefix}_MODEL"
            if os.getenv(model_env):
                node_config.model = os.getenv(model_env)

            use_mcp_env = f"{env_prefix}_USE_MCP"
            if os.getenv(use_mcp_env):
                node_config.use_mcp = os.getenv(use_mcp_env).lower() == "true"

            temperature_env = f"{env_prefix}_TEMPERATURE"
            if os.getenv(temperature_env):
                node_config.temperature = float(os.getenv(temperature_env))

            max_tokens_env = f"{env_prefix}_MAX_TOKENS"
            if os.getenv(max_tokens_env):
                node_config.max_tokens = int(os.getenv(max_tokens_env))

            # Load MCP tools this node has access to
            node_config.mcp_tools = self._load_node_mcp_tools(node_name)

            # Only add if at least one setting is configured
            if any(
                [
                    node_config.provider,
                    node_config.model,
                    node_config.use_mcp is not None,
                    node_config.temperature is not None,
                    node_config.max_tokens is not None,
                    node_config.mcp_tools,
                ]
            ):
                self.node_configs[node_name] = node_config

    def _load_node_mcp_tools(self, node_name: str) -> List[str]:
        """Load MCP tools available to a specific node from environment variables."""
        env_prefix = node_name.upper()

        # Check for MCP tools configuration
        # Format: {NODE}_MCP_TOOLS = "web_search,github,tavily"
        tools_env = f"{env_prefix}_MCP_TOOLS"
        tool_names = os.getenv(tools_env, "").split(",") if os.getenv(tools_env) else []

        # Clean and validate tool names
        valid_tools = []
        for tool_name in tool_names:
            tool_name = tool_name.strip()
            if tool_name and tool_name in self.mcp_clients:
                valid_tools.append(tool_name)
            elif tool_name:  # Invalid tool name
                print(f"Warning: MCP tool '{tool_name}' not found in global clients for node '{node_name}'")

        # If no specific tools configured, use defaults based on global settings
        if not valid_tools and self.use_mcp:
            # Default to all available MCP clients
            valid_tools = list(self.mcp_clients.keys())

        return valid_tools

    def get_node_config(self, node_name: str) -> Dict[str, Any]:
        """Get effective configuration for a specific node (merging global and node-specific)."""
        node_config = self.node_configs.get(node_name, NodeConfig())

        # Determine effective provider
        effective_provider = node_config.provider or self.default_provider
        provider_config = self.llm_providers.get(effective_provider)

        if not provider_config:
            raise ValueError(f"Provider '{effective_provider}' not configured for node '{node_name}'")

        # Get MCP clients that this node has access to
        available_mcp_clients = []
        for tool_name in node_config.mcp_tools:
            if tool_name in self.mcp_clients:
                available_mcp_clients.append(self.mcp_clients[tool_name])

        return {
            "provider": effective_provider,
            "provider_config": provider_config,
            "model": node_config.model or provider_config.model,
            "use_mcp": (node_config.use_mcp if node_config.use_mcp is not None else self.use_mcp),
            "temperature": (
                node_config.temperature if node_config.temperature is not None else provider_config.temperature
            ),
            "max_tokens": (
                node_config.max_tokens if node_config.max_tokens is not None else provider_config.max_tokens
            ),
            "mcp_tools": node_config.mcp_tools,  # Available tool names
            "mcp_clients": available_mcp_clients,  # Actual client configurations
            # Legacy keys for backward compatibility
            "openai_api_key": self.openai_api_key,
            "github_token": self.github_token,
            "tavily_api_key": self.tavily_api_key,
        }

    def set_node_config(self, node_name: str, **kwargs) -> None:
        """Set configuration for a specific node."""
        if node_name not in self.node_configs:
            self.node_configs[node_name] = NodeConfig()

        node_config = self.node_configs[node_name]

        for key, value in kwargs.items():
            if hasattr(node_config, key):
                setattr(node_config, key, value)
            else:
                raise ValueError(f"Invalid node configuration key: {key}")

    def add_mcp_tool_to_node(self, node_name: str, tool_name: str) -> bool:
        """Add an MCP tool to a specific node. Returns True if added, False if tool doesn't exist."""
        if tool_name not in self.mcp_clients:
            return False

        if node_name not in self.node_configs:
            self.node_configs[node_name] = NodeConfig()

        if tool_name not in self.node_configs[node_name].mcp_tools:
            self.node_configs[node_name].mcp_tools.append(tool_name)

        return True

    def remove_mcp_tool_from_node(self, node_name: str, tool_name: str) -> bool:
        """Remove an MCP tool from a specific node. Returns True if removed, False if not found."""
        if node_name not in self.node_configs:
            return False

        if tool_name in self.node_configs[node_name].mcp_tools:
            self.node_configs[node_name].mcp_tools.remove(tool_name)
            return True

        return False

    def get_node_mcp_tools(self, node_name: str) -> List[str]:
        """Get all MCP tool names available to a specific node."""
        node_config = self.node_configs.get(node_name, NodeConfig())
        return node_config.mcp_tools.copy()  # Return a copy to prevent external modification

    def get_provider_config(self, provider_name: str) -> Optional[LLMProviderConfig]:
        """Get configuration for a specific LLM provider."""
        return self.llm_providers.get(provider_name)

    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers."""
        return list(self.llm_providers.keys())

    def set_node_provider(self, node_name: str, provider: str) -> bool:
        """Set the LLM provider for a specific node. Returns True if successful."""
        if provider not in self.llm_providers:
            return False

        if node_name not in self.node_configs:
            self.node_configs[node_name] = NodeConfig()

        self.node_configs[node_name].provider = provider
        return True

    def get_node_mcp_clients(self, node_name: str) -> List[MCPClientConfig]:
        """Get all MCP client configurations available to a specific node."""
        node_config = self.node_configs.get(node_name, NodeConfig())
        clients = []
        for tool_name in node_config.mcp_tools:
            if tool_name in self.mcp_clients:
                clients.append(self.mcp_clients[tool_name])
        return clients

    def add_global_mcp_client(self, client: MCPClientConfig) -> None:
        """Add a global MCP client configuration."""
        self.mcp_clients[client.name] = client

    def remove_global_mcp_client(self, client_name: str) -> bool:
        """Remove a global MCP client configuration. Returns True if removed, False if not found."""
        if client_name in self.mcp_clients:
            del self.mcp_clients[client_name]

            # Remove from all nodes that use this client
            for node_config in self.node_configs.values():
                if client_name in node_config.mcp_tools:
                    node_config.mcp_tools.remove(client_name)

            return True
        return False

    def get_global_mcp_clients(self) -> Dict[str, MCPClientConfig]:
        """Get all global MCP client configurations."""
        return self.mcp_clients.copy()  # Return a copy to prevent external modification

    def for_node(self, node_name: str) -> "Config":
        """Create a new Config instance with node-specific settings applied as defaults.

        This allows backward compatibility while providing node-specific configuration.
        """
        node_config = self.get_node_config(node_name)

        # Create a new config instance with node-specific values
        new_config = Config(
            openai_api_key=self.openai_api_key,
            github_token=self.github_token,
            tavily_api_key=self.tavily_api_key,
            model=node_config["model"],
            use_mcp=node_config["use_mcp"],
            temperature=node_config["temperature"],
            max_tokens=node_config["max_tokens"],
            mcp_clients=self.mcp_clients.copy(),  # Keep all global MCP clients
            node_configs=self.node_configs,  # Keep the node configs for potential nested calls
        )

        return new_config

    def get_all_node_names(self) -> list[str]:
        """Get list of all known node names."""
        return [
            "plan",
            "web_research",
            "prior_art",
            "criticism",
            "synthesize",
            "validate",
            "persist",
        ]

    def get_schema(self) -> dict:
        """Load and return the JSON schema, handling JSONC format."""
        schema_text = SCHEMA_PATH.read_text(encoding="utf-8")
        # Simple JSONC to JSON conversion (remove // comments)
        lines = []
        for line in schema_text.split("\n"):
            # Remove // comments but preserve URLs
            if "//" in line and not line.strip().startswith('"') and "http" not in line:
                line = line[: line.find("//")]
            lines.append(line)

        clean_json = "\n".join(lines)
        return json.loads(clean_json)

    def setup_logging(self):
        """Setup logging configuration based on the logging config."""
        log_config = self.logging

        # Configure the root logger
        logging.basicConfig(
            level=getattr(logging, log_config.level.upper()),
            format=log_config.format,
            force=True,  # Override any existing configuration
        )

        # If file logging is enabled, add file handler
        if log_config.log_to_file:
            from logging.handlers import RotatingFileHandler

            file_handler = RotatingFileHandler(
                log_config.log_file_path,
                maxBytes=log_config.max_log_file_size,
                backupCount=log_config.backup_count,
            )
            file_handler.setFormatter(logging.Formatter(log_config.format))

            # Add file handler to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)

        # Create loggers for graph and nodes
        if log_config.enable_graph_logging:
            graph_logger = logging.getLogger("research_agent.graph")
            graph_logger.info("Graph logging initialized")

        if log_config.enable_node_logging:
            node_names = self.get_all_node_names()
            for node_name in node_names:
                node_logger = logging.getLogger(f"research_agent.nodes.{node_name}")
                node_logger.info(f"Node logger initialized for {node_name}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name under the research_agent namespace."""
    return logging.getLogger(f"research_agent.{name}")
