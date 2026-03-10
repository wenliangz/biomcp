# Design: P038 — HTTP Transport Parity and Health

## Verified Context

The current Rust server surface is still legacy SSE:

- `src/mcp/shell.rs` uses `rmcp::transport::sse_server::SseServer`
  and logs `/sse` plus `/message`.
- `src/mcp/mod.rs` documents `serve-http` as the SSE transport.
- `src/cli/mod.rs` exposes `ServeHttp` only, with help text that still says
  "HTTP (SSE transport)".
- `src/main.rs` dispatches `ServeHttp` directly, so any new transport command
  must be wired there too.
- `build.rs` generates the MCP `shell` tool description from
  `src/cli/list_reference.md`, so transport wording in that markdown affects
  both `biomcp list` output and the MCP tool description shipped to clients.
- Existing docs-contract tests already assert the current HTTP/SSE wording in
  `RUN.md`, `analysis/technical/staging-demo.md`,
  `analysis/technical/overview.md`, `analysis/ux/cli-reference.md`, and
  `docs/user-guide/cli-reference.md`.

The work is therefore larger than a transport swap in `shell.rs`: the real
blast radius includes CLI help, `main.rs`, generated MCP tool description,
runtime docs, staging contract docs, tests, and one repo-external notes file.

## Architecture Decisions

### AD-1: Upgrade to `rmcp 1.1.1` and add direct `axum`

Use:

```toml
rmcp = { version = "1.1.1", features = ["server", "transport-io", "transport-streamable-http-server"] }
axum = { version = "0.8.1", default-features = false, features = ["tokio", "http1", "json"] }
```

Why:

- `rmcp 1.1.1` provides `StreamableHttpService`.
- `rmcp 1.1.1` no longer ships server-side SSE transport support, so the old
  `transport-sse-server` path cannot remain the primary implementation.
- `axum` is required because the new RMCP HTTP service is mounted into a router
  and served with `axum::serve`.

Relevant API corrections for `src/mcp/shell.rs`:

- Replace `PaginatedRequestParam` with `Option<PaginatedRequestParams>` in
  `list_resources`.
- Replace `ReadResourceRequestParam` with `ReadResourceRequestParams`.
- Replace `Error as McpError` with `ErrorData as McpError`.
- Convert `BioMcpServer` from a unit struct to a struct holding
  `tool_router: ToolRouter<Self>`.
- Use `#[tool_router]` on the tool impl.
- Use `#[tool_handler(router = self.tool_router)]` on the `impl ServerHandler`
  block so tool routing is generated from that stored router.

### AD-2: `serve-http` becomes the canonical Streamable HTTP server

`serve-http` keeps its name but changes meaning:

- `POST /mcp` handles client JSON-RPC requests.
- `GET /mcp` exposes the SSE subscription stream managed by RMCP.
- `GET /health` returns a lightweight liveness response.
- `GET /readyz` is an alias of `/health`.
- `GET /` returns a small identity/status document instead of `404`.

Implementation shape:

```rust
let ct = CancellationToken::new();

let service = StreamableHttpService::new(
    || Ok(BioMcpServer::new()),
    Default::default(),
    StreamableHttpServerConfig {
        stateful_mode: true,
        cancellation_token: ct.child_token(),
        ..Default::default()
    },
);

let router = axum::Router::new()
    .nest_service("/mcp", service)
    .route("/health", get(health_handler))
    .route("/readyz", get(health_handler))
    .route("/", get(index_handler));
```

`stateful_mode` is not an open question anymore. It should be left `true` so
`GET /mcp` exists and RMCP manages reconnectable sessions. Setting it to
`false` would change the contract to POST-only and conflict with the desired
route layout.

### AD-3: `serve-sse` is an explicit compatibility/deprecation command

Add a visible `serve-sse` subcommand. It should:

- appear in `--help`,
- be clearly labeled as removed/deprecated,
- print a migration message that points users to `biomcp serve-http`,
- exit non-zero without starting a server.

Why visible instead of hidden:

- the ticket requires an honest transport story,
- the help surface is part of the migration contract,
- a visible command gives existing SSE users a concrete next step rather than
  a "command not found" failure.

This also requires:

- adding `run_sse` to `src/mcp/mod.rs`,
- excluding `ServeSse` from `cli::run()`,
- adding a `ServeSse` match arm in `src/main.rs`.

### AD-4: Health and root responses stay minimal

`GET /health` and `GET /readyz` should both return:

```json
{"status":"ok"}
```

No upstream dependency probes belong here. The repo already has a separate
`biomcp health` command for external API checks; the HTTP routes are lightweight
process probes.

`GET /` should return:

```json
{
  "name": "biomcp",
  "version": "<CARGO_PKG_VERSION>",
  "transport": "streamable-http",
  "mcp": "/mcp"
}
```

### AD-5: Remove stale `skill list` guidance from server-emitted instructions

The server-emitted `get_info().instructions` string in `src/mcp/shell.rs`
currently tells clients to use `biomcp skill list`. That text is stale and must
be replaced with guidance that points to `biomcp skill`.

This design does **not** require removing every legacy-compatibility mention
from user docs such as `docs/getting-started/skills.md`. Those pages currently
document the alias intentionally. The required cleanup is the server-emitted
guidance and any shipped CLI/help text that would otherwise present the removed
UX as current.

### AD-6: Transport wording must be updated in the generated help pipeline

`build.rs` reads `src/cli/list_reference.md` and writes the generated MCP tool
description. That means:

- updating `src/cli/list_reference.md` is required,
- otherwise the MCP `shell` tool description will continue to imply SSE even if
  `run_http` is fixed.

### AD-7: Split operator docs in `spec/` from transport behavior in `tests/`

`spec/` is executable documentation, not the exhaustive integration layer.
For this ticket:

- add a small spec file that documents the operator-facing help contract for
  `serve-http` and `serve-sse`,
- keep the actual HTTP transport/session behavior in `tests/`.

Do not try to force the long-running HTTP server itself into a `mustmatch`
shell spec. That would be brittle and out of character for this repo's spec
suite.

## File Disposition

| File | Action | Notes |
|------|--------|-------|
| `Cargo.toml` | Modify | Upgrade `rmcp`, drop `transport-sse-server`, add `axum` |
| `src/mcp/shell.rs` | Modify | RMCP 1.1 migration, `run_http`, `run_sse`, health/root handlers, instruction string |
| `src/mcp/mod.rs` | Modify | Export/doc both `run_http` and `run_sse`; update transport doc comments |
| `src/cli/mod.rs` | Modify | `ServeHttp` help rewrite, add visible `ServeSse`, adjust `cli::run()` exclusion arm |
| `src/main.rs` | Modify | Dispatch `ServeSse` explicitly |
| `src/cli/list_reference.md` | Modify | Replace SSE wording in deployment guidance; this also updates generated MCP tool description |
| `README.md` | Modify | Multi-worker deployment guidance must describe Streamable HTTP and `/mcp` |
| `RUN.md` | Modify | Replace HTTP/SSE runbook section with Streamable HTTP, `/health`, `/readyz`, `/` |
| `docs/reference/mcp-server.md` | Modify | Keep resource-contract coverage; add current HTTP transport surface and route contract |
| `docs/user-guide/cli-reference.md` | Modify | Replace "HTTP/SSE" wording and mention `serve-sse` deprecation path |
| `analysis/technical/overview.md` | Modify | Replace "HTTP relay" phrasing with canonical Streamable HTTP deployment guidance |
| `analysis/technical/staging-demo.md` | Modify | Update runtime modes, owned endpoints, and proof contract |
| `analysis/ux/cli-reference.md` | Modify | Replace SSE phrasing and add the `serve-sse` migration note |
| `tests/test_mcp_contract.py` | Modify | Assert initialize instructions do not contain `skill list` |
| `tests/test_public_skill_docs_contract.py` | Modify | Assert `docs/reference/mcp-server.md` documents Streamable HTTP routes without regressing resource-contract assertions |
| `tests/test_upstream_planning_analysis_docs.py` | Modify | Update HTTP runtime/doc assertions to `/mcp`, `/health`, `/readyz`, `/` |
| `tests/test_mcp_http_surface.py` | Create | HTTP route + CLI help/deprecation contract tests |
| `tests/test_mcp_http_transport.py` | Create | End-to-end Streamable HTTP initialize/list_tools/call_tool test |
| `spec/15-mcp-runtime.md` | Create | Executable doc for `serve-http --help` and `serve-sse --help` |
| `/home/ian/workspace/notes/BioMCP Streamable HTTP launch note.md` | Modify | Repo-external notes artifact; append release/post copy after code/docs are updated |

## Implementation Notes

### `src/mcp/shell.rs`

Keep the existing read-only `shell` allowlist logic. The transport work should
not change command authorization.

Use this structural pattern:

```rust
#[derive(Debug, Clone)]
pub struct BioMcpServer {
    tool_router: ToolRouter<Self>,
}

impl BioMcpServer {
    pub fn new() -> Self {
        Self {
            tool_router: Self::tool_router(),
        }
    }
}

#[tool_router]
impl BioMcpServer {
    #[tool(description = shell_description())]
    async fn shell(&self, #[tool(param)] command: String) -> Result<String, String> {
        // existing body
    }
}

#[tool_handler(router = self.tool_router)]
impl ServerHandler for BioMcpServer {
    // get_info/list_resources/read_resource
}
```

Do not keep the unit-struct form from RMCP 0.1.x.

### `serve-http` logging

Log the new public contract explicitly:

- `POST/GET http://<bind>/mcp`
- `GET http://<bind>/health`
- `GET http://<bind>/readyz`
- `GET http://<bind>/`

### `serve-http --help`

The subcommand help text should make the primary transport honest. It should
mention Streamable HTTP, not SSE, and ideally name `/mcp`.

### `serve-sse --help`

The subcommand help text should identify the command as removed/deprecated and
direct users to `serve-http`.

### `docs/reference/mcp-server.md`

This page already serves as executable documentation for the MCP resource
contract. Keep those assertions. Add a separate transport section describing:

- stdio server entrypoint: `biomcp serve`
- remote HTTP entrypoint: `biomcp serve-http`
- Streamable HTTP endpoint: `/mcp`
- health/status routes: `/health`, `/readyz`, `/`

### `spec/15-mcp-runtime.md`

This file should stay small and operator-oriented. Example shape:

````markdown
# MCP Runtime Help

BioMCP exposes a stdio MCP server for local agent use and a Streamable HTTP
server for remote/shared deployments. This file documents the help contract
users see when choosing between those runtime modes.

## Streamable HTTP Help

`serve-http --help` should describe the current transport honestly and point
operators at the canonical HTTP path.

```bash
out="$(biomcp serve-http --help)"
echo "$out" | mustmatch like "Streamable HTTP"
echo "$out" | mustmatch like "/mcp"
```

## Legacy SSE Help

`serve-sse --help` exists only as a migration aid and should point back to
`serve-http`.

```bash
out="$(biomcp serve-sse --help)"
echo "$out" | mustmatch like "removed"
echo "$out" | mustmatch like "serve-http"
```
````

## Acceptance Criteria

### AC-1: Streamable HTTP transport works end-to-end

A remote MCP client can connect to `http://127.0.0.1:<port>/mcp` using the
Python `mcp` package's Streamable HTTP client, complete `initialize`,
successfully `list_tools`, and successfully `call_tool("shell", ...)`.

Verified by: `tests/test_mcp_http_transport.py`

### AC-2: HTTP route surface is explicit and healthy

| Route | Status | Content-Type | Required body |
|------|--------|--------------|---------------|
| `GET /` | `200` | `application/json` | keys `name`, `version`, `transport`, `mcp` |
| `GET /health` | `200` | `application/json` | `{"status":"ok"}` |
| `GET /readyz` | `200` | `application/json` | `{"status":"ok"}` |

Verified by: `tests/test_mcp_http_surface.py`

### AC-3: Legacy SSE users get an explicit migration path

- `biomcp serve-sse --help` is visible and names the command as removed or
  deprecated.
- `biomcp serve-sse` exits non-zero and prints a message pointing to
  `biomcp serve-http`.

Verified by: `tests/test_mcp_http_surface.py` and `spec/15-mcp-runtime.md`

### AC-4: Server-emitted guidance no longer references `skill list`

The initialize instructions exposed by the running MCP server do not contain
`skill list` and instead point users to `biomcp skill`.

Verified by: `tests/test_mcp_contract.py`

### AC-5: Shipped help/docs no longer present SSE as the primary HTTP transport

The operator-facing docs and help text describe:

- `serve-http` as Streamable HTTP,
- `/mcp` as the canonical endpoint,
- `/health`, `/readyz`, and `/` as the HTTP probe surface,
- `serve-sse` as compatibility/deprecation only.

Verified by:

- `tests/test_mcp_http_surface.py`
- `tests/test_public_skill_docs_contract.py`
- `tests/test_upstream_planning_analysis_docs.py`
- `spec/15-mcp-runtime.md`

### AC-6: Release note artifact is updated

`/home/ian/workspace/notes/BioMCP Streamable HTTP launch note.md` contains
plain-language change notes plus short release-post copy that names:

- Streamable HTTP,
- `/mcp`,
- `/health` and `/readyz`,
- the `serve-http` / `serve-sse` migration story.

Verified by: manual file inspection in verify

## Test Plan

### `tests/test_mcp_http_surface.py`

Use a subprocess fixture that:

- allocates a free local port,
- starts `./target/release/biomcp serve-http --host 127.0.0.1 --port <port>`,
- polls `GET /health` until ready instead of using a fixed sleep,
- terminates the child cleanly in teardown.

Cover:

- `GET /`
- `GET /health`
- `GET /readyz`
- `biomcp serve-http --help`
- `biomcp serve-sse --help`
- `biomcp serve-sse` non-zero deprecation exit

### `tests/test_mcp_http_transport.py`

Use the canonical client helper:

```python
from mcp.client.streamable_http import streamable_http_client
```

Not the deprecated alias.

Cover:

- initialize,
- list tools,
- one successful `shell` tool call such as `biomcp version`.

### `tests/test_mcp_contract.py`

Extend the existing stdio MCP contract test to assert that the initialize
instructions string does not contain `skill list` and does contain
`biomcp skill`.

## Dev Verification Plan

1. `cargo build --release --locked`
2. `./target/release/biomcp serve-http --host 127.0.0.1 --port 8099`
3. `curl http://127.0.0.1:8099/health`
4. `curl http://127.0.0.1:8099/readyz`
5. `curl http://127.0.0.1:8099/`
6. Run one initialize request against `http://127.0.0.1:8099/mcp`
7. `./target/release/biomcp serve-sse`
8. `cargo test`
9. `uv run pytest tests/test_mcp_contract.py tests/test_mcp_http_surface.py tests/test_mcp_http_transport.py tests/test_public_skill_docs_contract.py tests/test_upstream_planning_analysis_docs.py -v`
10. `make spec`

## Shared Staging/Demo Contract Updates

`analysis/technical/staging-demo.md` must explicitly say:

- canonical remote runtime: `./target/release/biomcp serve-http --host 127.0.0.1 --port 8080`
- owned remote routes: `POST/GET /mcp`, `GET /health`, `GET /readyz`, `GET /`
- proof artifact: successful `/health` probe plus one successful MCP initialize
  against `/mcp`
- legacy SSE runtime is removed from the primary contract and retained only as a
  deprecated compatibility command

## Notes Vault Artifact

The notes file already exists at:

`/home/ian/workspace/notes/BioMCP Streamable HTTP launch note.md`

Append final release-post copy after the implementation is done. The artifact is
outside the repo, so the developer must update it deliberately rather than
assuming a repo-relative `notes/` path exists.
