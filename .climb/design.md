# Design: P038 — HTTP Transport Parity and Health

## Context

The Rust BioMCP server currently exposes only the legacy SSE transport
(`GET /sse`, `POST /message`), backed by `rmcp 0.1.5`. The Python `v0.7.3`
release had Streamable HTTP, a `/mcp` endpoint, and `/health`. This ticket
restores parity and makes `serve-http` mean what users expect.

---

## Architecture Decisions

### AD-1: Upgrade rmcp 0.1.5 → 1.1.1

**Decision:** Upgrade.

**Rationale:** rmcp 1.x ships `StreamableHttpService` (axum Tower service)
which implements the MCP Streamable HTTP transport
(`POST /mcp` + `GET /mcp` SSE subscription) per the finalized spec.
rmcp 1.x dropped `transport-sse-server` — the old SSE transport is gone
from the SDK, so retaining it would require re-implementing it by hand.
The API surface in rmcp 1.x is stable and already used by production deployments.

**Breaking changes introduced by rmcp 0.1.5 → 1.1.1 (relevant to shell.rs):**

| Old (0.1.x) | New (1.x) | Notes |
|---|---|---|
| `#[tool(tool_box)]` on impl block | `#[tool_router]` | separate macro |
| `#[tool(tool_box)]` on `impl ServerHandler` | `#[tool_handler]` | separate macro |
| `BioMcpServer` is a unit struct | needs `tool_router: ToolRouter<Self>` field | required by `#[tool_router]` |
| `PaginatedRequestParam` | `Option<PaginatedRequestParams>` in method sigs | old type alias still compiles, but signature differs |
| `ReadResourceRequestParam` | `ReadResourceRequestParams` | pluralized, old alias still compiles |
| `Error as McpError` | `Error` is deprecated; prefer `ErrorData as McpError` | old alias compiles with deprecation warning |
| `transport-sse-server` feature | removed; no equivalent | legacy SSE must be explicitly deprecated |
| `rmcp::transport::stdio()` | unchanged | stdio still works |
| `ServiceExt::serve_with_ct` | unchanged | still exported from `service` |
| `AnnotateAble::no_annotation()` | unchanged | still on trait |

### AD-2: Deprecate `serve-sse`, keep the CLI command as a no-op error

**Decision:** Add a `serve-sse` CLI command that prints a clear deprecation
message and exits with a non-zero status.

**Rationale:** rmcp 1.x dropped the server-side SSE transport entirely.
Re-implementing SSE session management in bare axum is out-of-scope for this
ticket. The ticket says "clearly deprecated for SSE users" is acceptable. The
command exists so that scripts relying on `serve-sse` get a helpful message
rather than a "command not found" error.

### AD-3: `serve-http` stays named `serve-http` and gains Streamable HTTP

**Decision:** Keep the `serve-http` subcommand name; change its implementation
from SSE to Streamable HTTP. No rename.

**Rationale:** `serve-http` already means "HTTP server" to existing users.
The content changes (new endpoint, new transport), but the command name stays
consistent. The deprecation of legacy SSE is communicated in help text.

### AD-4: Route layout for `serve-http`

```
POST /mcp         ← MCP Streamable HTTP (client→server JSON-RPC)
GET  /mcp         ← MCP SSE subscription stream
GET  /health      ← Lightweight health check (liveness)
GET  /readyz      ← Alias for /health (readiness; same response)
GET  /            ← Identity/status document (JSON)
```

The MCP endpoint is mounted at `/mcp` via
`axum::Router::new().nest_service("/mcp", StreamableHttpService::new(...))`.
`/health`, `/readyz`, and `/` are plain axum routes added to the same router.

### AD-5: `GET /` identity document

Returns a small JSON object:
```json
{
  "name": "biomcp",
  "version": "<CARGO_PKG_VERSION>",
  "transport": "streamable-http",
  "mcp": "/mcp"
}
```

### AD-6: `GET /health` and `GET /readyz` responses

Both return HTTP 200 with:
```json
{"status": "ok"}
```

`Content-Type: application/json`. No upstream API checks are performed (liveness
only). Readiness alias exists for container platform compatibility.

### AD-7: MCP server instructions — remove `skill list` reference

`get_info()` currently advises:
> Start with `biomcp list` for a command reference, or `biomcp skill list` for
> guided investigation workflows.

Replace with:
> Use the `shell` tool to run BioMCP CLI commands. Start with `biomcp list` for
> a command reference, or `biomcp skill` to access guided investigation workflows.

`biomcp skill list` is not a valid command; `biomcp skill` or `biomcp skill show`
are the correct spellings. This change is isolated to the `instructions` string
in `get_info()`.

### AD-8: axum as a direct dependency

rmcp 1.x's `StreamableHttpService` is a Tower service that integrates with axum.
The `counter_streamhttp.rs` example shows that callers must bring their own axum
router and call `axum::serve`. Add axum 0.8 as a direct dependency so the
`run_http` function can build the router and call `axum::serve`.

---

## File Disposition

| File | Action | Notes |
|------|--------|-------|
| `Cargo.toml` | Modify | Upgrade rmcp to `1.1`, swap features, add axum |
| `src/mcp/shell.rs` | Modify | rmcp 1.x API migration + new `run_http` + `run_sse` |
| `src/mcp/mod.rs` | Modify | Update `run_http` docstring, add `run_sse` |
| `src/cli/mod.rs` | Modify | Add `ServeSse` command, update match arm, update help text |
| `src/cli/list_reference.md` | Modify | Update multi-worker guidance copy |
| `RUN.md` | Modify | Update HTTP/SSE section with Streamable HTTP |
| `analysis/technical/staging-demo.md` | Modify | Update runtime modes, endpoints, proof contract |
| `docs/reference/mcp-server.md` | Modify | Update transport section |
| `README.md` | Modify | Update multi-worker guidance |
| `tests/test_mcp_http_surface.py` | Create | New HTTP surface integration tests |
| `tests/test_mcp_http_transport.py` | Create | Streamable HTTP protocol test |
| `notes/BioMCP Streamable HTTP launch note.md` | Modify | Finalize the launch note |

---

## Code Sketches

### Cargo.toml changes

```toml
# Remove transport-sse-server; upgrade rmcp; add axum
rmcp = { version = "1.1", features = ["server", "transport-io", "transport-streamable-http-server"] }
axum = { version = "0.8", default-features = false, features = ["tokio", "http1", "json"] }
```

Note: rmcp 1.x uses `pastey` instead of `paste`; the macro re-export is
`pastey::paste`. This is internal to rmcp — no change required in biomcp code.

### src/mcp/shell.rs — struct and tool macro migration

```rust
use rmcp::handler::server::router::tool::ToolRouter;
use rmcp::model::{
    AnnotateAble, ErrorData as McpError, Implementation, ListResourcesResult,
    PaginatedRequestParams, RawResource, ReadResourceRequestParams,
    ReadResourceResult, ResourceContents, ServerCapabilities, ServerInfo,
};
use rmcp::service::{RequestContext, RoleServer};
use rmcp::{ServerHandler, ServiceExt, tool, tool_handler, tool_router};

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
        // ... same body as before ...
    }
}

#[tool_handler]
impl ServerHandler for BioMcpServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            // ...
            instructions: Some(
                "BioMCP provides biomedical data from 15 sources. \
                 Use the `shell` tool to run BioMCP CLI commands. \
                 Start with `biomcp list` for a command reference, \
                 or `biomcp skill` to access guided investigation workflows."
                    .to_string(),
            ),
            ..Default::default()
        }
    }

    fn list_resources(
        &self,
        _request: Option<PaginatedRequestParams>,
        _context: RequestContext<RoleServer>,
    ) -> impl Future<Output = Result<ListResourcesResult, McpError>> + Send + '_ {
        // ... same body ...
    }

    fn read_resource(
        &self,
        request: ReadResourceRequestParams,
        _context: RequestContext<RoleServer>,
    ) -> impl Future<Output = Result<ReadResourceResult, McpError>> + Send + '_ {
        // ... same body ...
    }
}
```

### src/mcp/shell.rs — new run_http

```rust
pub async fn run_http(host: &str, port: u16) -> anyhow::Result<()> {
    use axum::routing::get;
    use rmcp::transport::streamable_http_server::{
        StreamableHttpServerConfig, StreamableHttpService,
        session::local::LocalSessionManager,
    };

    let ip: std::net::IpAddr = host
        .parse()
        .map_err(|e| anyhow::anyhow!("Invalid host address: {e}"))?;
    let bind = std::net::SocketAddr::new(ip, port);

    let ct = tokio_util::sync::CancellationToken::new();

    let service = StreamableHttpService::new(
        || Ok(BioMcpServer::new()),
        LocalSessionManager::default().into(),
        StreamableHttpServerConfig {
            cancellation_token: ct.child_token(),
            ..Default::default()
        },
    );

    let router = axum::Router::new()
        .nest_service("/mcp", service)
        .route("/health", get(health_handler))
        .route("/readyz", get(health_handler))
        .route("/", get(index_handler));

    tracing::info!("BioMCP HTTP server listening on http://{bind}");
    tracing::info!("  MCP endpoint:  POST/GET  http://{bind}/mcp");
    tracing::info!("  Health check:  GET       http://{bind}/health");
    tracing::info!("  Status:        GET       http://{bind}/");

    let listener = tokio::net::TcpListener::bind(bind)
        .await
        .map_err(|e| anyhow::anyhow!("Failed to bind HTTP server: {e}"))?;

    axum::serve(listener, router)
        .with_graceful_shutdown(async move {
            tokio::signal::ctrl_c().await.ok();
            tracing::info!("Shutting down…");
            ct.cancel();
        })
        .await
        .map_err(Into::into)
}

async fn health_handler() -> axum::Json<serde_json::Value> {
    axum::Json(serde_json::json!({"status": "ok"}))
}

async fn index_handler() -> axum::Json<serde_json::Value> {
    axum::Json(serde_json::json!({
        "name": "biomcp",
        "version": env!("CARGO_PKG_VERSION"),
        "transport": "streamable-http",
        "mcp": "/mcp",
    }))
}
```

### src/mcp/shell.rs — new run_sse (deprecated stub)

```rust
pub async fn run_sse(_host: &str, _port: u16) -> anyhow::Result<()> {
    anyhow::bail!(
        "SSE transport has been removed. Use `biomcp serve-http` (Streamable HTTP) instead.\n\
         The new HTTP server exposes the MCP endpoint at /mcp and is compatible with \
         current MCP clients."
    )
}
```

### src/cli/mod.rs — ServeSse command

Add alongside `ServeHttp`:

```rust
/// Run MCP server over HTTP (legacy SSE transport — REMOVED)
///
/// This transport has been removed. Use `serve-http` (Streamable HTTP) instead.
#[command(hide = false)]
ServeSse {
    #[arg(long, default_value = "127.0.0.1")]
    host: String,
    #[arg(long, default_value = "8080")]
    port: u16,
},
```

And update the match arm in the main dispatch:

```rust
Commands::Mcp | Commands::Serve | Commands::ServeHttp { .. } | Commands::ServeSse { .. } => {
    anyhow::bail!("MCP/serve commands should not go through CLI run()")
}
```

And in `main.rs`, add handling:

```rust
Commands::ServeSse { host, port } => {
    crate::mcp::run_sse(&host, port).await?;
}
```

### src/cli/list_reference.md — update multi-worker guidance

Change:
```
- In multi-worker environments, run one shared `biomcp serve-http` process so workers use a single BioMCP SSE server and one limiter budget.
```

To:
```
- In multi-worker environments, run one shared `biomcp serve-http` process (Streamable HTTP) so all workers share a single BioMCP server and rate-limiter budget.
```

---

## Acceptance Criteria

### AC-1: Streamable HTTP MCP handshake

A remote MCP client using Streamable HTTP transport can:
- Connect to `http://host:port/mcp`
- Complete `initialize` handshake
- Call `tools/list` and receive the `shell` tool
- Call `tools/call` with a valid `shell` command and get a non-error result

Verified by: `tests/test_mcp_http_transport.py`

### AC-2: HTTP route responses

| Route | Status | Content-Type | Required body/keys |
|-------|--------|-------------|-------------------|
| `GET /` | 200 | `application/json` | `name`, `version`, `mcp` |
| `GET /health` | 200 | `application/json` | `status: "ok"` |
| `GET /readyz` | 200 | `application/json` | `status: "ok"` |

Verified by: `tests/test_mcp_http_surface.py`

### AC-3: SSE transport deprecated

`biomcp serve-sse` exits with a non-zero status and prints a message telling
users to use `serve-http`. No server is started.

Verified by: `tests/test_mcp_http_surface.py` (CLI smoke test)

### AC-4: MCP instructions no longer reference `skill list`

`get_info()` instructions string does not contain `skill list`.

Verified by: `tests/test_mcp_contract.py` (new assertion) or spec file check.

### AC-5: CLI help text is updated

`biomcp serve-http --help` does not reference SSE. `biomcp serve-sse --help`
references the removal and points to `serve-http`.

Verified by: `tests/test_mcp_http_surface.py` (CLI help contract)

### AC-6: Docs updated

- `README.md` multi-worker section references `serve-http` (Streamable HTTP)
- `RUN.md` HTTP section describes the new endpoint layout (`/mcp`, `/health`, `/`)
- `analysis/technical/staging-demo.md` lists the new endpoints under "Owned Artifacts"
- `docs/reference/mcp-server.md` describes the HTTP transport with `/mcp`, `/health`, `/`

Verified by: `tests/test_mcp_http_surface.py` docs-contract checks and
`tests/test_upstream_planning_analysis_docs.py` if staging-demo is covered.

### AC-7: Release note exists

`/home/ian/workspace/notes/BioMCP Streamable HTTP launch note.md` contains
a social/GitHub/Discord post draft that can be used after merge + release.

Verified by: file exists and is non-empty (manual check at verify step).

---

## Dev Verification Plan

1. `cargo build --release --locked` — must compile without warnings
2. Start `./target/release/biomcp serve-http --host 127.0.0.1 --port 8099`
3. Curl `/health` → `{"status":"ok"}`; curl `/` → JSON with `"mcp":"/mcp"`;
   `curl -X POST http://127.0.0.1:8099/mcp -H 'Content-Type: application/json'
   -d '{"jsonrpc":"2.0","method":"initialize","id":1,"params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"0.1"}}}'`
   → 200 JSON-RPC response
4. `./target/release/biomcp serve-sse` → exits non-zero with deprecation message
5. `uv run pytest tests/ -v` — existing contract tests pass; new HTTP surface
   and transport tests pass

---

## Shared Staging/Demo Contract Updates

`analysis/technical/staging-demo.md` must be updated to:
- Add `serve-http` (Streamable HTTP) as the canonical HTTP runtime mode
- List owned HTTP endpoints: `POST/GET /mcp`, `GET /health`, `GET /readyz`, `GET /`
- Add HTTP surface proof step: start server, curl `/health`, attempt MCP POST to `/mcp`
- Move legacy SSE section to "removed" note

---

## Test File Sketches

### tests/test_mcp_http_surface.py

```python
"""HTTP surface contract tests for GET /, /health, /readyz and CLI/help contract."""

import subprocess
import time
import requests
import pytest

@pytest.fixture(scope="module")
def http_server():
    """Start biomcp serve-http on a random port for the test session."""
    import socket
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()

    proc = subprocess.Popen(
        ["./target/release/biomcp", "serve-http", "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    time.sleep(1.0)  # wait for bind
    yield f"http://127.0.0.1:{port}"
    proc.terminate()
    proc.wait()


def test_health_returns_ok(http_server):
    r = requests.get(f"{http_server}/health", timeout=5)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_readyz_returns_ok(http_server):
    r = requests.get(f"{http_server}/readyz", timeout=5)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root_returns_identity(http_server):
    r = requests.get(f"{http_server}/", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "biomcp"
    assert "version" in data
    assert data["mcp"] == "/mcp"


def test_serve_sse_exits_with_deprecation():
    result = subprocess.run(
        ["./target/release/biomcp", "serve-sse", "--help"],
        capture_output=True, text=True,
    )
    output = result.stdout + result.stderr
    assert "removed" in output.lower() or "serve-http" in output.lower()


def test_serve_http_help_mentions_mcp_endpoint():
    result = subprocess.run(
        ["./target/release/biomcp", "serve-http", "--help"],
        capture_output=True, text=True,
    )
    output = result.stdout + result.stderr
    assert "mcp" in output.lower() or "streamable" in output.lower()
```

### tests/test_mcp_http_transport.py

```python
"""Integration test: Streamable HTTP MCP handshake and one tool call."""

import asyncio
import socket
import subprocess
import time
import pytest
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


@pytest.fixture(scope="module")
def http_server_url():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()

    proc = subprocess.Popen(
        ["./target/release/biomcp", "serve-http", "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    time.sleep(1.5)
    yield f"http://127.0.0.1:{port}/mcp"
    proc.terminate()
    proc.wait()


@pytest.mark.asyncio
async def test_streamable_http_initialize_and_list_tools(http_server_url):
    async with streamablehttp_client(http_server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            result = await session.initialize()
            assert result.capabilities.tools is not None
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            assert "shell" in names


@pytest.mark.asyncio
async def test_streamable_http_tool_call(http_server_url):
    async with streamablehttp_client(http_server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("shell", {"command": "biomcp version"})
            assert not result.isError
            assert result.content
```

---

## Notes Vault Artifact

File: `/home/ian/workspace/notes/BioMCP Streamable HTTP launch note.md`

The existing file already has the structure. Developer must append:

```markdown
## Social / GitHub / Discord post draft

---

BioMCP Rust server now supports Streamable HTTP as the primary remote transport.

What's new:
- `biomcp serve-http` is now true MCP Streamable HTTP (not legacy SSE)
- Endpoint at `/mcp` — fully spec-compliant MCP 2025-03-26 HTTP transport
- `GET /health` and `GET /readyz` for ops and container health probes
- `GET /` returns server identity/status JSON
- Legacy SSE mode has been removed; use `serve-http` for all new deployments

If you were using `serve-http` before for SSE sessions: the command now starts
a Streamable HTTP server instead. Update your MCP client to point to `/mcp`.

```

---

## Open Questions for Reviewer

1. **`serve-sse` visibility**: Should the command be hidden (`#[command(hide = true)]`)
   so it does not appear in `--help`, but still prints the deprecation message when
   invoked? Or should it appear (unhidden) with a clear `[REMOVED]` prefix in the
   description? Recommend: unhidden so the migration message is visible.

2. **`StreamableHttpServerConfig::stateful_mode`**: The default is `true` (stateful
   session management with reconnect). This is correct for a multi-worker server but
   adds `Mcp-Session-Id` header overhead. If stateless mode is preferred for simplicity,
   set `stateful_mode: false`. Recommend: keep `stateful_mode: true` (default) to
   match the counter example and allow client reconnect.

3. **axum feature flags**: `axum = { version = "0.8", features = ["tokio", "http1", "json"] }` —
   verify `json` feature needed or if `axum::Json` comes from default features.
