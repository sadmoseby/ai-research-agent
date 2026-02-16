"""
State management for the Lean Research Agent using LangGraph.
"""

from dataclasses import dataclass
from enum import IntFlag
from typing import Any, Dict, List, Optional, TypedDict


class ResearchComponents(IntFlag):
    UNIVERSE = 1 << 0
    ALPHA = 1 << 1
    PORTFOLIO = 1 << 2
    EXECUTION = 1 << 3
    RISK = 1 << 4


class ResearchState(TypedDict, total=False):
    """State structure for the research agent workflow."""

    # Input
    idea: str
    alpha_only: bool
    components: ResearchComponents
    instruments: List[str]  # Financial instruments: stocks, options, futures, forex, crypto
    slug: str
    output_dir: str  # Output directory for proposal files
    upload_to_github: bool  # Whether to create a GitHub issue after persisting
    bootstrap_config_path: Optional[str]  # Path to bootstrap config (for GitHub auth)

    # Current step tracking
    current_step: str

    # Planning phase
    research_plan: Optional[str]
    search_queries: Optional[List[str]]
    mcp_tools_available: Optional[List[str]]  # Track available MCP tools

    # Research phase
    web_search_results: Optional[List[Dict[str, Any]]]
    component_research_results: Optional[Dict[str, List[Dict[str, Any]]]]  # Component-specific results
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
    state_path: Optional[str]
    issue_path: Optional[str]
    github_issue_url: Optional[str]

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
