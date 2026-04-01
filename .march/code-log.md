## Execution Order
1. Record T107 scope, out-of-scope guardrails, and baseline proof surfaces in this code log; run the existing cache path tests that cover the current `src/sources/mod.rs` seam — [status: done]
2. Add proof-first tests for migration outcomes and startup-boundary behavior, then run the targeted test set to confirm the intended red state — [status: done]
3. Implement the migration helper, internal exports, and `build_http_client` wiring; rerun the targeted tests to reach green and commit the implementation change — [status: done]
4. Run `make check`, review/stage only intended repo changes, and finalize this code log with commands, proof, and any deviations — [status: done]

## Resume State
- Last completed batch: 4
- Files edited so far: [.march/code-log.md, src/cache/migration.rs, src/cache/mod.rs, src/sources/mod.rs]
- Existing partial edits: preserve committed repo changes; keep `.march/code-log.md` unstaged as runtime artifact
- Tests passing: `cargo test renames_legacy_http_cache_directory_when_only_legacy_dir_exists --lib`; `cargo test skips_when_legacy_http_cache_directory_is_missing --lib`; `cargo test skips_when_runtime_http_directory_already_exists --lib`; `cargo test errors_when_legacy_path_is_not_a_directory --lib`; `cargo test errors_when_runtime_http_target_is_not_a_directory --lib`; `cargo test apply_migration_non_fatal_warns_and_continues_on_error --lib`; `cargo test build_http_client_renames_legacy_http_cache_before_client_init --lib`; `cargo test http_cache_dir_default_root_uses_xdg_cache_home_biomcp_http --lib`; `cargo test http_cache_dir_env_override_uses_biomcp_cache_dir_http --lib`; `make check < /dev/null 2>&1`
- Next concrete action: none
- Current blocker: none

## Out of Scope
- Any runtime cache path cutover beyond the already-live `<cache_root>/http/`
- Changes to `src/cli/health.rs`, `src/utils/download.rs`, docs, or `spec/*.md`
- Shared temp-dir test helper refactors outside the file-local duplication acknowledged by the design
- Platform-specific permission-failure filesystem tests without a deterministic cross-platform proof

## Commands and Changes
- `checkpoint status`
- `GIT_EDITOR=true git rebase main`
- `git --no-pager diff --stat main..HEAD | tail -1`
- Read `.march/design-final.md` as authoritative; read `.march/design-draft.md`, `.march/investigation-notes.md`, and `.march/ticket.md` as background only.
- Reviewed the current implementation seams in `src/cache/mod.rs`, `src/cache/config.rs`, and `src/sources/mod.rs`.
- Replaced a stale carried-over `.march/code-log.md` from another ticket with this T107-specific execution log before code changes.
- Verified the baseline proof surface called out by the design:
  - `cargo test http_cache_dir_default_root_uses_xdg_cache_home_biomcp_http --lib`
  - `cargo test http_cache_dir_env_override_uses_biomcp_cache_dir_http --lib`
- Confirmed there is no spec surface for this internal migration and that `make check` is the repo-wide verification gate.
- Added proof-first tests in `src/cache/migration.rs` and `src/sources/mod.rs` for the rename/skip/error outcomes, non-fatal warning seam, and end-to-end builder migration wiring.
- Confirmed the red state with:
  - `cargo test renames_legacy_http_cache_directory_when_only_legacy_dir_exists --lib`
  - current failure: missing `apply_migration_non_fatal` seam in `src/sources/mod.rs`, plus closure type inference pending that new helper signature
- Implemented `src/cache/migration.rs` with `MigrationOutcome`, metadata-based directory inspection that preserves real I/O failures, explicit non-directory errors, and `std::fs::rename` when the legacy directory exists and the runtime target is absent.
- Updated `src/cache/mod.rs` to export `migration`, `MigrationOutcome`, and `migrate_http_cache` internally.
- Refactored `src/sources/mod.rs` to:
  - resolve `cache_root` once from `resolve_cache_config()`
  - apply migration before `create_dir_all`
  - warn and continue through a private `apply_migration_non_fatal` seam
  - remove the redundant production `http_cache_dir()` helper
  - update path-resolution tests to assert via `resolve_cache_config()?.cache_root.join("http")`
- Green targeted proof after implementation:
  - `cargo test renames_legacy_http_cache_directory_when_only_legacy_dir_exists --lib`
  - `cargo test skips_when_legacy_http_cache_directory_is_missing --lib`
  - `cargo test skips_when_runtime_http_directory_already_exists --lib`
  - `cargo test errors_when_legacy_path_is_not_a_directory --lib`
  - `cargo test errors_when_runtime_http_target_is_not_a_directory --lib`
  - `cargo test apply_migration_non_fatal_warns_and_continues_on_error --lib`
  - `cargo test build_http_client_renames_legacy_http_cache_before_client_init --lib`
  - `cargo test http_cache_dir_default_root_uses_xdg_cache_home_biomcp_http --lib`
  - `cargo test http_cache_dir_env_override_uses_biomcp_cache_dir_http --lib`
- Formatted the Rust changes with `cargo fmt --all`.
- Ran the full repo verification gate:
  - `make check < /dev/null 2>&1`
  - lint passed
  - cargo test passed
  - quality ratchet passed
- Reviewed repo hygiene:
  - `git --no-pager diff -- src/cache/mod.rs src/cache/migration.rs src/sources/mod.rs`
  - `git add src/cache/mod.rs src/cache/migration.rs src/sources/mod.rs`
  - `git --no-pager diff --cached -- src/cache/mod.rs src/cache/migration.rs src/sources/mod.rs`
  - `git --no-pager diff --cached --check`
  - `git --no-pager status --short`
- Created logical commit:
  - `git commit -m "Add HTTP cache migration helper" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"`
  - commit: `192d537`
- Docs/scripts/spec review:
  - No docs or operator-facing script updates were needed because the approved design explicitly keeps docs and specs out of scope for this internal startup-side-effect ticket.
  - No new spec files or spec edits were needed because the migration adds no CLI/MCP/runtime contract surface beyond internal startup behavior.

## Deviations from Design
- None.
