# Design: P049 — Streamable HTTP Demo Polish

## Problem Summary

The current `demo/streamable_http_client.py` works, but it is still a developer
artifact rather than a polished public demo.

1. **The story breaks at step 3.** The current scenario ends with
   `biomcp variant trials "BRAF V600E" --limit 5`, which is mutation-only and
   currently returns a broad cross-indication result set. In local review on
   2026-03-11 this surface showed `455` total results, which weakens the
   melanoma narrative set up by steps 1 and 2.
2. **There is no `demo/README.md`.** Setup, run instructions, and expected
   output cues currently live only in the script header.
3. **Scenario selection requires editing source.** The script still uses a
   top-level `SCENARIO = "braf-melanoma"` constant plus `selected_steps()`.
4. **Startup failures are not newcomer-friendly.** The script jumps straight
   into MCP session setup, so a dead server fails with lower-level transport
   errors instead of a clear "start the server first" message.
5. **Local version confusion is real.** The running server may come from a
   different `biomcp` binary than the one on `PATH`; the design has to make the
   release-binary path explicit in docs and dev verification.
6. **The terminal output needs a little more framing.** For screenshots and
   recordings, the demo should print scenario and command context, not only raw
   BioMCP output.

First-run `uv` dependency installation noise is also a polish issue, but that
belongs in documentation (`uv run --quiet`), not in runtime logic.

## Verified Facts From The Current Codebase

- `demo/streamable_http_client.py` currently defines `SCENARIO` and
  `selected_steps()` and accepts only an optional positional base URL.
- `tests/test_streamable_http_demo.py` currently covers `selected_steps()` and
  the PEP 723 Python-floor contract, but not CLI parsing or health-check UX.
- Streamable HTTP probe routes are real and stable:
  `GET /health` and `GET /readyz` both return `{"status": "ok"}`. This is
  covered by `tests/test_mcp_http_surface.py` and implemented in
  `src/mcp/shell.rs`.
- The live MCP tool name is `biomcp`, not `shell`. This is covered by
  `tests/test_mcp_http_transport.py`.
- `variant trials` does **not** accept a disease filter. The current parser in
  `src/cli/mod.rs` only exposes `id`, `--limit`, `--offset`, and `--source`.
- The supported disease-scoped alternative already exists:
  `biomcp search trial -c melanoma --mutation "BRAF V600E" --limit 5`.
  A live run on 2026-03-11 returned `Results: 5 of 104` with query echo
  `condition=melanoma, mutation=BRAF V600E`.
- Existing docs-contract tests already describe the demo in
  `docs/getting-started/remote-http.md`,
  `analysis/technical/overview.md`, and
  `tests/test_docs_changelog_refresh.py`; these must move with the demo.

## Product Decisions

**Primary optimization**: prove BioMCP scientific usefulness over Streamable
HTTP. Pure transport correctness is already covered elsewhere by
`tests/test_mcp_http_transport.py`; this demo should foreground a coherent
research story.

**Output shape**: keep real BioMCP markdown output, not a custom summary mode.
The polish work is limited to lightweight framing lines around that output:
health line, connection line, scenario line, available-tools line, section
title, and the command being executed.

**Disease scoping for step 3**: use the existing `search trial` surface instead
of trying to extend `variant trials`. The demo should rely on current repo
capabilities, not invent a new CLI flag during polish work.

**Narrative expectation**: the step-3 query must be explicitly melanoma-scoped,
but results may still include multi-indication basket trials whose condition
lists contain melanoma among other diseases. Verify should assert the query echo
contains `condition=melanoma, mutation=BRAF V600E`; it should not require every
returned row to be melanoma-only.

**CLI vs MCP comparison**: out of scope for this ticket.

**Health prelude**: add only a lightweight `GET /health` check before opening
the MCP session. `/readyz` exists, but duplicating both probes in the demo adds
noise without improving the newcomer story.

**Two demos / `--json` / artifact capture**: out of scope for this ticket.

**Spec impact**: no `spec/` change is required. This ticket changes a demo
artifact plus documentation/tests around that artifact; the numbered CLI
behavior specs remain the wrong proof surface here.

## Architecture Decisions

### 1. Replace `SCENARIO` with `parse_args(argv=None)`

Add `argparse` to the demo script and expose:

- optional positional `base_url` with default `http://127.0.0.1:8080`
- optional `--scenario` flag with `choices=sorted(SCENARIOS)`

Use:

```python
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
```

This signature is valid on Python 3.11 because the file already uses
`from __future__ import annotations`.

Remove the `SCENARIO` constant and `selected_steps()` helper. Replace them with
`steps_for(scenario: str) -> list[ScenarioStep]` that directly indexes
`SCENARIOS`; `argparse` now owns unknown-scenario validation.

### 2. Add `check_health(base_url)` using `urllib.request`

No new dependency is needed. `check_health()` should:

- call `GET {base_url.rstrip('/')}/health`
- parse JSON and require `{"status": "ok"}`
- print `Health check passed: <url>` on success
- raise `SystemExit` on failure with a message that:
  - names the probe URL that failed
  - tells the user to start `biomcp serve-http --host 127.0.0.1 --port 8080`
  - is clear enough for a first-time user reading a screenshot/log

The runtime error message should stay generic and portable. The version-aligned
release-binary guidance belongs in README/dev verification, not in the script's
fatal path.

### 3. Tighten step 3 using the supported trial search surface

Do **not** implement this:

```bash
biomcp variant trials "BRAF V600E" --disease melanoma --limit 5
```

That flag does not exist on the current CLI.

Use this existing command instead:

```bash
biomcp search trial -c melanoma --mutation "BRAF V600E" --limit 5
```

Update the step title accordingly, for example:

```text
Step 3 - Trials: melanoma trials mentioning BRAF V600E
```

This keeps the demo coherent without requiring new CLI functionality.

### 4. Add explicit command framing to each step

Before each MCP tool call, print the exact BioMCP command being executed:

```text
=== Step 2 - Evidence: BRAF V600E ClinVar evidence ===
Command: biomcp get variant "BRAF V600E" clinvar
```

This is important for screenshot/recording readability and makes the MCP run
easier to compare mentally with everyday CLI use.

### 5. Add `demo/README.md`

Create a short standalone README that covers:

- what the demo proves
- how to start the server
- how to run the client
- how to choose a scenario
- what output to expect, using structural markers rather than brittle exact data
- how to avoid first-run `uv` noise with `uv run --quiet`
- version-alignment guidance:
  - installed `biomcp` is fine for normal use
  - for repo verification, prefer `./target/release/biomcp serve-http ...`
    so the server version matches the checked-out code

### 6. Update existing demo-facing docs contracts

Because the repo already describes the Streamable HTTP demo outside the script,
the implementation must update these surfaces too:

- `docs/getting-started/remote-http.md`
- `analysis/technical/overview.md`
- `tests/test_docs_changelog_refresh.py`

The goal is not a docs rewrite. The goal is to keep existing newcomer/runtime
documentation aligned with the polished demo story and the removal of the
`SCENARIO` constant.

## File Disposition

| File | Action | Notes |
|------|--------|-------|
| `demo/streamable_http_client.py` | Modify | add argparse, remove `SCENARIO`, add health check, print command context, switch step 3 to `search trial -c melanoma --mutation ...` |
| `demo/README.md` | Create | newcomer-facing demo guide with expected-output sketch and version-alignment note |
| `tests/test_streamable_http_demo.py` | Modify | replace `selected_steps()` tests with parse/health/scenario assertions |
| `docs/getting-started/remote-http.md` | Modify | update the documented three-step demo workflow and mention the new scenario flag |
| `analysis/technical/overview.md` | Modify | keep the technical overview aligned with the actual polished demo behavior |
| `tests/test_docs_changelog_refresh.py` | Modify | update contract assertions for the demo script and remote-http overview |

No `spec/` files are part of this change.

## Implementation Notes

### `demo/streamable_http_client.py`

Representative structure:

```python
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
ScenarioStep: TypeAlias = tuple[str, str]

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
        description="BioMCP Streamable HTTP demo client.",
    )
    parser.add_argument(
        "base_url",
        nargs="?",
        default=DEFAULT_BASE_URL,
        help=f"Base URL of the BioMCP server (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--scenario",
        default="braf-melanoma",
        choices=sorted(SCENARIOS),
        help="Named demo scenario to run (default: braf-melanoma)",
    )
    return parser.parse_args(argv)


def steps_for(scenario: str) -> list[ScenarioStep]:
    return SCENARIOS[scenario]


def check_health(base_url: str) -> None:
    url = f"{base_url.rstrip('/')}/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError) as exc:
        raise SystemExit(
            f"Cannot reach BioMCP server at {url}: {exc}\n"
            "Start the server first:\n"
            "  biomcp serve-http --host 127.0.0.1 --port 8080"
        ) from exc
    if body.get("status") != "ok":
        raise SystemExit(f"Unexpected health response from {url}: {body}")
    print(f"Health check passed: {url}")


async def main(base_url: str, scenario: str) -> None:
    check_health(base_url)

    mcp_url = f"{base_url.rstrip('/')}/mcp"
    print(f"Connecting to BioMCP at {mcp_url}")
    print(f"Running scenario: {scenario}\n")

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
            print(f"Available tools: {', '.join(tool_names)}\n")

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
```

Notes:

- Keep `terminate_on_close=False`; this is still required because of the known
  Python MCP client warning on valid `202 Accepted` session teardown.
- Keep the script standalone and runnable as a PEP 723 artifact.
- Do not add CLI-vs-MCP diff logic or artifact-capture mode in this ticket.

### `tests/test_streamable_http_demo.py`

Replace the current constant-driven tests with focused coverage for the polished
demo contract:

```python
def test_parse_args_defaults() -> None:
    module = _load_demo_module()
    args = module.parse_args([])
    assert args.scenario == "braf-melanoma"
    assert args.base_url == module.DEFAULT_BASE_URL


def test_parse_args_rejects_unknown_scenario() -> None:
    module = _load_demo_module()
    with pytest.raises(SystemExit):
        module.parse_args(["--scenario", "missing"])


def test_parse_args_accepts_positional_url_and_scenario() -> None:
    module = _load_demo_module()
    args = module.parse_args(
        ["http://10.0.0.1:9000", "--scenario", "braf-melanoma"]
    )
    assert args.base_url == "http://10.0.0.1:9000"
    assert args.scenario == "braf-melanoma"


def test_check_health_failure_message_mentions_start_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_demo_module()

    def fail(*args, **kwargs):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(module.urllib.request, "urlopen", fail)

    with pytest.raises(SystemExit, match="biomcp serve-http --host 127.0.0.1 --port 8080"):
        module.check_health(module.DEFAULT_BASE_URL)


def test_braf_melanoma_step3_uses_trial_search_with_condition_and_mutation() -> None:
    module = _load_demo_module()
    _, step3_cmd = module.SCENARIOS["braf-melanoma"][2]
    assert step3_cmd == (
        'biomcp search trial -c melanoma --mutation "BRAF V600E" --limit 5'
    )


def test_demo_python_floor_matches_syntax() -> None:
    # keep the existing floor/syntax contract unchanged
    ...
```

### `demo/README.md`

Expected content shape:

````markdown
# BioMCP Streamable HTTP Demo

This demo proves that the live `biomcp` MCP tool is reachable over Streamable
HTTP and can drive a coherent BRAF/melanoma workflow end to end.

## Start the server

For repo-local verification, prefer the checked-out release binary:

```bash
./target/release/biomcp serve-http --host 127.0.0.1 --port 8080
```

Installed binary also works:

```bash
biomcp serve-http --host 127.0.0.1 --port 8080
```

## Run the demo

```bash
uv run --script demo/streamable_http_client.py
uv run --script demo/streamable_http_client.py --scenario braf-melanoma
uv run --quiet --script demo/streamable_http_client.py
```

## Expected output

Look for these structural markers:

- `Health check passed: http://127.0.0.1:8080/health`
- `Connecting to BioMCP at http://127.0.0.1:8080/mcp`
- `Available tools: biomcp`
- `Command: biomcp search all --gene BRAF --disease melanoma --counts-only`
- `Command: biomcp get variant "BRAF V600E" clinvar`
- `Command: biomcp search trial -c melanoma --mutation "BRAF V600E" --limit 5`
- step 3 output with query echo `condition=melanoma, mutation=BRAF V600E`
````

Important: keep the expected output section structural. Do not pin exact trial
titles, counts, or server versions that may drift.

## Acceptance Criteria

- [ ] `demo/streamable_http_client.py` remains a standalone PEP 723 script with
  `requires-python = ">=3.11"` and no new non-stdlib dependency beyond `mcp`
- [ ] `parse_args(argv=None)` exists and supports:
  - default scenario `braf-melanoma`
  - optional positional base URL
  - `--scenario` selection with clear argparse rejection for unknown values
- [ ] The demo performs a `GET /health` preflight before opening the MCP
  session and fails with a human-readable start-the-server message
- [ ] The default three-step scenario is:
  - `biomcp search all --gene BRAF --disease melanoma --counts-only`
  - `biomcp get variant "BRAF V600E" clinvar`
  - `biomcp search trial -c melanoma --mutation "BRAF V600E" --limit 5`
- [ ] The demo prints enough framing for screenshots/recordings:
  - health line
  - scenario line
  - tool list containing `biomcp`
  - section title per step
  - `Command: ...` line per step
- [ ] `demo/README.md` exists and documents setup, scenario selection, expected
  output structure, `uv run --quiet`, and version-alignment guidance
- [ ] Demo-facing docs stay aligned with the polished workflow in:
  `docs/getting-started/remote-http.md` and `analysis/technical/overview.md`
- [ ] Focused tests and contracts pass without leaving stale references to
  `SCENARIO = "braf-melanoma"` or the old `variant trials ... --limit 5`
  demo step

## Dev Verification Plan

```bash
# 1. Focused demo tests
uv run pytest tests/test_streamable_http_demo.py -v

# 2. Focused docs-contract regression for the demo surfaces
uv run pytest tests/test_docs_changelog_refresh.py -v

# 3. Start the release binary explicitly to avoid PATH/version confusion
./target/release/biomcp serve-http --host 127.0.0.1 --port 8080

# 4. Run the default scenario
uv run --script demo/streamable_http_client.py

# 5. Run with explicit scenario selection
uv run --script demo/streamable_http_client.py --scenario braf-melanoma

# 6. Confirm unknown scenario failure is clear
uv run --script demo/streamable_http_client.py --scenario missing 2>&1 || true

# 7. Optional: confirm quieter first-run recording path
uv run --quiet --script demo/streamable_http_client.py --scenario braf-melanoma

# 8. Full contracts gate
make test-contracts
```

Manual smoke expectations:

- health check prints before MCP initialization
- server info prints a `biomcp` implementation/version
- tool listing includes `biomcp`
- step 3 query echo includes `condition=melanoma, mutation=BRAF V600E`
- no step requires source editing to change scenario

## Proof Matrix

| Proof type | Coverage |
|------------|----------|
| Focused test proof | `tests/test_streamable_http_demo.py` covers arg parsing, health-check failure UX, step-3 command contract, and Python-floor compatibility |
| Docs-contract proof | `tests/test_docs_changelog_refresh.py` covers remote-http and overview alignment with the polished demo |
| Runtime proof | manual smoke against a real `./target/release/biomcp serve-http --host 127.0.0.1 --port 8080` instance |
| Shared transport proof | existing `tests/test_mcp_http_transport.py` and `tests/test_mcp_http_surface.py` remain the transport/route proof surfaces |
| Full regression proof | `make test-contracts` |

## Out of Scope

- Adding a new `--disease` flag to `variant trials`
- CLI-vs-MCP side-by-side comparison mode
- A second short-form demo script
- `--json` / artifact capture mode
- Changes to numbered `spec/` files
