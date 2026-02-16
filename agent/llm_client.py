"""
LangChain-based LLM client supporting multiple providers.
"""

import json
import os
from typing import Any, Dict, List, Optional, Type, Union

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

# Import LangChain provider modules
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None

from .config import Config, LLMProviderConfig


class LLMClient:
    """Unified LLM client using LangChain for multiple providers."""

    def __init__(self, config: Config, node_name: Optional[str] = None):
        """Initialize the LLM client.

        Args:
            config: Configuration object
            node_name: Optional node name for node-specific configuration
        """
        self.config = config
        self.node_name = node_name
        self._client_cache: Dict[str, BaseChatModel] = {}

        # Get effective configuration for this node
        if node_name:
            self.node_config = config.get_node_config(node_name)
        else:
            # Use default provider configuration
            default_provider_config = config.default_config.llm_provider
            if not default_provider_config:
                raise ValueError(f"Default provider '{config.default_config.llm_provider.provider}' not configured")

            self.node_config = {
                "provider": config.default_config.llm_provider.provider,
                "provider_config": default_provider_config,
                "model": default_provider_config.model,
                "temperature": default_provider_config.temperature,
                "max_tokens": default_provider_config.max_tokens,
            }

    def _get_client(self, provider: Optional[str] = None) -> BaseChatModel:
        """Get or create a LangChain client for the specified provider."""
        provider = provider or self.node_config["provider"]

        if provider in self._client_cache:
            return self._client_cache[provider]

        # Use node configuration values, not hardcoded provider defaults
        if "provider_config" in self.node_config:
            # Use the provider config from node configuration
            provider_config = self.node_config["provider_config"]
        else:
            # Fallback to provider defaults if no node config available
            provider_config = self.config.get_provider_config(provider)
            if not provider_config:
                raise ValueError(f"Provider '{provider}' not configured")

        # Get API key from environment
        api_key = None
        if provider_config.api_key_env and provider != "ollama":
            api_key = os.getenv(provider_config.api_key_env)
            if not api_key:
                raise ValueError(f"API key not found in environment variable '{provider_config.api_key_env}'")
        elif provider_config.api_key_env and provider == "ollama":
            # Ollama typically doesn't need an API key for local usage
            api_key = os.getenv(provider_config.api_key_env)  # Optional for Ollama

        client = self._create_provider_client(provider_config, api_key)
        self._client_cache[provider] = client
        return client

    def _create_provider_client(self, provider_config: LLMProviderConfig, api_key: Optional[str]) -> BaseChatModel:
        """Create a provider-specific LangChain client."""
        base_kwargs = {
            "model": provider_config.model,
            "temperature": provider_config.temperature,
            "max_tokens": provider_config.max_tokens,
            **provider_config.extra_kwargs,
        }

        if provider_config.provider == "openai":
            if not ChatOpenAI:
                raise ImportError("langchain-openai not installed. Run: pip install langchain-openai")
            return ChatOpenAI(api_key=api_key, **base_kwargs)

        elif provider_config.provider == "anthropic":
            if not ChatAnthropic:
                raise ImportError("langchain-anthropic not installed. Run: pip install langchain-anthropic")
            return ChatAnthropic(api_key=api_key, **base_kwargs)

        elif provider_config.provider == "gemini":
            if not ChatGoogleGenerativeAI:
                raise ImportError("langchain-google-genai not installed. Run: pip install langchain-google-genai")
            return ChatGoogleGenerativeAI(google_api_key=api_key, **base_kwargs)

        elif provider_config.provider == "ollama":
            if not ChatOllama:
                raise ImportError("langchain-ollama not installed. Run: pip install langchain-ollama")
            return ChatOllama(
                base_url=provider_config.base_url or "http://localhost:11434",
                **base_kwargs,
            )

        else:
            raise ValueError(f"Unsupported provider: {provider_config.provider}")

    async def chat_completion(self, messages: List[Dict[str, str]], provider: Optional[str] = None, **kwargs) -> str:
        """Generate a chat completion.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            provider: Optional provider override
            **kwargs: Additional parameters for the model

        Returns:
            Generated response text
        """
        client = self._get_client(provider)

        # Convert messages to LangChain format
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role in ["user", "human"]:
                langchain_messages.append(HumanMessage(content=content))
            else:
                # For assistant/ai messages, treat as human for simplicity
                langchain_messages.append(HumanMessage(content=content))

        # Generate response
        response = await client.ainvoke(langchain_messages, **kwargs)
        return response.content

    async def structured_completion(
        self,
        messages: List[Dict[str, str]],
        response_model: Type[BaseModel],
        provider: Optional[str] = None,
        **kwargs,
    ) -> BaseModel:
        """Generate a structured completion using Pydantic models.

        Args:
            messages: List of message dictionaries
            response_model: Pydantic model class for structured output
            provider: Optional provider override
            **kwargs: Additional parameters

        Returns:
            Instance of response_model
        """
        client = self._get_client(provider)

        # Create parser and prompt
        parser = PydanticOutputParser(pydantic_object=response_model)

        # Add format instructions to the last message
        format_instructions = parser.get_format_instructions()
        if messages:
            last_message = messages[-1].copy()
            last_message["content"] += f"\n\n{format_instructions}"
            messages = messages[:-1] + [last_message]

        # Convert to LangChain messages
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))

        # Generate and parse response
        response = await client.ainvoke(langchain_messages, **kwargs)
        return parser.parse(response.content)

    async def json_completion(
        self,
        messages: List[Dict[str, str]],
        json_schema: Dict[str, Any],
        provider: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate a JSON completion with schema validation.

        Args:
            messages: List of message dictionaries
            json_schema: JSON schema for validation
            provider: Optional provider override
            **kwargs: Additional parameters

        Returns:
            Parsed JSON response
        """
        client = self._get_client(provider)

        # Add JSON format instructions
        schema_str = json.dumps(json_schema, indent=2)
        format_instruction = f"""
Please respond with valid JSON that conforms to this schema:

{schema_str}

Your response should be JSON only, no additional text or explanations.
"""

        if messages:
            last_message = messages[-1].copy()
            last_message["content"] += format_instruction
            messages = messages[:-1] + [last_message]

        # Convert to LangChain messages
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))

        # Generate response
        response = await client.ainvoke(langchain_messages, **kwargs)

        # Parse JSON response
        try:
            content = response.content.strip()

            # Strip markdown code blocks if present (handle truncated responses too)
            if content.startswith("```"):
                # Find the start of actual JSON content (first { or [)
                json_start = -1
                for i, ch in enumerate(content):
                    if ch in "{[":
                        json_start = i
                        break
                if json_start != -1:
                    content = content[json_start:]
                    # Remove trailing ``` if present (may be absent if response was truncated)
                    if content.endswith("```"):
                        content = content[:-3].strip()
                    else:
                        content = content.strip()

            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response.content}")

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the currently configured provider."""
        return {
            "provider": self.node_config["provider"],
            "model": self.node_config["model"],
            "temperature": self.node_config["temperature"],
            "max_tokens": self.node_config["max_tokens"],
            "node_name": self.node_name,
        }

    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """Get a dict of providers and their availability status."""
        return {
            "openai": ChatOpenAI is not None,
            "anthropic": ChatAnthropic is not None,
            "gemini": ChatGoogleGenerativeAI is not None,
            "ollama": ChatOllama is not None,
        }


# Backward compatibility function
def create_openai_client(config: Config, node_name: Optional[str] = None):
    """Create an OpenAI-compatible client (for backward compatibility)."""
    llm_client = LLMClient(config, node_name)

    class OpenAICompatClient:
        def __init__(self, llm_client: LLMClient):
            self._llm_client = llm_client

        async def chat_completions_create(self, messages, model=None, **kwargs):
            response_text = await self._llm_client.chat_completion(
                messages=[{"role": msg.get("role", "user"), "content": msg.get("content", "")} for msg in messages],
                **kwargs,
            )

            # Mock OpenAI response format
            class MockChoice:
                def __init__(self, content):
                    self.message = type("Message", (), {"content": content})()
                    self.finish_reason = "stop"

            class MockResponse:
                def __init__(self, content):
                    self.choices = [MockChoice(content)]
                    self.usage = type("Usage", (), {"total_tokens": 0})()

            return MockResponse(response_text)

        def beta_chat_completions_parse(self, messages, response_format, model=None, **kwargs):
            # For structured outputs, this would need to be implemented
            # based on the specific response_format
            raise NotImplementedError("Structured outputs not yet supported in compatibility mode")

    return OpenAICompatClient(llm_client)
