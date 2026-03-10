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
