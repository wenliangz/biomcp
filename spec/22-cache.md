# Cache Path

`biomcp cache path` is the local operator command for discovering the managed
HTTP cache directory. It is read-only, prints a plain-text path, and stays
CLI-only because exposing workstation-local filesystem paths over MCP would
cross the runtime security boundary.

## Cache Path

The command should print `<resolved cache_root>/http` exactly, using the same
cache-root resolution rules as runtime HTTP caching while avoiding directory
creation or migration side effects.

```bash
bin="$(git rev-parse --show-toplevel)/target/release/biomcp"
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT
mkdir -p "$tmp_root/cache-home" "$tmp_root/config-home/biomcp"
cat >"$tmp_root/config-home/biomcp/cache.toml" <<'EOF'
[cache]
dir = "relative-cache"
EOF

out="$(env XDG_CACHE_HOME="$tmp_root/cache-home" XDG_CONFIG_HOME="$tmp_root/config-home" "$bin" cache path)"
echo "$out" | mustmatch like "relative-cache/http"
test ! -d "$tmp_root/relative-cache"
```

## JSON Flag Exception

`biomcp cache path` is a documented exception to the usual query-command JSON
contract. Even under the global `--json` flag, it must print the same plain-text
path instead of a JSON object.

```bash
bin="$(git rev-parse --show-toplevel)/target/release/biomcp"
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT
mkdir -p "$tmp_root/cache-home" "$tmp_root/config-home"

plain="$(env XDG_CACHE_HOME="$tmp_root/cache-home" XDG_CONFIG_HOME="$tmp_root/config-home" "$bin" cache path)"
json_flag="$(env XDG_CACHE_HOME="$tmp_root/cache-home" XDG_CONFIG_HOME="$tmp_root/config-home" "$bin" --json cache path)"

test "$plain" = "$json_flag"
echo "$json_flag" | mustmatch like "$tmp_root/cache-home/biomcp/http"
echo "$json_flag" | mustmatch not like "{"
```
