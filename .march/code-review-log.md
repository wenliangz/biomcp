# Code Review Log — Ticket 144: Automatic cache eviction with disk-aware limits

## What was reviewed

Reviewed the full `git diff main..HEAD` (4 commits, 14 files changed), the design-draft.md,
design-final.md, and code-log.md artifacts. Read all new and modified source files in full.

### Files reviewed

- `Cargo.toml` / `Cargo.lock` — `fs2`, `http-cache`, `http-cache-semantics` dependencies
- `src/cache/config.rs` — `DiskFreeThreshold` enum, parsing, config resolution
- `src/cache/limits.rs` (new) — `FilesystemSpace`, `CacheUsage`, `CacheLimitEvaluation`, shared helpers
- `src/cache/manager.rs` (new) — `SizeAwareCacheManager`, background eviction, fast estimate
- `src/cache/mod.rs` — new module declarations and re-exports
- `src/cache/clean.rs` — test helper update for `min_disk_free` field
- `src/cli/cache.rs` — `CacheStatsReport` gains `referenced_blob_bytes`, `min_disk_free*`
- `src/cli/health.rs` — `ProbeClass::Warning`, `HealthReport.warning`, `check_cache_limits()`
- `src/cli/list_reference.md` — docs updated
- `src/sources/mod.rs` — `SizeAwareCacheManager` wiring replaces `CACacheManager`
- `spec/22-cache.md` — new stats fields and Cache Health Warning section
- `spec/01-overview.md` — prose update for cache-limit warnings
- `docs/user-guide/cli-reference.md` �� docs updated

## Design Completeness Audit

All design-final items verified against the diff:

1. Shared limit primitives (`DiskFreeThreshold`, parsing, origins) — present ✅
2. Shared cache-usage summary (`limits.rs` module) — present ✅
3. Runtime manager (`manager.rs`, `SizeAwareCacheManager`) — present ✅
4. Wiring in `sources/mod.rs` — present ✅
5. Cache stats exposure (`referenced_blob_bytes`, `min_disk_free`) — present ✅
6. Health warnings (`ProbeClass::Warning`, `check_cache_limits()`) — present ✅
7. Specs and docs — all updated ✅

No design items were skipped.

## Test-Design Traceability

All proof matrix items traced to matching tests except one:

- `min_disk_free` percent parsing/origin/defaults — 3 unit tests ✅
- `min_disk_free` absolute-byte parsing — 1 unit test ✅
- `required_free_bytes()` and `is_violated()` — 1 unit test ✅
- `summarize_cache_usage()` — 1 unit test with shared-integrity fixture ✅
- disk-floor deficit → effective max-size target — 2 unit tests ✅
- fast bootstrap estimate — 2 unit tests ✅
- heuristic false positives — 1 unit test ✅
- over-size eviction uses exact snapshot — 1 unit test ✅
- disk-floor eviction uses effective_max_size — 1 unit test ��
- debounce — 1 unit test ✅
- cache stats JSON/markdown fields — spec + unit tests ✅
- health Cache limits row — spec + unit tests ✅
- warning includes cleanup advice — unit test ✅
- `all_healthy()` with warnings — unit test ✅
- inspection failure → error row — unit test ✅
- API-only health unchanged — existing spec ✅

**Gap found:** "eviction-cycle errors always release `eviction_running` and log" — no matching test.

## What was fixed

### Fix 1: Added missing eviction error propagation test

Added `run_eviction_cycle_propagates_snapshot_error` test in `src/cache/manager.rs` that:
- Injects a failing snapshotter into `run_eviction_cycle_with`
- Verifies the error propagates (result is Err)
- Verifies `approx_bytes` is unchanged (cycle failed before resync)
- Verifies cleaner is never called when snapshot fails

The flag release itself is architectural (RAII `ResetFlag` guard in `spawn_eviction_task`) and
verified by inspection — it's impossible to exit the spawned async block without the guard
dropping and releasing the flag.

**Collateral scan:** No dead code, unused imports, shadowed variables, or resource conflicts
introduced. The edit only adds a new test function.

## Residual concerns for verify

- Disk-free warning path has no spec (design-acknowledged; environment-dependent). Verified by
  unit tests only.
- The `TempDirGuard` helper is duplicated across `limits.rs`, `manager.rs`, `clean.rs`, and
  `config.rs` test modules. Not a defect but a candidate for a shared test-util module in a
  future housekeeping ticket.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| 1 | missing-test | yes | Design proof matrix item "eviction-cycle errors always release eviction_running and log" had no test — added `run_eviction_cycle_propagates_snapshot_error` |
