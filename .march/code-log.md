# Code Log

## Commands Run

```bash
checkpoint status
sed -n '1,260p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,520p' .march/design-final.md
cargo test --test ema_auto_sync ema_sync_forces_reload_of_all_feeds -- --exact
cargo test --test ema_auto_sync clean_eu_search_downloads_missing_feeds -- --exact
cargo test --test ema_auto_sync
cargo test html_response_is_rejected_before_write --lib
cargo test malformed_json_is_rejected_before_write --lib
cargo test ema_sync_parses_subcommand --lib
cargo test mcp_allowlist_blocks_mutating_commands --lib
cargo fmt --check
cargo fmt
uv pip install --python .venv/bin/python pytest mustmatch pytest-asyncio pytest-timeout mcp jsonschema mkdocs-material pymdown-extensions
PATH="$PWD/target/debug:$PATH" .venv/bin/pytest spec/01-overview.md --mustmatch-lang bash --mustmatch-timeout 60 -q
PATH="$PWD/target/debug:$PATH" .venv/bin/pytest spec/05-drug.md --mustmatch-lang bash --mustmatch-timeout 60 -q
.venv/bin/pytest tests/test_mcp_contract.py tests/test_source_licensing_docs_contract.py tests/test_upstream_planning_analysis_docs.py tests/test_docs_changelog_refresh.py -q
git status --short
checkpoint done 1
checkpoint done 2
checkpoint done 3
checkpoint note "EMA sync is source-owned in src/sources/ema.rs with per-feed planning, first-use auto-download, 72h stale refresh, no-cache force refresh, and stale-file fallback warnings; ema sync stays CLI-only and excluded from MCP."
sed -n '1,220p' /home/ian/workspace/.agents/skills/checkpoint/SKILL.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md
checkpoint note "Verified the staged EMA auto-sync implementation matches the approved final design; the remaining work is clippy cleanup plus rerunning lint and targeted contract proofs."
cargo clippy -- -D warnings
cargo test --test ema_auto_sync
python -m pytest tests/test_mcp_contract.py -q
python3 -m pytest tests/test_mcp_contract.py -q
PATH="$PWD/target/debug:$PATH" .venv/bin/pytest tests/test_mcp_contract.py -q --mcp-cmd "./target/debug/biomcp serve"
PATH="$PWD/target/debug:$PATH" .venv/bin/pytest tests/test_mcp_contract.py -q -k "ema or description" --mcp-cmd "./target/debug/biomcp serve"
./bin/lint
```

## What Changed

- Extended `src/sources/ema.rs` in place, per the approved design:
  - added authoritative EMA feed metadata with local filenames + remote report filenames
  - added `EmaSyncMode::{Auto, Force}`
  - added `EmaClient::ready(...)` and `EmaClient::sync(...)`
  - implemented per-feed planning for fresh / stale / missing files
  - implemented first-use auto-download, 72-hour stale refresh, `--no-cache` force refresh, and stale-file fallback warnings
  - added internal `BIOMCP_EMA_REPORT_BASE` override for testability
  - validated downloaded bodies as JSON with a top-level `data` array before writing
  - collapsed the unchanged-body fast path in `sync_feed(...)` to satisfy clippy without changing behavior
- Added shared helpers for the sync path:
  - `src/sources/mod.rs`: `is_no_cache_enabled()` and `read_limited_body_with_limit(...)`
  - `src/utils/download.rs`: reusable atomic byte writer for sibling temp files, with `save_atomic(...)` refactored onto it
- Wired the EMA readiness contract into drug flows:
  - `src/entities/drug.rs` now uses `EmaClient::ready(EmaSyncMode::Auto).await?` for EMA-backed get/search paths
- Added the CLI-only manual sync surface:
  - `src/cli/mod.rs` now exposes `biomcp ema sync`
  - `build.rs` and `src/mcp/shell.rs` keep `ema sync` off the MCP description and allowlist
- Updated operator-facing docs and fixtures:
  - CLI/list reference now advertises `ema sync`
  - drug/user/source/troubleshooting docs now describe auto-download + manual refresh
  - `spec/fixtures/setup-ema-spec-fixture.sh` copies checked-in EMA fixtures into `.cache/` and touches them fresh for stable offline specs
  - `.gitignore` now ignores `.cache/`

## Tests And Proof Added/Updated

- Added Rust integration coverage in `tests/ema_auto_sync.rs` for:
  - first-use download
  - within-TTL reuse
  - single-feed stale refresh
  - single-feed missing repair
  - `--no-cache` full refresh
  - `ema sync` full refresh
  - custom `BIOMCP_EMA_DIR`
  - stale-file fallback
  - no-data failure
- Added EMA source unit tests in `src/sources/ema.rs` for:
  - feed-table contract
  - sync-plan classification
  - HTML / malformed payload rejection before write
- Added CLI/MCP proof updates:
  - `src/cli/mod.rs`: `ema_sync_parses_subcommand`, help assertion
  - `src/mcp/shell.rs`: allowlist test blocks `ema sync`
  - `tests/test_mcp_contract.py`: MCP description excludes `ema sync`
- Updated specs:
  - `spec/01-overview.md` now expects `ema sync` in the command reference
  - `spec/05-drug.md` now uses the copied/touched EMA fixture root instead of the checked-in fixture directory directly

## Verification Results

- Passed:
  - `cargo clippy -- -D warnings`
  - `cargo test --test ema_auto_sync`
  - `cargo test html_response_is_rejected_before_write --lib`
  - `cargo test malformed_json_is_rejected_before_write --lib`
  - `cargo test ema_sync_parses_subcommand --lib`
  - `cargo test mcp_allowlist_blocks_mutating_commands --lib`
  - `PATH="$PWD/target/debug:$PATH" .venv/bin/pytest tests/test_mcp_contract.py -q -k "ema or description" --mcp-cmd "./target/debug/biomcp serve"`
  - `PATH="$PWD/target/debug:$PATH" .venv/bin/pytest spec/01-overview.md --mustmatch-lang bash --mustmatch-timeout 60 -q`
  - `PATH="$PWD/target/debug:$PATH" .venv/bin/pytest spec/05-drug.md --mustmatch-lang bash --mustmatch-timeout 60 -q`
  - `.venv/bin/pytest tests/test_mcp_contract.py tests/test_source_licensing_docs_contract.py tests/test_upstream_planning_analysis_docs.py tests/test_docs_changelog_refresh.py -q`
  - `./bin/lint`

## Deviations

- Product implementation followed the approved design.
- Verification used `.venv` + direct `pytest` after installing the documented dev dependencies with `uv pip install`, instead of `uv run --extra dev`, because the editable-package path kept re-invoking a slow `maturin` release build before running the actual checks.
- Resumed verification narrowed the debug-binary MCP run to `tests/test_mcp_contract.py -k "ema or description"` because the full file hit an unrelated `discover` stack overflow in the debug server path before reaching the ticket-specific assertion.
