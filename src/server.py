"""MCP server implementation."""

from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
import json
import os
import asyncio

from variants.tools import register_variant_tools
from trials.tools import register_trial_tools
from articles.tools import register_article_tools
from resources.tools import register_resource_tools

load_dotenv()

# Create a dataclass for our application context
@dataclass
class WeBioMCPContext:
    """Context for the WeBioMCP server."""
    pass

@asynccontextmanager
async def webiomcp_lifespan(server: FastMCP) -> AsyncIterator[WeBioMCPContext]:
    """Manages the WeBioMCP server lifecycle."""
    try:
        yield WeBioMCPContext()
    finally:
        pass

# Initialize FastMCP server
mcp = FastMCP(
    "webiomcp",
    description="MCP server for biomedical data access and analysis",
    lifespan=webiomcp_lifespan,
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "8000"))
)

async def main():
    """Run the WeBioMCP server."""
    # Register module-specific tools
    await register_variant_tools(mcp)
    await register_trial_tools(mcp)
    await register_article_tools(mcp)
    await register_resource_tools(mcp)
    
    transport = os.getenv("TRANSPORT", "sse")
    print(f"Starting WeBioMCP server with {transport} transport...")
    
    if transport == 'sse':
        await mcp.run_sse_async()
    else:
        await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main()) 