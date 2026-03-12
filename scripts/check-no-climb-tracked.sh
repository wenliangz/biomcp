#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tracked="$(git ls-files '.climb/**')"

if [[ -n "$tracked" ]]; then
    echo "Error: tracked .climb files detected:" >&2
    echo "$tracked" >&2
    echo "Fix: git rm --cached <path>" >&2
    exit 1
fi

echo "No tracked .climb files found"
