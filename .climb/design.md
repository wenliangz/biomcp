# Design: P051 - Trial Search Edge-Case Tests

## Ticket

T061: Trial search edge-case tests (age units, biomarker tokens, cursor boundary)

This review corrected one major inaccuracy from the prior design: the proposed
compound CTGov cursor is not warranted in the current codebase. The age-unit
fix is real, the PD-L1+ gap is test coverage only, and the cursor work should
stay at the regression-test layer because the current `trial.rs` CTGov search
path cannot stop mid-page against a compliant upstream response.

---

## Verified Facts From The Codebase

### Gap 1: `parse_age_years` is unit-blind

`src/entities/trial.rs` defines:

```rust
fn parse_age_years(value: &str) -> Option<u32> {
    let trimmed = value.trim().to_ascii_lowercase();
    let digits = trimmed.trim_end_matches(|c: char| !c.is_ascii_digit());
    let digits = digits.trim();
    if digits.is_empty() {
        return None;
    }
    digits.parse().ok()
}
```

That means:

- `"18 Years"` -> `Some(18)` (current tests cover this)
- `"6 Months"` -> `Some(6)` instead of `Some(0.5)`
- `"2 Weeks"` -> `Some(2)` instead of about `0.038`

`verify_age_eligibility` consumes `parse_age_years` for both minimum and
maximum age checks, so the parser bug directly affects CTGov post-filtering.

### Gap 2: `PD-L1+` matching already works; coverage is incomplete

`contains_keyword_tokens` escapes each token and delegates boundaries to
`build_token_pattern`.

For `PD-L1+`, the resulting pattern is effectively:

```text
\bPD\-L1\+($|[^\w])
```

That correctly matches:

- `"PD-L1+ expression"`
- `"PD-L1+"`

and correctly rejects:

- `"PD-L1 positive"` when the keyword is `PD-L1+`

Existing tests already cover:

- `HER2+`
- `ER+`
- `PD-L1` (without plus)
- plain word boundaries like `BRAF`

The missing coverage is specifically the hyphen-plus biomarker form.

### Gap 3: the previously proposed mid-page CTGov cursor fix is based on an unreachable production path

The current CTGov search path sets:

```rust
let page_size = limit.clamp(1, 100);
```

and then passes that `page_size` to `ClinicalTrialsClient::search`.

Within the same function:

- `page_study_count` is the number of post-filtered studies from the fetched
  CTGov page
- new rows are appended until `rows.len() >= limit`
- the "mid-page" branch is only taken when `page_consumed < page_study_count`

Against a compliant upstream CTGov response, a fetched page cannot contain more
than `page_size`, and here `page_size == limit`. That means a single fetched
page cannot contain more than `limit` CTGov studies, so the current trial
search implementation cannot hit `rows.len() >= limit` while leaving additional
studies unconsumed on that same fetched page.

This remains true even when `offset > 0`: with `page_size == limit`, there is
still no faithful way to both skip some rows and fill `limit` fresh rows while
also leaving extra rows unconsumed in the same response.

Conclusion: do not add a compound cursor format, do not change `--next-page`
semantics, and do not add a mock that returns oversized CTGov pages just to
force an impossible branch.

The valid cursor regression for the current code is narrower:

- when `offset` consumes part of a fetched page but the code still consumes the
  whole response, the returned cursor must remain the upstream `nextPageToken`
- no `next_page` format change is required

### Existing harnesses are sufficient

`src/entities/trial.rs` already has:

- unit tests near `parse_age_years` and `contains_keyword_tokens`
- async `MockServer` CTGov pagination tests
- `ClinicalTrialsClient::new_for_test(...)`

No new file, fixture system, or helper module is needed.

---

## Architecture Decisions

### AD-1: Change `parse_age_years` to `Option<f32>`

Fractional years are required for month/week/day inputs. Keeping `u32` would
force truncation or rounding in the wrong domain.

Implementation requirements:

- parse the leading numeric token as `f32`
- read the first unit token case-insensitively
- support `year|years|month|months|week|weeks|day|days`
- treat a missing unit as years
- return `None` for empty/unknown inputs such as `""` or `N/A`

Comparison sites in `verify_age_eligibility` must compare `age as f32` against
the parsed bounds.

### AD-2: Keep `contains_keyword_tokens` implementation unchanged

The code already handles `PD-L1+`. Only add tests that prove the intended
behavior and prevent regressions.

### AD-3: Keep CTGov `next_page` as the upstream token format

Do not introduce `CtGovCursorToken`, JSON cursor wrapping, or any new parsing
logic in `trial.rs`.

Instead, add one faithful regression test around the current cursor contract:

- offset may reduce the number of rows returned from a fetched page
- when the fetched page is fully consumed, the returned cursor must still be
  the upstream `nextPageToken`

If trial pagination is ever refactored to use a fixed CTGov page size larger
than `limit`, then a compound cursor design may become necessary. That is not
the current architecture and should not be pre-implemented here.

### AD-4: No `spec/` change for this ticket

This repo is spec-driven, but this ticket does not need a new executable spec.

Reasoning:

- the age-unit behavior is exercised through private helper logic fed by CTGov
  age strings, not a stable public CLI string contract
- the PD-L1+ gap is a private tokenizer boundary case
- the corrected cursor regression is about preserving an upstream token in a
  mocked pagination flow, not a stable live-API spec scenario

`spec/04-trial.md` already covers the outside-in trial search surface. The
faithful proof for this ticket belongs in focused Rust tests in
`src/entities/trial.rs`.

---

## File Disposition

| File | Action | Notes |
|------|--------|-------|
| `src/entities/trial.rs` | Modify | age parsing code fix, age/token/cursor regression tests |

No `spec/`, docs, CLI, renderer, or source-client files should change.

---

## Implementation Notes

### Age parsing

Preferred shape:

```rust
fn parse_age_years(value: &str) -> Option<f32>
```

Use a parser that is tolerant of normal CTGov strings:

- `"18 Years"`
- `"6 Months"`
- `"2 Weeks"`
- `"30 Days"`

The implementation should parse the first numeric token and the first unit
token rather than depending on trimming all non-digits from the tail.

### Age comparison

Update these two checks only:

```rust
.is_none_or(|min| age as f32 >= min)
.is_none_or(|max| age as f32 <= max)
```

### Token tests

Add tests near the existing `contains_keyword_tokens_*` cases:

- `contains_keyword_tokens_matches_hyphenated_plus_token`
- `contains_keyword_tokens_rejects_hyphenated_token_without_plus_suffix`

### Cursor regression

Add one async mock test using the existing `MockServer` pattern. Use a faithful
response shape where `pageSize == limit`.

Suggested scenario:

1. call `search_page_with_ctgov_client(..., limit = 3, offset = 1, next_page = None)`
2. first mocked CTGov page returns exactly 3 studies and `nextPageToken = "p2"`
3. because one row is skipped by offset, 2 rows are returned
4. because the fetched page was fully consumed, returned `next_page_token` is
   still `"p2"`

This proves the current cursor boundary without inventing a new cursor format.

---

## Acceptance Criteria

### 1. Age unit conversion

- `parse_age_years("18 Years")` returns `Some(18.0)`
- `parse_age_years("6 Months")` returns `Some(0.5)`
- `parse_age_years("2 Weeks")` returns a value close to `2.0 / 52.0`
- `parse_age_years("30 Days")` returns a value close to `30.0 / 365.0`
- `parse_age_years("N/A")` returns `None`
- `parse_age_years("")` returns `None`
- `verify_age_eligibility` excludes age `0` for a trial with minimum age
  `"6 Months"`
- `verify_age_eligibility` includes age `1` for that same trial

### 2. PD-L1+ token coverage

- `contains_keyword_tokens("PD-L1+ expression level >= 1%", "PD-L1+")` is `true`
- `contains_keyword_tokens("PD-L1 positive", "PD-L1+")` is `false`
- existing plus-token and hyphen-token tests continue to pass

### 3. Faithful CTGov cursor regression

- with `limit = 3`, `offset = 1`, and a mocked CTGov response containing
  exactly 3 studies plus `nextPageToken = "p2"`, the returned page contains
  2 results
- the returned `next_page_token` is `Some("p2".into())`
- no new JSON cursor envelope is introduced
- `validate_search_page_args` remains unchanged

---

## Dev Verification Plan

Run in the P051 worktree:

```bash
cd /home/ian/workspace/worktrees/P051-biomcp

cargo test --lib entities::trial

cargo test parse_age_years -- --nocapture
cargo test contains_keyword_tokens_matches_hyphenated_plus_token -- --nocapture
cargo test ctgov_cursor_preserves_next_page_token_after_offset_full_page_consumption -- --nocapture
```

Baseline check during review-design: `cargo test --lib entities::trial` is
already green on the current branch before implementation.

---

## Proof Matrix

| Proof type | Coverage |
|------------|----------|
| Spec proof | Not applicable for this ticket; behavior is private-helper/mock driven rather than a stable outside-in CLI contract |
| Unit test - age conversion | `parse_age_years_*` coverage for years, months, weeks, days, and invalid inputs |
| Unit/integration test - age eligibility | focused `verify_age_eligibility` coverage for sub-year minimum age |
| Unit test - PD-L1+ token | the two new `contains_keyword_tokens_*` cases plus the existing plus/hyphen tests |
| Async mock test - cursor | faithful offset/full-page-consumption regression preserving upstream `nextPageToken` |
| Dev proof | `cargo test --lib entities::trial` |

---

## Out Of Scope

- any change to trial CLI flags or query summaries
- any change to markdown/json pagination rendering
- any change to CTGov source client request/response types
- introducing a new CTGov cursor serialization format
- speculative fixes for a future trial pagination architecture that does not
  exist in the current codebase
