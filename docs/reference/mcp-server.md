# MCP Server Reference

BioMCP exposes one execution tool (`shell`) and a current resource inventory
centered on the help guide. This page documents the stable MCP contract and
executes lightweight checks against the source tree.

## Capability Advertisement

The server must advertise both tools and resources.

| Capability | Required |
|------------|----------|
| `tools` | enabled |
| `resources` | enabled |

```python
from pathlib import Path

repo_root = Path.cwd()
shell = (repo_root / "src/mcp/shell.rs").read_text()
assert "enable_tools()" in shell
assert "enable_resources()" in shell
```

## Resource Catalog

Current builds always publish the help resource:

| URI | Name | Notes |
|-----|------|-------|
| `biomcp://help` | BioMCP Overview | Always listed |

No `biomcp://skill/<slug>` resources are currently listed because the embedded
`skills/` tree ships no `use-cases/*.md` files.

```python
from pathlib import Path

repo_root = Path.cwd()
shell = (repo_root / "src/mcp/shell.rs").read_text()
use_cases_dir = repo_root / "skills" / "use-cases"
assert "RESOURCE_HELP_URI" in shell
assert 'uri: RESOURCE_HELP_URI.to_string()' in shell
assert 'name: "BioMCP Overview".to_string()' in shell
assert "list_use_case_refs()" in shell
assert not use_cases_dir.exists() or list(use_cases_dir.glob("*.md")) == []
```

## Resource Read Mapping

- `biomcp://help` maps to `show_overview()`.
- Compatibility reads for `biomcp://skill/<slug>` map to `show_use_case(<slug>)`
  when an embedded use-case exists.
- All successful reads return `text/markdown`.

```python
from pathlib import Path

repo_root = Path.cwd()
shell = (repo_root / "src/mcp/shell.rs").read_text()
assert "show_overview()" in shell
assert 'if let Some(slug) = uri.strip_prefix("biomcp://skill/")' in shell
assert "show_use_case(slug)" in shell
assert 'mime_type: Some("text/markdown".to_string())' in shell
```

## Unknown URI Behavior

Unknown resource URIs must return an MCP resource-not-found error and include a helpful message.

```python
from pathlib import Path

repo_root = Path.cwd()
shell = (repo_root / "src/mcp/shell.rs").read_text()
assert "resource_not_found" in shell
assert "Unknown resource:" in shell
```

## Companion Runtime Tests

Protocol-level checks are implemented in Python integration tests:

- `tests/conftest.py`
- `tests/test_mcp_contract.py`

These tests run a real `biomcp serve` session over stdio and validate:

- initialize handshake,
- tools inventory,
- current resource inventory,
- resource reads,
- invalid URI error semantics.

```python
from pathlib import Path

repo_root = Path.cwd()
assert (repo_root / "tests/conftest.py").exists()
assert (repo_root / "tests/test_mcp_contract.py").exists()
```
