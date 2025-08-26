# Prompt Organization

## Overview

All prompts are centralized in `agent/prompts.py` for better maintainability and modification. For configuration details, see [CONFIGURATION_GUIDE.md](./CONFIGURATION_GUIDE.md).

## Benefits of Centralization

- Find and modify all prompts in one place
- Maintain consistency across different nodes
- Update messaging without touching core logic
- Add new prompts or variations easily

## Structure

### Centralized Prompts Class

The `ResearchPrompts` class in `agent/prompts.py` contains:

#### Planning Prompts

- `ALPHA_ONLY_RESEARCH_PLAN_TEMPLATE`: Template for alpha-only research plans
- `FULL_RESEARCH_PLAN_TEMPLATE`: Template for full research plans
- `ALPHA_ONLY_SEARCH_QUERIES`: Search query templates for alpha-only mode
- `FULL_SEARCH_QUERIES`: Search query templates for full mode

#### Research Prompts

- `PRIOR_ART_QUERIES`: Templates for GitHub prior art searches
- `CRITICISM_SYSTEM_PROMPT`: System prompt for critical analysis
- `CRITICISM_USER_PROMPT`: User prompt template for criticism
- `CRITICISM_CONTEXT_TEMPLATE`: Template for formatting criticism context
- `SYNTHESIS_SYSTEM_PROMPT`: Main system prompt for proposal synthesis
- `SYNTHESIS_USER_PROMPT`: User prompt template for synthesis
- `RESEARCH_CONTEXT_TEMPLATE`: Template for formatting research context

#### Validation & Error Messages

- `VALIDATION_*`: All validation success/failure messages
- `WEB_SEARCH_ERROR_*`: Error messages for failed web searches
- `PRIOR_ART_*_REASONING`: Templates for prior art analysis
- `PERSISTENCE_*`: Error messages for file persistence

### Helper Methods

The `ResearchPrompts` class includes utility methods:

- `get_alpha_mode_note()`: Returns alpha mode indicator
- `format_web_results()`: Formats web search results for context
- `format_validation_errors()`: Formats validation errors for repair
- `format_criticism_context()`: Formats context for criticism analysis
- `format_criticism_summary()`: Formats criticism results for synthesis
- `format_prior_art_summary()`: Formats prior art results for context
- `get_search_queries()`: Returns formatted search queries by mode
- `get_prior_art_queries()`: Returns formatted prior art queries
- `get_prior_art_reasoning()`: Determines verdict based on results count

## Node Changes

Each node has been updated to import and use the centralized prompts:

### plan.py

- Uses `ALPHA_ONLY_RESEARCH_PLAN_TEMPLATE` or `FULL_RESEARCH_PLAN_TEMPLATE`
- Gets search queries via `get_search_queries()`

### web_research.py

- Uses `WEB_SEARCH_ERROR_*` templates for error handling

### prior_art.py

- Uses `get_prior_art_queries()` for search queries
- Uses `get_prior_art_reasoning()` for verdict determination

### criticism.py

- Uses `CRITICISM_SYSTEM_PROMPT` and `CRITICISM_USER_PROMPT` for analysis
- Uses `format_criticism_context()` and `format_prior_art_summary()` for context
- Provides critical evaluation of research proposals before synthesis

### synthesize.py

- Uses `SYNTHESIS_SYSTEM_PROMPT` and `SYNTHESIS_USER_PROMPT`
- Uses `RESEARCH_CONTEXT_TEMPLATE` for context formatting
- Uses helper methods for web results and validation error formatting

### validate.py

- Uses `VALIDATION_*` templates for all user-facing messages
- Uses consistent error message formatting

### persist.py

- Uses `PERSISTENCE_*` templates for error messages

## Benefits

1. **Single Source of Truth**: All prompts are in one file
2. **Easy Modification**: Change messages without touching node logic
3. **Consistency**: Standardized formatting and messaging
4. **Maintainability**: Clear separation of prompts from business logic
5. **Testability**: Prompts can be easily unit tested
6. **Internationalization Ready**: Templates can be easily localized

## Usage Examples

### Modifying a Prompt

To change the alpha-only research plan template:

```python
# In agent/prompts.py
ALPHA_ONLY_RESEARCH_PLAN_TEMPLATE = """
New Research Plan for Alpha-Only Proposal: {idea}

Updated Focus Areas:
1. Enhanced market analysis...
2. Advanced alpha generation...
"""
```

### Adding New Error Messages

```python
# In agent/prompts.py
NEW_ERROR_TEMPLATE = "Custom error: {details}"

# In the node file
error_msg = ResearchPrompts.NEW_ERROR_TEMPLATE.format(details="specific error")
```

### Creating Prompt Variations

```python
# In agent/prompts.py
@classmethod
def get_research_plan(cls, idea: str, alpha_only: bool, advanced_mode: bool = False):
    if advanced_mode:
        template = cls.ADVANCED_RESEARCH_PLAN_TEMPLATE
    elif alpha_only:
        template = cls.ALPHA_ONLY_RESEARCH_PLAN_TEMPLATE
    else:
        template = cls.FULL_RESEARCH_PLAN_TEMPLATE

    return template.format(idea=idea)
```

## Future Enhancements

- Add prompt versioning for A/B testing
- Create prompt validation to ensure required placeholders exist
- Add prompt performance metrics
- Consider external prompt configuration files for non-technical users
