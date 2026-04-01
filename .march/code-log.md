## Execution Order
1. Baseline and proof setup: confirm scope, inspect prior art, run existing tests/specs surface, then add failing cache config tests — [status: done]
2. Implement cache config foundation: add dependency/module wiring and resolver implementation, then compile — [status: done]
3. Green proof: run targeted cache tests, fix failures, and commit logical change(s) — [status: done]
4. Full verification and wrap-up: run make check, review diff/status, clean staging, and finalize code log — [status: done]

## Resume State
- Last completed batch: 4
- Files edited so far: [.march/code-log.md, Cargo.toml, Cargo.lock, src/lib.rs, src/cache/mod.rs, src/cache/config.rs]
- Existing partial edits: preserve and continue
- Tests passing: `cargo test parse_cache_mode --lib`, `cargo test resolve_cache_mode --lib`, `cargo test cache::config --lib`, `make check < /dev/null 2>&1`
- Next concrete action: none; code step is complete
- Current blocker: none

## Out of Scope
- Rewiring existing cache callers to the new resolver
- Health command output changes
- CLI cache commands or new user-visible cache surfaces
- Cache directory rename or migration logic
- User-facing cache docs/spec changes unless contract unexpectedly changes

## Commands and Changes
- `GIT_EDITOR=true git rebase main`
- `git --no-pager diff --stat main..HEAD | tail -1`
- `checkpoint status`
- Reviewed `.march/design-final.md` plus draft/background notes and ticket scope.
- Inspected prior art in `src/sources/mod.rs`, `src/utils/download.rs`, `src/error.rs`, `src/test_support.rs`, and existing env-mutating test helpers.
- Baseline proof: `cargo test parse_cache_mode --lib`
- Baseline proof: `cargo test resolve_cache_mode --lib`
- Added proof-first cache resolver tests in `src/cache/config.rs` covering defaults, env/file/default precedence, strict TOML parsing, zero-value rejection, blank-dir rejection, and end-to-end resolver discovery.
- Red proof: `cargo test cache::config --lib` (captured 16 expected failures before implementation)
- Added `toml = "0.8"` to `Cargo.toml` and refreshed `Cargo.lock`.
- Added `mod cache;` in `src/lib.rs` with `#[cfg_attr(not(test), allow(dead_code))]` because T097 intentionally introduces the internal resolver before caller cutover.
- Added `src/cache/mod.rs` with the narrow crate-internal re-export surface: `CacheConfig` and `resolve_cache_config`.
- Implemented `src/cache/config.rs` with:
  - `CacheConfig { cache_root, max_size, max_age }`
  - fixed config discovery at `dirs::config_dir()/biomcp/cache.toml`
  - exact default cache root parity with current `biomcp_cache_dir()` fallback logic
  - trimmed env handling for `BIOMCP_CACHE_DIR` and `BIOMCP_CACHE_MAX_SIZE`
  - strict `cache.toml` parsing via `serde(deny_unknown_fields)`
  - deterministic validation for blank TOML dir and zero numeric values
  - path-qualified read and parse errors
  - pure helper coverage for precedence logic plus end-to-end resolver tests under `env_lock()`
- Green proof: `cargo fmt --all`
- Green proof: `cargo test cache::config --lib`
- Created logical commit: `Add cache config foundation` (`9fdc3ff`)
- Full verification: `make check < /dev/null 2>&1`
- Final git hygiene: reviewed `git status`, branch diff, and confirmed `.march/` remains unstaged runtime state only.
- Docs/scripts: no operator-facing/runtime contract changed in T097, so no docs or script updates were required.
- Specs: no user-visible cache surface was introduced in T097, so no spec changes were required by design.

## Deviations from Design
- None.
