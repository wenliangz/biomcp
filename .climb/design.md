# Design: P045 — Rename MCP Tool from `shell` to `biomcp`

## Problem

The MCP server currently advertises a single tool named `shell`. That name is
generic in Claude Desktop and other MCP clients, and it hides that the tool is
specifically the BioMCP execution surface.

The current repo confirms the old name in all of these places:

- `src/mcp/shell.rs`: `#[tool] async fn shell(...)`
- `src/mcp/shell.rs`: server instructions say `Use the \`shell\` tool`
- `tests/test_mcp_contract.py`: stdio contract asserts `shell`
- `tests/test_mcp_http_transport.py`: Streamable HTTP contract asserts `shell`
- `demo/streamable_http_client.py`: tool calls target `"shell"`
- public docs still describe the MCP tool as `shell`
- `src/cli/benchmark/score.rs`: benchmark session scoring recognizes `bash` and
  `shell`, but not `biomcp`

## Compatibility Decision

**Decision: clean break for the MCP runtime surface.**

Implementation guidance:

- Rename the advertised MCP tool from `shell` to `biomcp`.
- Do **not** keep a runtime alias that still exposes `shell` through MCP.
- Do keep non-runtime compatibility where it helps internal tooling. In
  particular, benchmark session scoring should recognize both historical
  `shell` logs and new `biomcp` logs.

Rationale:

- The repo is still on `0.8.x`, so a small MCP surface break is acceptable.
- The change is user-facing but mechanically simple: clients learn the new tool
  name from `tools/list`.
- A temporary MCP alias would add avoidable branching to the server surface.

## Verified Constraints

### 1. Rename the Rust tool function

In this codebase, the `#[tool]` macro currently derives the MCP tool name from
the Rust function name. Renaming `async fn shell` to `async fn biomcp` in
`src/mcp/shell.rs` is the direct way to rename the MCP tool.

### 2. Keep `src/mcp/shell.rs` as the module file

The file path should remain `src/mcp/shell.rs`.

Reasons:

- `src/mcp/mod.rs` already imports `mod shell;` and delegates to
  `shell::run_stdio()` / `shell::run_http()`.
- `docs/reference/mcp-server.md` reads `src/mcp/shell.rs` directly inside its
  executable Python snippets.
- The filename is internal. The user-facing contract is the advertised tool
  name, not the module filename.

### 3. `build.rs` does not need a functional change

`build.rs` currently writes the generated description file
`mcp_shell_description.txt` via `write_shell_description()`.

That artifact name is internal and is only referenced by
`src/mcp/shell.rs`'s `#[doc = include_str!(...)]` attribute. It does not expose
the MCP tool name to clients, so no functional rename is required there.

### 4. The demo requirement is broader than a one-line rename

The current `demo/streamable_http_client.py` does **not** list tools today. It
initializes the session and immediately calls the tool.

The ticket requires the demo to print a tool list containing `biomcp`, so the
design must include:

- calling `session.list_tools()`
- printing the returned tool names
- then invoking `session.call_tool("biomcp", ...)`

Updating only the `call_tool()` target is not sufficient.

### 5. The repo is spec-driven, so this rename should be captured in `spec/`

`spec/15-mcp-runtime.md` currently covers `serve-http --help` and the legacy
`serve-sse` help contract, but it does not capture the advertised MCP tool
name.

Because this ticket changes a public runtime contract, add a short executable
spec section that verifies a stdio MCP handshake returns `biomcp` in
`tools/list` and does not advertise `shell`.

### 6. The current design's version-bump instruction was not implementable

The repo currently pins `0.8.15` in:

- `Cargo.toml`
- `pyproject.toml`
- `analysis/technical/overview.md`
- `tests/test_docs_changelog_refresh.py`

Do **not** invent a new release header for this ticket. That would force a
separate release-version sweep unrelated to the MCP rename.

Instead, add the migration note to the existing top `CHANGELOG.md` section so
the rename is documented without expanding scope into a release cut.

## File Disposition

| File | Action | Notes |
|------|--------|-------|
| `src/mcp/shell.rs` | Modify | Rename `async fn shell` to `async fn biomcp`; update server instructions and read-only error copy |
| `tests/test_mcp_contract.py` | Modify | Assert `biomcp` is listed and look up the tool by `tool.name == "biomcp"` |
| `tests/test_mcp_http_transport.py` | Modify | Assert `biomcp` is listed and call `session.call_tool("biomcp", ...)` |
| `demo/streamable_http_client.py` | Modify | Print `tools/list` output and switch tool calls to `"biomcp"` |
| `tests/test_docs_changelog_refresh.py` | Modify | Update demo-script contract from `"shell"` to `"biomcp"` and assert the top changelog block mentions the MCP rename |
| `src/cli/benchmark/score.rs` | Modify | Recognize `biomcp`/`*.biomcp` as BioMCP tool names while preserving legacy `shell` recognition for old logs |
| `spec/15-mcp-runtime.md` | Modify | Add executable outside-in spec for MCP tool identity over stdio |
| `docs/reference/mcp-server.md` | Modify | Update prose to say the execution tool is `biomcp`; leave local Python variable names like `shell = ...` alone |
| `docs/concepts/what-is-biomcp.md` | Modify | Update the MCP-mode tool name |
| `docs/blog/we-deleted-35-tools.md` | Modify | Update the historical description of the current MCP tool name |
| `docs/getting-started/claude-desktop.md` | Modify | Update the verification bullet from `shell` to `biomcp` |
| `docs/getting-started/remote-http.md` | Modify | Update the runnable-demo description from remote MCP `shell` tool to `biomcp` tool |
| `CHANGELOG.md` | Modify | Add a breaking-change note to the existing top release block; do not create a new version header here |
| `src/mcp/mod.rs` | No change | Module wiring stays `shell::run_stdio()` / `shell::run_http()` because the file remains `shell.rs` |
| `build.rs` | No change | Internal description-file naming can remain `mcp_shell_description.txt` |

## Implementation Notes

### `src/mcp/shell.rs`

Required changes:

- rename `async fn shell` to `async fn biomcp`
- change the instruction string from `Use the \`shell\` tool` to
  `Use the \`biomcp\` tool`
- update the read-only rejection text so it no longer says `MCP shell`

Representative sketch:

```rust
#[tool]
async fn biomcp(
    &self,
    Parameters(ShellCommand { command }): Parameters<ShellCommand>,
) -> Result<String, String> {
    ...
    if !is_allowed_mcp_command(&args) {
        return Err(
            "Error: BioMCP allows read-only commands only (search/get/helpers/study/list/version/health/batch/enrich/skill)."
                .to_string(),
        );
    }
    ...
}

.with_instructions(
    "BioMCP provides biomedical data from 15 sources (PubMed, ClinicalTrials.gov, \
     ClinVar, gnomAD, OncoKB, Reactome, UniProt, PharmGKB, OpenFDA, and more). \
     Use the `biomcp` tool to run BioMCP CLI commands. \
     Start with `biomcp list` for a command reference, \
     or `biomcp skill` for guided investigation workflows."
        .to_string(),
)
```

### `demo/streamable_http_client.py`

The demo should prove the tool rename explicitly before running the scenario.

Representative sketch:

```python
tools_result = await session.list_tools()
tool_names = [tool.name for tool in tools_result.tools]
print(f"Available tools: {', '.join(tool_names)}")

for title, command in selected_steps():
    print(f"\n=== {title} ===")
    call_result = await session.call_tool(
        "biomcp",
        arguments={"command": command},
    )
```

### `src/cli/benchmark/score.rs`

This file is not part of the MCP server itself, but it consumes recorded agent
tool-call logs. After the rename, it must continue to count BioMCP calls when
the logged tool name is `biomcp`.

Keep backward compatibility here:

- accept `biomcp`
- accept names ending in `.biomcp`
- continue accepting `shell` and names ending in `.shell`
- continue accepting `bash` and names ending in `.bash`

Also update the existing unit fixture to include the new name, or add a second
fixture case so both legacy and current log names are covered.

### `spec/15-mcp-runtime.md`

Add one new prose section plus a short executable block that validates the
advertised MCP tool name. Keep it human-readable per the `spec-writing` skill.

Representative sketch:

```bash
out="$(printf '%s\n%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"spec","version":"0.1"}}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  | biomcp serve 2>/dev/null)"
echo "$out" | mustmatch like '"name":"biomcp"'
echo "$out" | mustmatch not like '"name":"shell"'
```

## Acceptance Criteria

- [ ] `cargo build --release` succeeds
- [ ] `cargo clippy -- -D warnings` passes
- [ ] `cargo test` passes, including any updated benchmark scorer unit coverage
- [ ] `uv run pytest tests/test_mcp_contract.py -v` passes with `biomcp` as the advertised stdio tool name
- [ ] `uv run pytest tests/test_mcp_http_transport.py -v` passes with `biomcp` as the advertised Streamable HTTP tool name
- [ ] `uv run pytest tests/test_docs_changelog_refresh.py -v` passes with the updated demo/changelog contract
- [ ] the updated `spec/15-mcp-runtime.md` passes via the repo spec runner
- [ ] `uv run --script demo/streamable_http_client.py http://127.0.0.1:8080` works against a running `biomcp serve-http` instance, prints a tool list containing `biomcp`, and completes the BRAF scenario without error
- [ ] `uv run mkdocs build --strict` passes after the doc text updates
- [ ] `rg '"shell"' tests/test_mcp_contract.py tests/test_mcp_http_transport.py tests/test_docs_changelog_refresh.py demo/streamable_http_client.py` returns no matches

## Dev Verification Plan

```bash
# 1. Build the release binary
cargo build --release

# 2. Confirm stdio advertises biomcp, not shell
printf '%s\n%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"verify","version":"0.1"}}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  | ./target/release/biomcp serve 2>/dev/null | rg '"name"'

# 3. Run focused MCP contract tests
uv run pytest tests/test_mcp_contract.py -v
uv run pytest tests/test_mcp_http_transport.py -v

# 4. Run the docs/changelog contract touched by the demo + release-note updates
uv run pytest tests/test_docs_changelog_refresh.py -v

# 5. Run Rust unit/integration coverage, including benchmark-score parsing
cargo test

# 6. Run the MCP runtime spec
XDG_CACHE_HOME="$(pwd)/.cache" PATH="$(pwd)/target/release:$PATH" \
  uv run --extra dev sh -c 'PATH="$(pwd)/target/release:$PATH" pytest spec/15-mcp-runtime.md --mustmatch-lang bash --mustmatch-timeout 60 -v'

# 7. Confirm the demo lists the renamed tool and completes its scenario
./target/release/biomcp serve-http --host 127.0.0.1 --port 8080
uv run --script demo/streamable_http_client.py http://127.0.0.1:8080

# 8. Build docs
uv run mkdocs build --strict

# 9. Sanity-check the targeted files for stale shell references
rg '"shell"' tests/test_mcp_contract.py tests/test_mcp_http_transport.py \
  tests/test_docs_changelog_refresh.py demo/streamable_http_client.py
```

## Developer Handoff

Implement the runtime rename as a clean break at the MCP layer, but keep the
internal benchmark scorer backward-compatible with historical `shell` logs.

The inherited design missed three concrete impacts that must be included in
code:

1. the demo script has to call `list_tools()` and print `biomcp`, not just
   swap the `call_tool()` string
2. the repo's docs/changelog contract test hard-codes `"shell"` in the demo
   artifact check and should be updated alongside the demo/changelog text
3. the repo is spec-driven, so `spec/15-mcp-runtime.md` should gain a short
   executable assertion for the renamed MCP tool

Do not bump package versions for this ticket. Add the migration note inside the
current top changelog section instead.
