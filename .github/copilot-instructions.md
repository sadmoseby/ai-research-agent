# Lean Research Agent - Copilot Instructions

## Overview

You are building a **Lean Research Agent** that, when executed, generates **only** a research proposal JSON file under the `proposals/` directory, conforming precisely to the schema at `schema/lean-research-schema.json`.

## Requirements for Copilot-generated Code

- **Orchestration:** Use **LangGraph** with checkpointed state.
- **Proposal Generation:** Use OpenAI’s **Responses API** with the `web_search` tool and **Structured Outputs (json_schema, strict)**.
- **Fallback Search (Optional):** Include search with **Tavily** via LangChain.
- **Prior-Art Check:** Use GitHub’s `/search/code` API. Record results (URLs + verdict) under `misc.prior_art`.
- **Validation:** Use `jsonschema` (Draft 2020-12) to validate the output against the provided schema.
  - On validation failure, perform one repair attempt (feed errors back into the model), then halt with a clear error.
- **Output:** Write the final valid proposal to `proposals/<slug>.json` where the slug is based on the idea text.
- **Trading Logic:** Do not generate trading logic—only include plain-language descriptions in `text` fields.
- **Alpha-only Flag:**
  - Enforce exactly one alpha (`alphas.new` or `alphas.amend`) **and** one `universe.existing`.
  - All other model categories must be absent or empty.

## Project Structure

```
/agent/
  __init__.py
  config.py
  graph.py
  state.py
  nodes/
    plan.py
    web_research.py
    prior_art.py
    synthesize.py
    validate.py
    persist.py
  tools/
    github_api.py
    tavily_tool.py
    __init__.py

/cli.py
/requirements.txt
/schema/lean-research-schema.json      # Provided schema (as-is)
/proposals/.gitkeep
/.github/workflows/validate-proposal.yml
```

## Environment Variables

- `OPENAI_API_KEY` (required)
- `GITHUB_TOKEN` (for search/code prior-art)
- `TAVILY_API_KEY` (optional fallback)

## Run Targets

- Command:
  `python cli.py propose --idea "<free text>" [--alpha-only] [--slug carry_trend]`
- Behavior:
  Writes `proposals/<slug>.json` and prints a validation report.

## Authoring rules for the agent

- Never emit code for Lean models; put logic only in each component’s text.

- Include research metadata (citations, prior-art verdict) under misc.* (schema allows extras).

- If validation fails, attempt one repair loop (show validator errors to the model) then exit with a clear message.
