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
#   uv run --script demo/streamable_http_client.py --scenario braf-melanoma
#   uv run --script demo/streamable_http_client.py http://127.0.0.1:8080

from __future__ import annotations

import argparse
import asyncio
import json
import urllib.error
import urllib.request
from datetime import timedelta
from typing import TypeAlias

from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client

DEFAULT_BASE_URL = "http://127.0.0.1:8080"
HEALTH_TIMEOUT_SECONDS = 5
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
            "Step 3 - Trials: melanoma trials mentioning BRAF V600E",
            'biomcp search trial -c melanoma --mutation "BRAF V600E" --limit 5',
        ),
    ],
}

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the BioMCP Streamable HTTP demo workflow."
    )
    parser.add_argument(
        "base_url",
        nargs="?",
        default=DEFAULT_BASE_URL,
        help=f"Base BioMCP HTTP URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--scenario",
        default="braf-melanoma",
        choices=sorted(SCENARIOS),
        help="Named demo scenario to run.",
    )
    return parser.parse_args(argv)


def steps_for(scenario: str) -> list[ScenarioStep]:
    return SCENARIOS[scenario]


def check_health(base_url: str) -> None:
    health_url = f"{base_url.rstrip('/')}/health"
    try:
        with urllib.request.urlopen(
            health_url,
            timeout=HEALTH_TIMEOUT_SECONDS,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("status") != "ok":
            raise ValueError(f"unexpected payload: {payload!r}")
    except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
        raise SystemExit(
            "Health check failed at "
            f"{health_url}. Start the server first with "
            "biomcp serve-http --host 127.0.0.1 --port 8080. "
            f"Details: {exc}"
        ) from exc

    print(f"Health check passed: {health_url}")


async def main(base_url: str, scenario: str) -> None:
    mcp_url = f"{base_url.rstrip('/')}/mcp"
    print(f"Connecting to BioMCP at {mcp_url}")
    print(f"Scenario: {scenario}\n")

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
            tool_names = [tool.name for tool in tools_result.tools]
            print(f"Available tools: {', '.join(tool_names)}")

            for title, command in steps_for(scenario):
                print(f"\n=== {title} ===")
                print(f"Command: {command}")
                call_result = await session.call_tool(
                    "biomcp",
                    arguments={"command": command},
                )
                for content in call_result.content:
                    if isinstance(content, types.TextContent):
                        print(content.text)


if __name__ == "__main__":
    args = parse_args()
    check_health(args.base_url)
    asyncio.run(main(args.base_url, args.scenario))
