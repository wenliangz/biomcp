## Execution Order
1. Baseline and proof setup: confirm design scope, verify preconditions, run existing targeted tests/spec surfaces, then add failing proof-first tests — [status: done]
2. Runtime caller cutover: wire `src/sources/mod.rs`, `src/utils/download.rs`, and `src/cli/health.rs` to `resolve_cache_config()`, then compile and run targeted tests — [status: done]
3. Operator proof update: extend the full-health executable spec, rerun targeted spec/tests, and commit the logical change set(s) — [status: done]
4. Full verification and wrap-up: run `make check`, review/stage intended changes only, and finalize this code log — [status: done]

## Resume State
- Last completed batch: 4
- Files edited so far: [.march/code-log.md, spec/05-drug.md, src/sources/mod.rs, src/utils/download.rs, src/cli/health.rs]
- Existing partial edits: preserve
- Tests passing: `cargo test sources:: --lib`, `cargo test utils::download --lib`, `cargo test cli::health --lib`, focused cutover unit tests, `cargo build --release --locked`, `pytest spec/01-overview.md spec/05-drug.md --mustmatch-lang bash --mustmatch-timeout 60 -v`, `pytest spec/05-drug.md --mustmatch-lang bash --mustmatch-timeout 60 -v`, `make check < /dev/null 2>&1`
- Next concrete action: none
- Current blocker: none

## Out of Scope
- Removing `biomcp_cache_dir()`, `biomcp_downloads_dir()`, or `cache_path()` in this ticket
- Adding HTTP cache migration logic or moving old `http-cacache` contents
- Editing `spec/01-overview.md` or changing the `--apis-only` health contract
- Changing `src/entities/article.rs` or adding new public APIs/helpers beyond private seams needed for proof

## Commands and Changes
- `checkpoint status`
- `GIT_EDITOR=true git rebase main`
- `git --no-pager diff --stat main..HEAD | tail -1`
- Reviewed `.march/design-final.md` as authoritative plus `.march/design-draft.md`, `.march/investigation-notes.md`, and `.march/ticket.md` for background/scope.
- Verified preconditions and proof surfaces in `Makefile`, `spec/01-overview.md`, `spec/05-drug.md`, `src/cache/config.rs`, `src/sources/mod.rs`, `src/utils/download.rs`, `src/cli/health.rs`, and `src/test_support.rs`.
- Baseline proof: `cargo test sources:: --lib`
- Baseline proof: `cargo test utils::download --lib`
- Baseline proof: `cargo test cli::health --lib`
- Baseline proof: `cargo build --release --locked`
- Baseline proof: `XDG_CACHE_HOME="$PWD/.cache" PATH="$PWD/target/release:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest spec/01-overview.md spec/05-drug.md --mustmatch-lang bash --mustmatch-timeout 60 -v'`
- Note: direct pytest node selection for markdown headings (`spec/file.md::Heading`) did not resolve under this harness, so baseline spec verification used file-level execution instead.
- Added proof-first tests for:
  - `http_cache_dir()` default and env-override behavior in `src/sources/mod.rs`
  - `download_path()` default/env behavior plus `save_atomic()` honoring `cache.toml` in `src/utils/download.rs`
  - `check_cache_dir()` success/config-error contracts and `probe_cache_dir()` failure contract in `src/cli/health.rs`
  - full `biomcp health` cache-row visibility in `spec/05-drug.md`
- Red proof: focused test run failed on missing `http_cache_dir`, `download_path`, and `probe_cache_dir` seams before implementation, confirming the tests were exercising the intended cutover points.
- Implemented cutover wiring:
  - `src/sources/mod.rs` now resolves HTTP cache under `<cache_root>/http`
  - `src/utils/download.rs` now resolves write targets under `<cache_root>/downloads`
  - `src/cli/health.rs` now resolves cache root through `resolve_cache_config()` and separates config failure from path probing
- Focused green proof: all new Rust cutover tests passed after implementation.
- Follow-up cleanup: added narrow `#[cfg_attr(not(test), allow(dead_code))]` on preserved legacy helpers in `src/utils/download.rs` because T104 intentionally keeps them for compatibility while no live runtime caller still uses them.
- Focused operator proof: `spec/05-drug.md::EMA Health Readiness` now asserts presence of the cache row and passed under full file execution.
- Commit attempt initially failed only on `cargo fmt --check`; ran `cargo fmt --all` to normalize formatting before retrying the logical commit.
- Logical commit created: `6d072df` — `Cut runtime cache callers to canonical root`
- Full verification gate: `make check < /dev/null 2>&1`
- Final git hygiene: removed transient `.pytest_cache` and `spec/__pycache__`; verified only `.march/code-log.md` remains unstaged and no repo changes remain outside the committed T104 diff.

## Deviations from Design
- None.
