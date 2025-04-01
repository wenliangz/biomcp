import signal
import sys

import anyio
import typer

from .. import logger, mcp_app

server_app = typer.Typer(help="Server operations")


@server_app.command("run")
def run_server():
    """Run the BioMCP server with STDIO transport."""

    # Use a simpler approach - just force exit on SIGINT
    def handle_sigint(sig, frame):
        typer.echo("\nShutting down server...")
        sys.exit(0)

    # Register only for SIGINT
    signal.signal(signal.SIGINT, handle_sigint)

    logger.info("Starting MCP server... (v0.0.1)")
    try:
        anyio.run(mcp_app.run_stdio_async)
        logger.info("MCP server stopped gracefully.")
        return 0
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        return 1
