"""MCP tools for resource access functionality."""

from mcp.server.fastmcp import Context
from pathlib import Path

RESOURCES_ROOT = Path(__file__).parent

async def register_resource_tools(mcp):
    """Register resource-related MCP tools."""
    
    @mcp.tool()
    async def get_instructions_tool(ctx: Context) -> str:
        """Get the instructions document.

        Args:
            ctx: The MCP server provided context

        Returns:
            The contents of the instructions document
        """
        try:
            return (RESOURCES_ROOT / "instructions.md").read_text()
        except Exception as e:
            return f"Error retrieving instructions: {str(e)}"

    @mcp.tool()
    async def get_researcher_tool(ctx: Context) -> str:
        """Get the researcher document.

        Args:
            ctx: The MCP server provided context

        Returns:
            The contents of the researcher document
        """
        try:
            return (RESOURCES_ROOT / "researcher.md").read_text()
        except Exception as e:
            return f"Error retrieving researcher document: {str(e)}" 