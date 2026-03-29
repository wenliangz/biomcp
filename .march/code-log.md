# Code Log

## Commands Run

```text
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,200p' .march/ticket.md
sed -n '1,240p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
sed -n '1,220p' Makefile
rg -n "mustmatch|check-quality-ratchet|mcp allowlist|source registry|HEALTH_SOURCES|BIOMCP_STUDY_DIR"
uv run pytest tests/test_mcp_contract.py -q
cargo test mcp_allowlist_blocks_mutating_commands -- --nocapture
cargo test health_inventory_includes_all_expected_sources -- --nocapture
python3 tools/check-mcp-allowlist.py --json
python3 tools/check-source-registry.py --json
bash tools/check-quality-ratchet.sh
uv run pytest tests/test_quality_ratchet_contract.py -q
uv run pytest tests/test_quality_ratchet_contract.py tests/test_upstream_planning_analysis_docs.py -q
make spec-pr
make check < /dev/null
cargo test related_disease_oncology_with_local_match_prefers_top_mutated -- --nocapture
git status --short
git diff --cached --stat
```

## What Changed

- Added `tools/check-quality-ratchet.sh` to run the quality ratchet end-to-end and emit JSON artifacts under `.march/reality-check/`.
- Added `tools/check-mcp-allowlist.py` to audit CLI/MCP/build metadata for the approved read-only command contract.
- Added `tools/check-source-registry.py` to compare source modules, aliases, and `HEALTH_SOURCES` coverage.
- Wired `make check` through the new `check-quality-ratchet` target in [Makefile](/home/ian/workspace/worktrees/075-wire-quality-ratchet-into-biomcp-make-check/Makefile).
- Added proof coverage in [tests/test_quality_ratchet_contract.py](/home/ian/workspace/worktrees/075-wire-quality-ratchet-into-biomcp-make-check/tests/test_quality_ratchet_contract.py).
- Updated planning/docs expectations in [tests/test_upstream_planning_analysis_docs.py](/home/ian/workspace/worktrees/075-wire-quality-ratchet-into-biomcp-make-check/tests/test_upstream_planning_analysis_docs.py) and [architecture/technical/overview.md](/home/ian/workspace/worktrees/075-wire-quality-ratchet-into-biomcp-make-check/architecture/technical/overview.md).
- Tightened many `spec/*.md` assertions so they pass the ratchet lint while still matching current stable CLI output.
- Fixed a pre-existing test race in [src/render/markdown.rs](/home/ian/workspace/worktrees/075-wire-quality-ratchet-into-biomcp-make-check/src/render/markdown.rs) by serializing `BIOMCP_STUDY_DIR` mutation through the existing env lock.

## Proof Added Or Updated

- Added `tests/test_quality_ratchet_contract.py` for:
  - MCP allowlist success and drift failure
  - source registry success and drift failure
  - wrapper success and wrapper failure
- Updated spec proofs to satisfy the stricter matcher and to reflect current CLI output truthfully.

## Verification

- `uv run pytest tests/test_quality_ratchet_contract.py tests/test_upstream_planning_analysis_docs.py -q` passed.
- `bash tools/check-quality-ratchet.sh` passed.
- `make spec-pr` passed.
- `make check < /dev/null` passed.

## Deviations From Design

- The design assumed an installable `mustmatch>=0.0.4`. That version was not available from PyPI or the published upstream repository during implementation, so the ratchet wrapper carries the needed `mustmatch 0.0.4` lint behavior in-repo instead of raising the dependency floor.
