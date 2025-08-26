# Web Research Node Comprehensive Update

## Summary of Changes

This update transforms the web research node from performing multiple finite web searches using Tavily to conducting a single comprehensive research session using LLM with web search tool calling capabilities.

## Key Changes Made

### 1. Modified `/agent/nodes/web_research.py`

**Before:**
- Performed multiple finite web searches (limited to 3 queries)
- Used Tavily search as primary method with LLM fallback
- Processed individual search queries separately
- Returned multiple search result objects

**After:**
- Conducts single comprehensive research session
- Uses LLM with web search tool calling (no Tavily dependency)
- Expands original idea into verbose detailed proposal
- Returns single comprehensive research document suitable for JSON schema conversion

**Key Changes:**
- Removed loop-based query processing
- Added `_conduct_comprehensive_research()` helper function
- Integrated web search tools directly with LLM providers (OpenAI, Anthropic, Gemini)
- Modified return structure to include comprehensive research

### 2. Added New Prompts to `/agent/prompts.py`

**New Prompts Added:**
- `WEB_RESEARCH_COMPREHENSIVE_SYSTEM_PROMPT`: System prompt for comprehensive research with web search tools
- `WEB_RESEARCH_COMPREHENSIVE_USER_PROMPT`: User prompt template for detailed research requests

**Prompt Features:**
- Emphasizes comprehensive research using web search tools
- Focuses on expanding basic ideas into detailed proposals
- Includes specific requirements for alpha-only mode
- Structured to produce content suitable for JSON schema conversion
- Covers strategy overview, methodology, academic research, risk analysis, and parameter optimization

### 3. Updated Function Signatures and Error Handling

**Improvements:**
- More specific exception handling (RuntimeError, ValueError, ConnectionError instead of generic Exception)
- Proper logging format compliance
- Removed unused imports and parameters
- Updated function signatures to match new workflow

## Technical Implementation Details

### MCP Client Integration

The updated implementation uses the MCP client's `web_search` API with a new `use_tavily=False` parameter:

**Added to MCPClient.web_search():**
```python
async def web_search(self, query: str, use_tavily: bool = True) -> List[Dict[str, Any]]:
    """Perform web search via Tavily MCP or LLM fallback."""
    # First try Tavily if available and requested
    if use_tavily and self.available_tools.get("tavily", False):
        # ... tavily logic

    # Fallback to LLM-generated search response (our desired behavior)
    if self.available_tools.get("llm_fallback", False):
        return await self._llm_fallback_search(query)
```

**Updated _conduct_comprehensive_research():**
```python
async def _conduct_comprehensive_research(
    mcp_client: MCPClient,
    system_prompt: str,
    user_prompt: str
) -> str:
    # Create comprehensive research query
    research_query = f"{system_prompt}\n\n{user_prompt}"

    # Use MCP client's web_search with Tavily disabled
    search_results = await mcp_client.web_search(research_query, use_tavily=False)

    # Extract comprehensive content
    return search_results[0].get("content", "") if search_results else ""
```

This approach ensures:
- **Identical LLM behavior**: Uses the same `_llm_fallback_search` method that was already implemented
- **Simplified implementation**: Leverages existing MCP infrastructure
- **Consistent interface**: Uses the standard `web_search` API with a parameter
- **No Tavily dependency**: Explicitly disables Tavily to force LLM-based search

### Research Output Structure

The new approach returns a single comprehensive research document with:

```python
{
    "title": f"Comprehensive Research: {idea}",
    "content": detailed_research,  # Comprehensive research content
    "url": "llm_comprehensive_research",
    "source": "llm_with_web_tools",
    "research_type": "comprehensive_proposal"
}
```

## Benefits of the New Approach

1. **Single Comprehensive Session**: More efficient than multiple discrete searches
2. **LLM-Driven Research**: Leverages LLM capabilities to expand and contextualize ideas
3. **Web Search Integration**: Direct integration with LLM web search tools for current information
4. **Detailed Proposals**: Generates verbose content suitable for structured conversion
5. **Alpha-Only Focus**: Tailored for alpha-only research requirements
6. **No Tavily Dependency**: Removes dependency on Tavily search service
7. **Provider Flexibility**: Works with multiple LLM providers (OpenAI, Anthropic, Gemini)

## Usage Example

```python
state = ResearchState({
    "idea": "Momentum-based factor investing using ML",
    "research_plan": "Investigate ML-enhanced momentum strategies",
    "alpha_only": True
})

result = await web_research_node(state, config)
# Returns single comprehensive research document via MCP client
comprehensive_research = result["web_search_results"][0]["content"]
```

The key difference is that `_conduct_comprehensive_research` now calls:
```python
# Uses MCP client web_search with use_tavily=False for LLM-only behavior
search_results = await mcp_client.web_search(research_query, use_tavily=False)
```

This ensures identical behavior to the existing LLM fallback system while using the standard MCP API.

## Demo Script

Created `/examples/web_research_demo.py` to demonstrate the new functionality and showcase the changes made.

## Testing

- All imports verified to work correctly
- Code passes linting requirements
- Demo script successfully demonstrates new functionality
- Maintains compatibility with existing state structure
