# Claude Desktop (MCP) Setup

BioMCP can run as an MCP server over stdio. If your Claude Desktop build
offers the Anthropic Directory, install BioMCP there first. Use the JSON config
below when you want a local/manual setup.

## Add BioMCP server config

Use `biomcp serve` as the MCP command:

```json
{
  "mcpServers": {
    "biomcp": {
      "command": "biomcp",
      "args": ["serve"]
    }
  }
}
```

If `biomcp` is not on your PATH, use the absolute path to the binary (e.g. `~/.local/bin/biomcp`).

## Validate before connecting Claude

```bash
biomcp --version
biomcp health --apis-only
```

## Verify MCP-level behavior

When connected, clients should discover:

- one tool: `biomcp`
- one help resource (`biomcp://help`)

Current builds do not discover a browsable `biomcp://skill/<slug>` catalog because no embedded use-case files ship.
Resource discovery still gives agent clients a stable entry point before
execution.

## Operational tips

- Keep API keys in the client launch environment.
- Restart Claude Desktop after config changes.
- Prefer stable absolute paths in managed environments.

## Related docs

- [Skills](skills.md)
- [API keys](api-keys.md)
- [MCP server reference](../reference/mcp-server.md)
