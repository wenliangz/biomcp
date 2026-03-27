# Code Log

## Commands run

- `checkpoint status`
- `cargo test mcp_allowlist_blocks_mutating_commands`
- `cargo build --quiet --bin biomcp`
- `uv sync --extra dev --no-install-project`
- `.venv/bin/python -m pytest tests/test_mcp_contract.py -q --mcp-cmd "./target/debug/biomcp serve" -k "description_matches_list_contract or mutating_study_download or charted_study_call_returns_text_then_svg_image"`
- `PATH="/home/ian/workspace/worktrees/070-security-fix-mcp-allowlist-permits-mutating-study-download-command/target/debug:$PATH" .venv/bin/python -m pytest spec/15-mcp-runtime.md --mustmatch-lang bash --mustmatch-timeout 60 -v`
- `cargo fmt`
- `./bin/lint`
- `cargo test`
- `cargo build --release --locked`
- `.venv/bin/python -m pytest tests/test_mcp_contract.py -q --mcp-cmd "./target/release/biomcp serve"`
- `PATH="/home/ian/workspace/worktrees/070-security-fix-mcp-allowlist-permits-mutating-study-download-command/target/release:$PATH" .venv/bin/python -m pytest spec/15-mcp-runtime.md --mustmatch-lang bash --mustmatch-timeout 60 -v`
- `.venv/bin/python -m mkdocs build --strict`

## What changed

- `src/mcp/shell.rs`
  - Replaced the blanket MCP allowlist for `study` with explicit subcommand checks.
  - Allowed read-only study commands (`list`, `query`, `filter`, `cohort`, `survival`, `compare`, `co-occurrence`).
  - Allowed `study download` only for the exact `--list` catalog form.
  - Rejected mutating or malformed `study download` forms.
  - Expanded `mcp_allowlist_blocks_mutating_commands()` to cover the allowed and rejected study shapes.

- `build.rs`
  - Kept the existing blocked-term filtering for mutating/package-management commands.
  - Added targeted study-line rewriting so the generated MCP description advertises `study download --list` but not install syntax.

- `tests/test_mcp_contract.py`
  - Added description assertions for the safe `study download --list` form.
  - Added an MCP runtime test that rejects `biomcp study download msk_impact_2017`.

- `docs/reference/mcp-server.md`
  - Documented the catalog-only MCP exception for `study download --list`.
  - Documented that operators must run study installs directly via CLI, outside MCP.
  - Updated executable doc assertions to match the new description/runtime contract.

- `spec/15-mcp-runtime.md`
  - Added an executable stdio MCP spec section proving `study download <study_id>` is rejected with the read-only error.

## Tests and specs added or updated

- Updated Rust unit proof in `src/mcp/shell.rs::mcp_allowlist_blocks_mutating_commands`.
- Updated Python MCP contract proof in `tests/test_mcp_contract.py`.
- Added executable MCP runtime proof in `spec/15-mcp-runtime.md`.

## Verification

- `./bin/lint` passed.
- `cargo test` passed.
- `tests/test_mcp_contract.py` passed against `./target/release/biomcp serve`.
- `spec/15-mcp-runtime.md` passed with mustmatch.
- `mkdocs build --strict` passed.

## Deviations from design

- None.

## Notes

- The full MCP Python contract suite was finalized against `./target/release/biomcp serve`, matching the repo's existing `test-contracts` workflow.
