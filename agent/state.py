"""
State management for the Lean Research Agent using LangGraph.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict


class ResearchState(TypedDict, total=False):
    """State structure for the research agent workflow."""

    # Input
    idea: str
    alpha_only: bool
    slug: str

    # Current step tracking
    current_step: str

    # Planning phase
    research_plan: Optional[str]
    search_queries: Optional[List[str]]
    mcp_tools_available: Optional[List[str]]  # Track available MCP tools

    # Research phase
    web_search_results: Optional[List[Dict[str, Any]]]
    prior_art_results: Optional[Dict[str, Any]]
    mcp_tools_used: Optional[List[str]]  # Track which tools were actually used

    # Criticism phase
    criticism_results: Optional[Dict[str, Any]]
    criticism_score: Optional[float]

    # Flow control
    should_restart_planning: bool
    restart_reason: Optional[str]
    planning_iteration: int

    # Synthesis phase
    raw_proposal: Optional[Dict[str, Any]]

    # Validation phase
    validation_errors: Optional[List[str]]
    validation_report: Optional[str]

    # Output
    final_proposal: Optional[Dict[str, Any]]
    proposal_path: Optional[str]

    # Error handling
    error: Optional[str]
    repair_attempts: int


@dataclass
class SearchResult:
    """Structure for search results."""

    title: str
    url: str
    content: str
    source: str  # "openai_web" or "tavily"


@dataclass
class PriorArtResult:
    """Structure for prior art check results."""

    query: str
    github_results: List[Dict[str, Any]]
    verdict: str  # "novel", "similar", "duplicate"
    reasoning: str
