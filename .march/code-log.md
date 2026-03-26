# Code Log

## Commands Run

```bash
checkpoint status
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
rg -n "Semantic Scholar|OptionalAuthGet|optional_auth_get" src/cli/health.rs
sed -n '80,280p' src/cli/health.rs
sed -n '620,760p' src/cli/health.rs
sed -n '1020,1585p' src/cli/health.rs
cargo test optional_auth_get_reports_ --lib
cargo fmt --all
cargo test sources::semantic_scholar::tests --lib
make check
git status --short
git add src/cli/health.rs src/sources/semantic_scholar.rs
git add -f .march/code-log.md
git diff --cached --stat
git diff --cached
```

## What Changed

- Updated `src/cli/health.rs` to extend `ProbeKind::OptionalAuthGet` with an optional unauthenticated-429 status override.
- Changed the Semantic Scholar health source descriptor to use the shorter affects text `Semantic Scholar features` and the new unauthenticated 429 guidance string.
- Updated the optional-auth probe path so an unauthenticated Semantic Scholar `429` renders as:
  - status: `unavailable (set S2_API_KEY for reliable access)`
  - latency: plain `Nms`
  - affects: omitted
  - probe class: `Healthy`
- Kept authenticated `429` responses on the existing generic error path, including the HTTP suffix and shortened affects text.
- Reworked the Semantic Scholar health tests to anchor to the production descriptor instead of duplicating a handwritten test descriptor.

## Tests And Proof Added/Updated

- Updated:
  - `optional_auth_get_reports_unauthed_semantic_scholar_as_healthy`
  - `optional_auth_get_reports_authed_semantic_scholar_as_configured`
- Added:
  - `optional_auth_get_reports_unauthenticated_429_as_unavailable`
  - `optional_auth_get_reports_authenticated_429_as_error`
- The new unauthenticated 429 proof asserts:
  - `ProbeClass::Healthy`
  - no `affects` field in JSON
  - `healthy == 1`, `excluded == 0`
  - markdown renders `-` in the `Affects` column when the table includes that column

## Verification Results

- `cargo test optional_auth_get_reports_ --lib`
- `cargo test sources::semantic_scholar::tests --lib`
- `make check`

All verification commands passed.

## Deviations

- Small test-only deviation from the design: `src/sources/semantic_scholar.rs` now wraps its mock-server tests with `with_no_cache(true)`. This was needed because `make check` exposed shared HTTP cache bleed between parallel Semantic Scholar tests. No production behavior changed outside `src/cli/health.rs`.
