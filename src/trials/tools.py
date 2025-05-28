"""MCP tools for clinical trial search functionality."""

from mcp.server.fastmcp import Context

from src.trials.search import TrialQuery, search_trials
from src.trials.getter import get_trial, Module

async def register_trial_tools(mcp):
    """Register trial-related MCP tools."""
    
    @mcp.tool()
    async def search_trials_tool(ctx: Context, query: str, limit: int = 3) -> str:
        """Search for clinical trials using semantic search.

        Args:
            ctx: The MCP server provided context
            query: Search query string describing what you're looking for
            limit: Maximum number of results to return (default: 3)
        """
        try:
            trial_query = TrialQuery(
                terms=[query],  # Use the query as a search term
                size=limit
            )
            return await search_trials(trial_query, output_json=True)
        except Exception as e:
            return f"Error searching trials: {str(e)}"

    @mcp.tool()
    async def get_trial_tool(ctx: Context, trial_id: str) -> str:
        """Get detailed information about a specific clinical trial.

        Args:
            ctx: The MCP server provided context
            trial_id: The identifier of the trial to retrieve
        """
        try:
            return await get_trial(trial_id)
        except Exception as e:
            return f"Error retrieving trial: {str(e)}"

    @mcp.tool()
    async def trial_protocol_tool(ctx: Context, nct_id: str) -> str:
        """Get core protocol information for a clinical trial.

        Args:
            ctx: The MCP server provided context
            nct_id: The NCT ID of the trial (e.g., "NCT04280705")

        Returns:
            A Markdown formatted string with protocol details including title,
            status, sponsor, purpose, study design, phase, interventions,
            and eligibility criteria
        """
        try:
            return await get_trial(nct_id, Module.PROTOCOL)
        except Exception as e:
            return f"Error retrieving trial protocol: {str(e)}"

    @mcp.tool()
    async def trial_locations_tool(ctx: Context, nct_id: str) -> str:
        """Get contact and location details for a clinical trial.

        Args:
            ctx: The MCP server provided context
            nct_id: The NCT ID of the trial (e.g., "NCT04280705")

        Returns:
            A Markdown formatted string with facility names, addresses,
            and contact information
        """
        try:
            return await get_trial(nct_id, Module.LOCATIONS)
        except Exception as e:
            return f"Error retrieving trial locations: {str(e)}"

    @mcp.tool()
    async def trial_outcomes_tool(ctx: Context, nct_id: str) -> str:
        """Get outcome measures and results for a clinical trial.

        Args:
            ctx: The MCP server provided context
            nct_id: The NCT ID of the trial (e.g., "NCT04280705")

        Returns:
            A Markdown formatted string with primary/secondary outcomes,
            participant flow, results tables, and adverse event summaries
        """
        try:
            return await get_trial(nct_id, Module.OUTCOMES)
        except Exception as e:
            return f"Error retrieving trial outcomes: {str(e)}"

    @mcp.tool()
    async def trial_references_tool(ctx: Context, nct_id: str) -> str:
        """Get publications and references for a clinical trial.

        Args:
            ctx: The MCP server provided context
            nct_id: The NCT ID of the trial (e.g., "NCT04280705")

        Returns:
            A Markdown formatted string with citations, PubMed IDs,
            and reference types
        """
        try:
            return await get_trial(nct_id, Module.REFERENCES)
        except Exception as e:
            return f"Error retrieving trial references: {str(e)}" 