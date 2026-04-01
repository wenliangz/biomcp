## Execution Order
1. Record scope and baseline proof surfaces in `.march/code-log.md`, then run the existing targeted checks for `src/utils/download.rs` and static searches — [status: done]
2. Add proof-first coverage that fails while legacy helpers still exist, then rerun the targeted test to confirm the red state — [status: done]
3. Remove the legacy helpers from `src/utils/download.rs`, rerun targeted tests/searches, and commit the logical cleanup change — [status: done]
4. Run `make check`, review/stage only intended repo changes, and finalize this code log — [status: done]

## Resume State
- Last completed batch: 4
- Files edited so far: [.march/code-log.md, src/utils/download.rs, tests/legacy_cache_helper_cleanup.rs]
- Existing partial edits: preserve
- Tests passing: `cargo test utils::download --lib`; `cargo test --test legacy_cache_helper_cleanup`; `rg 'biomcp_cache_dir\\(|biomcp_downloads_dir\\(|cache_path\\(' src`; `rg '^(pub fn biomcp_cache_dir|pub fn biomcp_downloads_dir|pub fn cache_path)' src/utils/download.rs`; `rg 'biomcp_cache_dir|biomcp_downloads_dir|cache_path' spec`; `make check < /dev/null 2>&1`
- Next concrete action: none
- Current blocker: none

## Out of Scope
- Any cache-root behavior changes or rewiring to `resolve_cache_config()`
- Changes to `src/sources/mod.rs`, `src/cli/health.rs`, `src/entities/article.rs`, or `src/sources/ema.rs`
- Removing the `dirs` dependency from `Cargo.toml`
- Editing `spec/*.md` for operator-facing behavior that did not change

## Commands and Changes
- `checkpoint status`
- `GIT_EDITOR=true git rebase main`
- `git --no-pager diff --stat main..HEAD | tail -1`
- Reviewed `.march/design-final.md` as authoritative plus `.march/design-draft.md`, `.march/investigation-notes.md`, and `.march/ticket.md` for background and scope confirmation.
- Found and replaced a stale carried-over `.march/code-log.md` from the prior ticket so this step has a T105-specific execution log.
- Verified baseline proof surface:
  - `cargo test utils::download --lib`
  - `rg 'biomcp_cache_dir\(|biomcp_downloads_dir\(|cache_path\(' src`
  - `rg 'biomcp_cache_dir|biomcp_downloads_dir|cache_path' spec`
- Transition note recorded: batch 1 complete, moving to proof-first red coverage for the helper removal.
- Added proof-first source-shape test `legacy_cache_helpers_are_removed` to `src/utils/download.rs`.
- Red proof confirmed: `cargo test utils::download::tests::legacy_cache_helpers_are_removed --lib` failed because `biomcp_cache_dir()` still exists in the module source.
- Transition note recorded: batch 2 complete, moving to helper deletion and green proof.
- Removed `biomcp_cache_dir()`, `biomcp_downloads_dir()`, and `cache_path()` from `src/utils/download.rs` while preserving `cache_key()`, `download_path()`, `write_atomic_bytes()`, and `save_atomic()`.
- Relocated the source-shape proof into `tests/legacy_cache_helper_cleanup.rs` so `rg ... src` acceptance checks stay clean.
- Green proof after implementation:
  - `cargo test --test legacy_cache_helper_cleanup`
  - `cargo test utils::download --lib`
  - `rg 'biomcp_cache_dir\(|biomcp_downloads_dir\(|cache_path\(' src`
  - `rg '^(pub fn biomcp_cache_dir|pub fn biomcp_downloads_dir|pub fn cache_path)' src/utils/download.rs`
  - `rg 'biomcp_cache_dir|biomcp_downloads_dir|cache_path' spec`
- Staged repo changes: `git add src/utils/download.rs tests/legacy_cache_helper_cleanup.rs`
- Logical commit created: `cfac6b6` — `Remove legacy download cache helpers`
- Transition note recorded: batch 4 start, moving to full verification and final git hygiene.
- Full verification gate:
  - `make check < /dev/null 2>&1`
  - repo lint passed
  - repo tests passed, including `tests/legacy_cache_helper_cleanup.rs`
  - quality ratchet passed
- Reviewed final repo diff and status:
  - `git --no-pager diff -- src/utils/download.rs tests/legacy_cache_helper_cleanup.rs`
  - `git --no-pager status --short`
  - only `.march/code-log.md` remains unstaged by design
- Docs/scripts assessment: no operator-facing or runtime-facing contract changed, so no docs or script updates were needed.
- Spec assessment: no new contract was introduced and `rg 'biomcp_cache_dir|biomcp_downloads_dir|cache_path' spec` stayed empty, so no spec updates were needed.

## Deviations from Design
- None.
