# Code Log

## Commands Run

```bash
checkpoint status
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,320p' .march/design-final.md
sed -n '1,320p' src/cli/mod.rs
sed -n '1,260p' benchmarks/bioasq/ingest_public.py
sed -n '1,260p' spec/15-mcp-runtime.md
sed -n '1,260p' docs/user-guide/cli-reference.md
sed -n '1,260p' design/ux/cli-reference.md
rg -n "serve-http|serve-sse|build_cli|parse_args|participants-area" src/cli/mod.rs benchmarks/bioasq/ingest_public.py tests spec docs design
cargo test --lib serve_http_help_describes_streamable_http
cargo fmt
cargo test --lib help
uv sync --extra dev --no-install-project
cargo build --release --bin biomcp
.venv/bin/pytest tests/test_mcp_http_surface.py -k "serve_http_help_matches_runtime_surface or top_level_help_hides_serve_sse_but_lists_serve_http or serve_sse_help_is_still_callable_and_deprecated or serve_sse_exits_non_zero_with_migration_message" -v
.venv/bin/pytest tests/test_bioasq_ingest.py -k "help or official" -v
.venv/bin/pytest tests/test_public_skill_docs_contract.py tests/test_upstream_planning_analysis_docs.py -k "public_skill_docs_match_current_cli_contract or technical_and_ux_docs_match_current_cli_and_workflow_contracts" -v
PATH="$PWD/target/release:$PATH" .venv/bin/pytest spec/15-mcp-runtime.md -v
git status --short
git ls-files --others --exclude-standard
```

## What Changed

- Added a canonical clap command builder and env-parse helper in `src/cli/mod.rs`, then switched `src/main.rs` to parse through that helper.
- Hid the global query-only `json` and `no_cache` flags from the runtime help surfaces by cloning the root args onto `mcp`, `serve`, `serve-http`, and `serve-sse` in hidden form before clap builds the tree.
- Marked `ServeSse` hidden from top-level help while preserving direct invocation and direct `--help`.
- Reworked `benchmarks/bioasq/ingest_public.py` help to use `RawDescriptionHelpFormatter`, a concise description, runnable examples, and a `Bundle lanes` epilog that separates the Public historical lane from the Official competition lane.
- Updated the operator-facing CLI reference and UX reference so `serve-sse` is documented as a hidden compatibility path instead of a primary top-level command.

## Tests And Proof

- Rust unit help proof updated in `src/cli/mod.rs`:
  - runtime commands do not advertise `--json` / `--no-cache`
  - `serve-http --help` still advertises Streamable HTTP, `/mcp`, `--host`, and `--port`
  - top-level help hides `serve-sse`
  - direct `serve-sse --help` still shows migration guidance
- Release-binary help proof updated in `tests/test_mcp_http_surface.py`
- BioASQ help and official-lane rejection proof updated in `tests/test_bioasq_ingest.py`
- Spec contract updated in `spec/15-mcp-runtime.md`
- Doc-contract assertions updated in:
  - `tests/test_public_skill_docs_contract.py`
  - `tests/test_upstream_planning_analysis_docs.py`

## Verification Results

- `cargo test --lib help`
- `.venv/bin/pytest tests/test_mcp_http_surface.py -k "serve_http_help_matches_runtime_surface or top_level_help_hides_serve_sse_but_lists_serve_http or serve_sse_help_is_still_callable_and_deprecated or serve_sse_exits_non_zero_with_migration_message" -v`
- `.venv/bin/pytest tests/test_bioasq_ingest.py -k "help or official" -v`
- `.venv/bin/pytest tests/test_public_skill_docs_contract.py tests/test_upstream_planning_analysis_docs.py -k "public_skill_docs_match_current_cli_contract or technical_and_ux_docs_match_current_cli_and_workflow_contracts" -v`
- `PATH="$PWD/target/release:$PATH" .venv/bin/pytest spec/15-mcp-runtime.md -v`

## Deviations

- No design deviations in the implementation.
- For local spec verification I prefixed `PATH` with `target/release` so `spec/15-mcp-runtime.md` exercised the freshly built `biomcp` binary rather than any other `biomcp` on the shell path.
