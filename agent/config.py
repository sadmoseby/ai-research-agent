"""
Configuration management for the Lean Research Agent.
"""

import json
import logging
import logging.config
import os
import pathlib
from typing import Any, Dict, List, Literal, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Try to load dotenv, but don't fail if not available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass

SCHEMA_PATH = pathlib.Path("schema/lean-research-schema.jsonc")

LLMProvider = Literal["openai", "anthropic", "gemini", "ollama"]


class LLMProviderConfig(BaseSettings):
    """Configuration for an LLM provider."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    provider: LLMProvider
    api_key_env: str  # Environment variable name for API key
    model: str
    base_url: Optional[str] = None  # For Ollama or custom endpoints
    temperature: float = 0.7
    max_tokens: int = 4000

    # Provider-specific settings
    extra_kwargs: Dict[str, Any] = Field(default_factory=dict)


class MCPClientConfig(BaseSettings):
    """Configuration for an individual MCP client/server."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    name: str  # Unique identifier for this MCP client
    server_type: str  # e.g., "web_search", "github", "tavily", "filesystem", "database"
    # Connection details
    command: Optional[str] = None  # Command to start the MCP server
    args: List[str] = Field(default_factory=list)  # Arguments for the server command
    env_vars: Dict[str, str] = Field(default_factory=dict)  # Environment variables for the server
    # Configuration
    api_key_env: Optional[str] = None  # Environment variable name for API key
    config_params: Dict[str, Any] = Field(default_factory=dict)  # Additional configuration parameters
    # Status
    enabled: bool = True  # Whether this MCP client is enabled
    # Timeouts and limits
    timeout: int = 30  # Connection timeout in seconds
    max_retries: int = 3


class NodeConfig(BaseSettings):
    """Configuration for a specific node."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    # Node-level settings
    enabled: Optional[bool] = None  # Whether this node is enabled (None = use default True)

    # Embedded LLM configuration
    llm_provider: Optional[LLMProviderConfig] = None  # Node-specific LLM configuration

    # MCP configuration
    mcp_enabled: Optional[bool] = None  # Whether MCP is enabled for this node
    mcp_tools: List[str] = Field(default_factory=list)  # Available tool names (for backward compatibility)


class LoggingConfig(BaseSettings):
    """Configuration for logging."""

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        case_sensitive=False,
        extra="ignore",
    )

    level: str = Field(default="INFO", alias="LOG_LEVEL")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_node_logging: bool = Field(default=True, alias="ENABLE_NODE_LOGGING")
    enable_graph_logging: bool = Field(default=True, alias="ENABLE_GRAPH_LOGGING")
    log_to_file: bool = Field(default=False, alias="LOG_TO_FILE")
    log_file_path: str = Field(default="research_agent.log", alias="LOG_FILE_PATH")
    max_log_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 3


class Config(BaseSettings):
    """Main configuration class for the research agent with global and per-node settings."""

    model_config = SettingsConfigDict(
        env_prefix="",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # Core LLM settings
    default_llm_provider: LLMProvider = Field(default="openai", alias="DEFAULT_LLM_PROVIDER")
    model: str = Field(default="gpt-4o", alias="MODEL")
    temperature: float = Field(default=0.7, alias="TEMPERATURE")
    max_tokens: int = Field(default=4000, alias="MAX_TOKENS")
    use_mcp: bool = Field(default=True, alias="USE_MCP")

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    github_token: Optional[str] = Field(default=None, alias="GITHUB_TOKEN")
    tavily_api_key: Optional[str] = Field(default=None, alias="TAVILY_API_KEY")

    # Proposal parameters
    idea: Optional[str] = Field(default=None, alias="IDEA")
    instruments: Optional[str] = Field(default=None, alias="INSTRUMENTS")  # comma-separated
    alpha_only: bool = Field(default=False, alias="ALPHA_ONLY")
    slug: Optional[str] = Field(default=None, alias="SLUG")
    output_dir: str = Field(default="proposals", alias="OUTPUT_DIR")
    components: Optional[str] = Field(default=None, alias="COMPONENTS")  # comma-separated
    unified_synthesis: bool = Field(default=False, alias="UNIFIED_SYNTHESIS")
    branch_name: Optional[str] = Field(default=None, alias="BRANCH_NAME")
    image_name: Optional[str] = Field(default=None, alias="IMAGE_NAME")
    upload_to_github: bool = Field(default=False, alias="UPLOAD_TO_GITHUB")
    github_owner: Optional[str] = Field(default=None, alias="GITHUB_OWNER")
    github_repository: Optional[str] = Field(default=None, alias="GITHUB_REPOSITORY")

    # Quality control
    min_viability_score: int = Field(default=51, alias="MIN_VIABILITY_SCORE")
    max_planning_iterations: int = Field(default=3, alias="MAX_PLANNING_ITERATIONS")

    # Node enable/disable flags
    # Can be set via environment variables (PLAN_ENABLED, etc.) or config files
    # Config files take precedence when using from_file() or from_dotenv()
    plan_enabled: bool = True
    web_research_enabled: bool = True
    criticism_enabled: bool = True
    synthesize_enabled: bool = True
    validate_enabled: bool = True
    persist_enabled: bool = True
    github_issue_enabled: bool = True

    # Logging configuration (for initialization)
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    enable_node_logging: bool = Field(default=True, alias="ENABLE_NODE_LOGGING")
    enable_graph_logging: bool = Field(default=True, alias="ENABLE_GRAPH_LOGGING")
    log_to_file: bool = Field(default=False, alias="LOG_TO_FILE")
    log_file_path: str = Field(default="research_agent.log", alias="LOG_FILE_PATH")

    # MCP Server Configuration
    mcp_github_command: str = Field(default="npx", alias="MCP_GITHUB_COMMAND")
    mcp_github_args: str = Field(default="@modelcontextprotocol/server-github", alias="MCP_GITHUB_ARGS")
    mcp_github_repo_access: str = Field(default="public", alias="MCP_GITHUB_REPO_ACCESS")
    mcp_github_timeout: int = Field(default=30, alias="MCP_GITHUB_TIMEOUT")
    mcp_github_max_retries: int = Field(default=3, alias="MCP_GITHUB_MAX_RETRIES")

    mcp_tavily_command: str = Field(default="npx", alias="MCP_TAVILY_COMMAND")
    mcp_tavily_args: str = Field(default="@modelcontextprotocol/server-tavily", alias="MCP_TAVILY_ARGS")
    mcp_tavily_search_depth: str = Field(default="advanced", alias="MCP_TAVILY_SEARCH_DEPTH")
    mcp_tavily_timeout: int = Field(default=30, alias="MCP_TAVILY_TIMEOUT")
    mcp_tavily_max_retries: int = Field(default=3, alias="MCP_TAVILY_MAX_RETRIES")

    mcp_filesystem_command: str = Field(default="npx", alias="MCP_FILESYSTEM_COMMAND")
    mcp_filesystem_args: str = Field(default="@modelcontextprotocol/server-filesystem", alias="MCP_FILESYSTEM_ARGS")
    mcp_filesystem_allowed_dirs: str = Field(default="/tmp,/workspace", alias="MCP_FILESYSTEM_ALLOWED_DIRS")
    mcp_filesystem_timeout: int = Field(default=30, alias="MCP_FILESYSTEM_TIMEOUT")
    mcp_filesystem_max_retries: int = Field(default=3, alias="MCP_FILESYSTEM_MAX_RETRIES")

    # Provider-specific model configuration
    enable_ollama: bool = Field(default=False, alias="ENABLE_OLLAMA")
    ollama_model: Optional[str] = Field(default=None, alias="OLLAMA_MODEL")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.1, alias="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=4000, alias="OPENAI_MAX_TOKENS")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", alias="ANTHROPIC_MODEL")
    anthropic_temperature: float = Field(default=0.1, alias="ANTHROPIC_TEMPERATURE")
    anthropic_max_tokens: int = Field(default=4000, alias="ANTHROPIC_MAX_TOKENS")
    google_model: str = Field(default="gemini-1.5-pro", alias="GOOGLE_MODEL")
    google_temperature: float = Field(default=0.1, alias="GOOGLE_TEMPERATURE")
    google_max_tokens: int = Field(default=4000, alias="GOOGLE_MAX_TOKENS")
    ollama_temperature: float = Field(default=0.1, alias="OLLAMA_TEMPERATURE")
    ollama_max_tokens: int = Field(default=4000, alias="OLLAMA_MAX_TOKENS")

    # Internal state - these are computed after initialization
    mcp_clients: Dict[str, MCPClientConfig] = Field(default_factory=dict, exclude=True)
    default_config: NodeConfig = Field(default_factory=NodeConfig, exclude=True)
    node_configs: Dict[str, NodeConfig] = Field(default_factory=dict, exclude=True)
    logging_config: LoggingConfig = Field(default_factory=LoggingConfig, exclude=True)

    @model_validator(mode="after")
    def initialize_internal_state(self) -> "Config":
        """Initialize internal configuration state after pydantic validation."""
        # Create default LLM provider config
        default_llm_config = LLMProviderConfig(
            provider=self.default_llm_provider,
            api_key_env=f"{str(self.default_llm_provider).upper()}_API_KEY",
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        # Initialize internal structures
        self.default_config = NodeConfig(
            enabled=True,
            llm_provider=default_llm_config,
            mcp_enabled=self.use_mcp,
            mcp_tools=[],
        )

        # Initialize logging config from the main config attributes
        self.logging_config = LoggingConfig(
            level=self.log_level,
            enable_node_logging=self.enable_node_logging,
            enable_graph_logging=self.enable_graph_logging,
            log_to_file=self.log_to_file,
            log_file_path=self.log_file_path,
        )

        # Load global MCP client configurations
        self._load_global_mcp_clients()
        # Load per-node configurations
        self._load_node_configs()

        return self

    @classmethod
    def from_dotenv(cls, dotenv_path: str = ".env") -> "Config":
        """Create config by loading from a .env file.

        Values from the .env file take precedence over existing environment variables.
        """
        try:
            from dotenv import dotenv_values
        except ImportError:
            raise ImportError(
                "python-dotenv is required to load .env files. Install it with: pip install python-dotenv"
            )

        # Load values from the dotenv file
        dotenv_config = dotenv_values(dotenv_path)

        # Temporarily override environment with dotenv values
        original_env = {}
        for key, value in dotenv_config.items():
            if key in os.environ:
                original_env[key] = os.environ[key]
            if value is not None:
                os.environ[key] = value

        try:
            # Create config with dotenv values in environment
            return cls()
        finally:
            # Restore original environment
            for key in dotenv_config:
                if key in original_env:
                    os.environ[key] = original_env[key]
                elif key in os.environ:
                    del os.environ[key]

    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Create config from a JSON or YAML file.

        Values from the config file take precedence over environment variables.
        """
        import pathlib

        path = pathlib.Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        # Determine file format by extension
        suffix = path.suffix.lower()

        with open(path, "r") as f:
            if suffix == ".json":
                data = json.load(f)
            elif suffix in [".yaml", ".yml"]:
                try:
                    import yaml

                    data = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML is required for YAML config files. Install it with: pip install pyyaml")
            else:
                # Try to auto-detect format
                content = f.read()
                # Try JSON first
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    # Try YAML
                    try:
                        import yaml

                        data = yaml.safe_load(content)
                    except (ImportError, Exception):
                        raise ValueError(f"Could not parse config file as JSON or YAML: {config_path}")

        # Pass config file data directly to constructor
        # Pydantic prioritizes constructor arguments over environment variables
        return cls(**data)

    def _load_global_mcp_clients(self) -> None:
        """Load global MCP client configurations."""
        # Initialize default MCP clients based on available API keys

        if self.github_token:
            self.mcp_clients["github"] = MCPClientConfig(
                name="github",
                server_type="github",
                command=self.mcp_github_command,
                args=self.mcp_github_args.split(","),
                api_key_env="GITHUB_TOKEN",
                config_params={"repo_access": self.mcp_github_repo_access},
                timeout=self.mcp_github_timeout,
                max_retries=self.mcp_github_max_retries,
            )

        if self.tavily_api_key:
            self.mcp_clients["tavily"] = MCPClientConfig(
                name="tavily",
                server_type="tavily",
                command=self.mcp_tavily_command,
                args=self.mcp_tavily_args.split(","),
                api_key_env="TAVILY_API_KEY",
                config_params={"search_depth": self.mcp_tavily_search_depth},
                timeout=self.mcp_tavily_timeout,
                max_retries=self.mcp_tavily_max_retries,
            )

        # Always add filesystem client (no API key required)
        allowed_dirs = [d.strip() for d in self.mcp_filesystem_allowed_dirs.split(",")]
        self.mcp_clients["filesystem"] = MCPClientConfig(
            name="filesystem",
            server_type="filesystem",
            command=self.mcp_filesystem_command,
            args=self.mcp_filesystem_args.split(","),
            config_params={"allowed_directories": allowed_dirs},
            timeout=self.mcp_filesystem_timeout,
            max_retries=self.mcp_filesystem_max_retries,
        )

    def _load_node_configs(self) -> None:
        """Load node-specific configurations from environment variables."""
        node_names = [
            "plan",
            "web_research",
            "criticism",
            "synthesize",
            "validate",
            "persist",
        ]

        for node_name in node_names:
            # Create node config from environment with proper prefix
            node_config = self._create_node_config_from_env(node_name)

            # Only add if at least one setting is configured
            if self._has_node_config(node_config):
                self.node_configs[node_name] = node_config

    def _create_node_config_from_env(self, node_name: str) -> NodeConfig:
        """Create a node config from environment variables."""
        # Create node config with environment-based loading
        node_config = NodeConfig()

        # Load LLM configuration for this node
        node_llm_config = self._load_node_llm_config(node_name)
        if node_llm_config:
            node_config.llm_provider = node_llm_config

        # Load MCP configuration for this node
        mcp_tools_list = self._get_node_mcp_tools_list(node_name)
        node_config.mcp_tools = mcp_tools_list

        # Check for MCP enabled/disabled
        mcp_enabled = self._get_node_mcp_enabled(node_name)
        if mcp_enabled is not None:
            node_config.mcp_enabled = mcp_enabled

        # Check if node is enabled/disabled
        enabled = self._get_node_enabled(node_name)
        if enabled is not None:
            node_config.enabled = enabled

        return node_config

    def _load_node_llm_config(self, node_name: str) -> Optional[LLMProviderConfig]:
        """Load node-specific LLM configuration.

        Note: This is deprecated. Per-node LLM settings should be configured
        through the NodeConfig in node_configs, not environment variables.
        """
        # No longer read from environment variables
        return None

    def _get_node_mcp_tools_list(self, node_name: str) -> List[str]:
        """Get MCP tools list for a specific node.

        Note: This is deprecated. Per-node MCP tool settings should be configured
        through the NodeConfig in node_configs, not environment variables.
        """
        # No longer read from environment variables
        return []

    def _get_node_mcp_enabled(self, node_name: str) -> Optional[bool]:
        """Get MCP enabled setting for a specific node.

        Note: This is deprecated. Per-node MCP settings should be configured
        through the NodeConfig in node_configs, not environment variables.
        """
        # No longer read from environment variables
        return None

    def _get_node_enabled(self, node_name: str) -> Optional[bool]:
        """Get enabled setting for a specific node from config fields only."""
        # Map node names to config field names
        field_map = {
            "plan": "plan_enabled",
            "web_research": "web_research_enabled",
            "criticism": "criticism_enabled",
            "synthesize": "synthesize_enabled",
            "validate": "validate_enabled",
            "persist": "persist_enabled",
            "github_issue": "github_issue_enabled",
        }

        # Return the config field value if it exists
        if node_name in field_map:
            field_name = field_map[node_name]
            if hasattr(self, field_name):
                return getattr(self, field_name)

        # Return None to use default behavior (enabled)
        return None

    def get_global_mcp_clients(self) -> Dict[str, MCPClientConfig]:
        """Get all global MCP client configurations."""
        return self.mcp_clients.copy()

    def get_node_mcp_clients(self, node_name: str) -> List[MCPClientConfig]:
        """Get MCP client configurations available to a specific node."""
        node_tools = self.get_node_tools(node_name)

        if node_tools is None:
            # No restrictions, return all available clients
            return list(self.mcp_clients.values())

        # Return only the clients for tools this node has access to
        return [self.mcp_clients[tool_name] for tool_name in node_tools if tool_name in self.mcp_clients]

    def get_node_mcp_tools(self, node_name: str) -> List[str]:
        """Get list of MCP tool names available to a specific node."""
        node_tools = self.get_node_tools(node_name)

        if node_tools is None:
            # No restrictions, return all available tools
            return list(self.mcp_clients.keys())

        return node_tools

    def add_global_mcp_client(self, client: MCPClientConfig) -> None:
        """Add a new global MCP client configuration."""
        self.mcp_clients[client.name] = client

    def add_mcp_tool_to_node(self, node_name: str, tool_name: str) -> bool:
        """Add MCP tool access to a specific node. Returns True if added, False if already present."""
        if tool_name not in self.mcp_clients:
            return False

        # Get or create node config
        if node_name not in self.node_configs:
            self.node_configs[node_name] = NodeConfig()

        node_config = self.node_configs[node_name]

        # Initialize mcp_tools if not set
        if not hasattr(node_config, "mcp_tools") or node_config.mcp_tools is None:
            node_config.mcp_tools = []

        # Add tool if not already present
        if tool_name not in node_config.mcp_tools:
            node_config.mcp_tools.append(tool_name)
            return True

        return False

    def remove_mcp_tool_from_node(self, node_name: str, tool_name: str) -> bool:
        """Remove MCP tool access from a specific node. Returns True if removed, False if not present."""
        if node_name not in self.node_configs:
            return False

        node_config = self.node_configs[node_name]

        if not hasattr(node_config, "mcp_tools") or not node_config.mcp_tools:
            return False

        if tool_name in node_config.mcp_tools:
            node_config.mcp_tools.remove(tool_name)
            return True

        return False

    def _has_node_config(self, node_config: NodeConfig) -> bool:
        """Check if node config has any non-default values."""
        return any(
            [
                node_config.llm_provider is not None,
                node_config.mcp_tools,
                node_config.enabled is not None,
                node_config.mcp_enabled is not None,
            ]
        )

    def get_node_config(self, node_name: str) -> Dict[str, Any]:
        """Get effective configuration for a specific node (merging global and node-specific)."""
        node_config = self.node_configs.get(node_name, NodeConfig())

        # Determine effective LLM configuration
        if node_config.llm_provider:
            provider_config = node_config.llm_provider
        else:
            provider_config = self.default_config.llm_provider

        # Determine effective MCP configuration
        mcp_tools = self.get_node_tools(node_name) or []
        available_mcp_clients = []

        for tool_name in mcp_tools:
            if tool_name in self.mcp_clients:
                available_mcp_clients.append(self.mcp_clients[tool_name])

        mcp_enabled = (
            node_config.mcp_enabled if node_config.mcp_enabled is not None else self.default_config.mcp_enabled
        )

        return {
            "provider": provider_config.provider,
            "provider_config": provider_config,
            "model": provider_config.model,
            "use_mcp": mcp_enabled,
            "mcp_enabled": mcp_enabled,
            "temperature": provider_config.temperature,
            "max_tokens": provider_config.max_tokens,
            "mcp_tools": mcp_tools,
            "mcp_clients": available_mcp_clients,
            "node_mcp_clients": {},
        }

    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers based on API keys."""
        providers = []
        if self.openai_api_key:
            providers.append("openai")
        if self.anthropic_api_key:
            providers.append("anthropic")
        if self.google_api_key:
            providers.append("gemini")
        if self.ollama_model or self.enable_ollama:
            providers.append("ollama")
        return providers

    def get_node_tools(self, node_name: str) -> Optional[List[str]]:
        """Get the list of tools available to a specific node."""
        # Check if node has specific tool configuration
        if node_name in self.node_configs:
            node_config = self.node_configs[node_name]
            if hasattr(node_config, "mcp_tools") and node_config.mcp_tools:
                return node_config.mcp_tools

        # Check default configuration
        if hasattr(self.default_config, "mcp_tools") and self.default_config.mcp_tools:
            return self.default_config.mcp_tools

        # Return None to indicate no specific tool restrictions (all tools allowed)
        return None

    def get_provider_config(self, provider: str) -> Optional[LLMProviderConfig]:
        """Get LLM provider configuration for the specified provider."""
        provider_configs = {
            "openai": LLMProviderConfig(
                provider="openai",
                api_key_env="OPENAI_API_KEY",
                model=self.openai_model,
                temperature=self.openai_temperature,
                max_tokens=self.openai_max_tokens,
            ),
            "anthropic": LLMProviderConfig(
                provider="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
                model=self.anthropic_model,
                temperature=self.anthropic_temperature,
                max_tokens=self.anthropic_max_tokens,
            ),
            "gemini": LLMProviderConfig(
                provider="gemini",
                api_key_env="GOOGLE_API_KEY",
                model=self.google_model,
                temperature=self.google_temperature,
                max_tokens=self.google_max_tokens,
            ),
            "ollama": LLMProviderConfig(
                provider="ollama",
                api_key_env="OLLAMA_API_KEY",  # Placeholder, not actually used
                model=self.ollama_model or "llama3.2:3b",
                temperature=self.ollama_temperature,
                max_tokens=self.ollama_max_tokens,
            ),
        }

        return provider_configs.get(provider)

    def get_effective_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the effective configuration for all nodes."""
        summary = {
            "global": {
                "default_provider": self.default_config.llm_provider.provider,
                "available_providers": self.get_available_providers(),
                "global_mcp_clients": list(self.mcp_clients.keys()),
                "use_mcp": self.default_config.mcp_enabled,
            },
            "nodes": {},
        }

        for node_name in ["plan", "web_research", "criticism", "synthesize", "validate", "persist"]:
            try:
                node_config = self.get_node_config(node_name)
                summary["nodes"][node_name] = {
                    "provider": node_config["provider"],
                    "model": node_config["model"],
                    "mcp_enabled": node_config["mcp_enabled"],
                    "mcp_tools": node_config["mcp_tools"],
                    "temperature": node_config["temperature"],
                    "max_tokens": node_config["max_tokens"],
                }
            except (KeyError, AttributeError, TypeError) as e:
                summary["nodes"][node_name] = {"error": str(e)}

        return summary

    def for_node(self, node_name: str) -> "Config":
        """Create a new Config instance with node-specific settings applied as defaults."""
        node_config_dict = self.get_node_config(node_name)

        # Create a new config instance with node-specific values
        new_config = Config()
        new_config.mcp_clients = self.mcp_clients.copy()
        new_config.default_config = NodeConfig(
            enabled=True,
            llm_provider=node_config_dict["provider_config"],
            mcp_enabled=node_config_dict["mcp_enabled"],
            mcp_tools=node_config_dict["mcp_tools"],
        )
        new_config.node_configs = self.node_configs
        new_config.logging_config = self.logging_config

        return new_config

    def get_all_node_names(self) -> list[str]:
        """Get list of all known node names."""
        return [
            "plan",
            "web_research",
            "criticism",
            "synthesize",
            "persist",
            "github_issue",
        ]

    # --- Components helpers ---
    def get_components_from_config(self) -> Optional[int]:
        """Parse COMPONENTS config field into a ResearchComponents bitmask.

        Examples:
          COMPONENTS="UNIVERSE,ALPHA" -> UNIVERSE | ALPHA
        """
        raw = self.components
        if not raw:
            return None

        # Import here to avoid any potential circular import at module load time
        try:
            from .state import ResearchComponents
        except ImportError:
            return None

        mapping = {
            "UNIVERSE": ResearchComponents.UNIVERSE,
            "ALPHA": ResearchComponents.ALPHA,
            "PORTFOLIO": ResearchComponents.PORTFOLIO,
            "EXECUTION": ResearchComponents.EXECUTION,
            "RISK": ResearchComponents.RISK,
        }

        bitmask = 0
        for part in raw.split(","):
            key = part.strip().upper()
            if key in mapping:
                bitmask |= int(mapping[key])

        return bitmask or None

    def is_node_enabled(self, node_name: str) -> bool:
        """Check if a node is enabled. Returns True by default if not explicitly disabled."""
        # Map node names to config field names
        field_map = {
            "plan": "plan_enabled",
            "web_research": "web_research_enabled",
            "criticism": "criticism_enabled",
            "synthesize": "synthesize_enabled",
            "validate": "validate_enabled",
            "persist": "persist_enabled",
            "github_issue": "github_issue_enabled",
        }

        # Check config field directly
        if node_name in field_map:
            field_name = field_map[node_name]
            if hasattr(self, field_name):
                return getattr(self, field_name)

        # Fallback: check node_configs for backward compatibility
        node_config = self.node_configs.get(node_name)
        if node_config and node_config.enabled is not None:
            return node_config.enabled

        return True  # Default to enabled

    def get_enabled_nodes(self) -> list[str]:
        """Get list of all enabled node names."""
        return [node for node in self.get_all_node_names() if self.is_node_enabled(node)]

    def get_disabled_nodes(self) -> list[str]:
        """Get list of all disabled node names."""
        return [node for node in self.get_all_node_names() if not self.is_node_enabled(node)]

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
        log_config = self.logging_config

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
                node_logger.info("Node logger initialized for %s", node_name)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name under the research_agent namespace."""
    return logging.getLogger(f"research_agent.{name}")
