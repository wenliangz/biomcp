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
from typing import TypeAlias

from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client

DEFAULT_BASE_URL = "http://127.0.0.1:8080"
ScenarioStep: TypeAlias = tuple[str, str]

# Named demo scenarios keep the workflow loop stable as stories expand.
SCENARIOS: dict[str, list[ScenarioStep]] = {
    "braf-melanoma": [
        (
            "Step 1 - Discovery: BRAF in melanoma",
            "biomcp search all --gene BRAF --disease melanoma --counts-only",
        ),
        (
            "Step 2 - Evidence: BRAF V600E ClinVar evidence",
            'biomcp get variant "BRAF V600E" clinvar',
        ),
        (
            "Step 3 - Trials: BRAF V600E clinical trials",
            'biomcp variant trials "BRAF V600E" --limit 5',
        ),
    ],
}

# Change this constant to run a different named scenario.
SCENARIO = "braf-melanoma"


def selected_steps() -> list[ScenarioStep]:
    try:
        return SCENARIOS[SCENARIO]
    except KeyError as exc:
        available = ", ".join(sorted(SCENARIOS))
        raise SystemExit(
            f"Unknown demo scenario {SCENARIO!r}. Available scenarios: {available}"
        ) from exc


async def main(base_url: str) -> None:
    mcp_url = f"{base_url.rstrip('/')}/mcp"
    print(f"Connecting to BioMCP at {mcp_url}\n")

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

            for title, command in selected_steps():
                print(f"\n=== {title} ===")
                call_result = await session.call_tool(
                    "shell",
                    arguments={"command": command},
                )
                for content in call_result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL))
