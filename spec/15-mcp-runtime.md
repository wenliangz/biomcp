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
echo "$out" | mustmatch like "--host"
echo "$out" | mustmatch like "--port"
echo "$out" | mustmatch not like "--json"
echo "$out" | mustmatch not like "--no-cache"
```

## Top-Level Discovery

`biomcp --help` should list the current Streamable HTTP transport and omit the
legacy SSE migration shim from first-run discovery.

```bash
out="$(biomcp --help)"
echo "$out" | mustmatch like "serve-http"
echo "$out" | mustmatch not like "serve-sse"
```

## Legacy SSE Help

`serve-sse --help` exists only as a migration aid and should point back to
`serve-http`.

```bash
out="$(biomcp serve-sse --help)"
echo "$out" | mustmatch like "removed"
echo "$out" | mustmatch like "serve-http"
echo "$out" | mustmatch like "/mcp"
echo "$out" | mustmatch not like "--json"
echo "$out" | mustmatch not like "--no-cache"
```

## Stdio Tool Identity

The stdio MCP handshake should advertise the BioMCP execution tool as
`biomcp`, not the old `shell` name.

```bash
out="$( (printf '%s\n%s\n%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"spec","version":"0.1"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'; \
  sleep 1) | biomcp serve 2>/dev/null)"
echo "$out" | mustmatch like '"name":"biomcp"'
echo "$out" | mustmatch not like '"name":"shell"'
```
