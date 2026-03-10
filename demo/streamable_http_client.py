#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcp>=1.1.1",
# ]
# ///
#
# Start the server first:
#   biomcp serve-http --host 127.0.0.1 --port 8080
#
# Then run this demo:
#   uv run --script demo/streamable_http_client.py
#   uv run --script demo/streamable_http_client.py http://127.0.0.1:8080

from __future__ import annotations

import asyncio
import sys
from datetime import timedelta

from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client

DEFAULT_BASE_URL = "http://127.0.0.1:8080"


async def main(base_url: str) -> None:
    mcp_url = f"{base_url.rstrip('/')}/mcp"
    print(f"Connecting to BioMCP at {mcp_url}")

    # The current Python MCP client warns on 202 Accepted during session teardown.
    async with streamable_http_client(
        mcp_url,
        terminate_on_close=False,
    ) as (read_stream, write_stream, _):
        async with ClientSession(
            read_stream,
            write_stream,
            read_timeout_seconds=timedelta(seconds=30),
        ) as session:
            initialize_result = await session.initialize()
            print(initialize_result.serverInfo)

            tools_result = await session.list_tools()
            print([tool.name for tool in tools_result.tools])

            call_result = await session.call_tool(
                "shell",
                arguments={"command": "biomcp version"},
            )
            for content in call_result.content:
                if isinstance(content, types.TextContent):
                    print(content.text)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL))
