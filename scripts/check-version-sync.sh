#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

extract_version() {
    local file="$1"
    local line
    line="$(grep -m1 -E '^version\s*=\s*"' "$file" || true)"
    if [[ -z "$line" ]]; then
        echo "" && return
    fi
    sed -E 's/^[^"]*"([^"]+)".*$/\1/' <<<"$line"
}

extract_lock_version() {
    local file="$1"
    awk '/name = "biomcp-cli"/{found=1} found && /^version/{print; exit}' "$file" \
        | sed -E 's/^[^"]*"([^"]+)".*$/\1/'
}

cargo_version="$(extract_version "$repo_root/Cargo.toml")"
python_version="$(extract_version "$repo_root/pyproject.toml")"
lock_version="$(extract_lock_version "$repo_root/Cargo.lock")"

if [[ -z "$cargo_version" || -z "$python_version" || -z "$lock_version" ]]; then
    echo "Unable to read version from one or more manifests:" >&2
    echo "  Cargo.toml:     '$cargo_version'" >&2
    echo "  pyproject.toml: '$python_version'" >&2
    echo "  Cargo.lock:     '$lock_version'" >&2
    exit 1
fi

ok=true

if [[ "$cargo_version" != "$python_version" ]]; then
    echo "Version mismatch: Cargo.toml=$cargo_version, pyproject.toml=$python_version" >&2
    ok=false
fi

if [[ "$cargo_version" != "$lock_version" ]]; then
    echo "Version mismatch: Cargo.toml=$cargo_version, Cargo.lock=$lock_version" >&2
    ok=false
fi

if [[ "$ok" == false ]]; then
    exit 1
fi

echo "Versions in sync: $cargo_version"
