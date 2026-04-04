# Cache Commands

`biomcp cache path` and `biomcp cache stats` are the local operator commands for
inspecting the managed HTTP cache. One locates the resolved cache directory,
while the other reports local cache inventory and configured limits. Both stay
CLI-only because they expose workstation-local filesystem paths.

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

## Cache Stats JSON

`biomcp cache stats --json` is the machine-readable companion to `cache path`.
On a fresh XDG cache root it should report the resolved cache path, zeroed local
blob counts, and the default cache-policy limits in one JSON object.

```bash
bin="$(git rev-parse --show-toplevel)/target/release/biomcp"
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT
mkdir -p "$tmp_root/cache-home" "$tmp_root/config-home"
out="$(env XDG_CACHE_HOME="$tmp_root/cache-home" XDG_CONFIG_HOME="$tmp_root/config-home" "$bin" --json cache stats)"
echo "$out" | mustmatch like '"max_age_origin": "default"'
echo "$out" | jq -e --arg path "$tmp_root/cache-home/biomcp/http" '
  . == {
    path: $path,
    blob_bytes: 0,
    blob_count: 0,
    orphan_count: 0,
    age_range: null,
    max_size_bytes: 10000000000,
    max_size_origin: "default",
    max_age_secs: 86400,
    max_age_origin: "default"
  }
' > /dev/null
```

## Cache Stats Markdown

Default `cache stats` output is the operator-facing markdown summary. The empty
cache fixture should still render every visible row, including the configured
limit rows that explain the current size and age policy.

```bash
bin="$(git rev-parse --show-toplevel)/target/release/biomcp"
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT
mkdir -p "$tmp_root/cache-home" "$tmp_root/config-home"
out="$(env XDG_CACHE_HOME="$tmp_root/cache-home" XDG_CONFIG_HOME="$tmp_root/config-home" "$bin" cache stats)"
echo "$out" | mustmatch like "| Path | $tmp_root/cache-home/biomcp/http |"
echo "$out" | mustmatch like "| Blob bytes | 0 |"
echo "$out" | mustmatch like "| Blob files | 0 |"
echo "$out" | mustmatch like "| Orphan blobs | 0 |"
echo "$out" | mustmatch like "| Age range | none |"
echo "$out" | mustmatch like "| Max size | 10000000000 bytes (default) |"
echo "$out" | mustmatch like "| Max age | 86400 s (default) |"
```
