# Design: T068 — Fix --age fractional year support (u32 -> f32)

## Summary

Change the `--age` CLI flag and `TrialSearchFilters.age` field from `u32` to `f32`
so fractional year inputs (e.g. `0.5` for 6 months) are accepted without truncation.
Remove the redundant `age as f32` casts inside `verify_age_eligibility`. Update the
help text and EXAMPLES block. Add a spec regression contract for `--age 0.5`.

---

## Architecture Decisions

**Why f32 and not f64?**
Age comparisons use `parse_age_years` which already returns `f32`. The existing
`age as f32` casts in `verify_age_eligibility` confirm the internal contract is f32.
Matching that type eliminates the casts and keeps precision consistent throughout.

**Shared filter struct still needs fixture/test updates.**
`TrialSearchFilters.age` is only used for numeric matching on the CTGov post-filter
path, but the shared struct is also constructed in CLI summary tests and in the NCI
validation test that rejects `--age` for `--source nci`. Widening the field to `f32`
therefore requires updating those helper/test literals too, even though the NCI runtime
behavior does not change.

**Clap parses f32 natively.**
Replacing `Option<u32>` with `Option<f32>` in the `#[arg]` declaration is sufficient;
clap will accept `0.5`, `6.5`, `67`, etc. and emit a user-friendly error for non-numeric
input.

---

## File Disposition

| File | Change |
|---|---|
| `src/cli/mod.rs:478` | `age: Option<u32>` → `Option<f32>`; update `#[arg]` doc comment |
| `src/cli/mod.rs:444–452` | Add `--age 0.5` example to `Trial` EXAMPLES block |
| `src/cli/mod.rs:5057` | Update `trial_search_query_summary_includes_geo_filters` fixture literal to `Some(67.0)` |
| `src/cli/mod.rs:5448` | Change the existing `search_trial_parses_new_filter_flags` regression to parse `--age 0.5` and assert `Some(0.5_f32)` |
| `src/entities/trial.rs:128` | `pub age: Option<u32>` → `Option<f32>` |
| `src/entities/trial.rs:1046` | `fn verify_age_eligibility(…, age: u32)` → `age: f32`; drop `age as f32` casts at lines 1057, 1061 |
| `src/entities/trial.rs:2039` | Update the sub-year eligibility tests to pass fractional literals (`0.0_f32`, `0.5_f32`, `1.0_f32`) instead of only integers |
| `src/entities/trial.rs:2396` | Update `nci_source_rejects_age_filter` fixture literal to `Some(67.0)` |
| `src/entities/trial.rs:2507` | Update `age_filtered_ctgov_filters()` helper to `age: Some(51.0)` so downstream CTGov pagination/count tests still compile unchanged |
| `spec/04-trial.md` | Insert **Fractional Age Filter** immediately after **Age Filter Count Stability** |

---

## Code Sketches

### cli/mod.rs — arg declaration (line 476–478)

```rust
/// Patient age in years for eligibility matching (decimals accepted, e.g. 0.5 for 6 months)
#[arg(long)]
age: Option<f32>,
```

### cli/mod.rs — EXAMPLES block (line 447)

Insert after the `--age 67` example line:

```
  biomcp search trial --age 0.5 --count-only          # infants eligible (6 months)
```

Full block becomes:
```
EXAMPLES:
  biomcp search trial -c melanoma -s recruiting
  biomcp search trial -p 3 -i pembrolizumab
  biomcp search trial -c melanoma --facility \"MD Anderson\" --age 67 --limit 5
  biomcp search trial --age 0.5 --count-only          # infants eligible (6 months)
  biomcp search trial --mutation \"BRAF V600E\" --status recruiting --study-type interventional --has-results --limit 5
  biomcp search trial -c \"endometrial cancer\" --criteria \"mismatch repair deficient\" -s recruiting
```

### entities/trial.rs — TrialSearchFilters field (line 128)

```rust
pub age: Option<f32>,
```

### entities/trial.rs — verify_age_eligibility (line 1046)

```rust
fn verify_age_eligibility(studies: Vec<CtGovStudy>, age: f32) -> Vec<CtGovStudy> {
    studies
        .into_iter()
        .filter(|study| {
            let module = study
                .protocol_section
                .as_ref()
                .and_then(|s| s.eligibility_module.as_ref());
            let min_ok = module
                .and_then(|m| m.minimum_age.as_deref())
                .and_then(parse_age_years)
                .is_none_or(|min| age >= min);
            let max_ok = module
                .and_then(|m| m.maximum_age.as_deref())
                .and_then(parse_age_years)
                .is_none_or(|max| age <= max);
            min_ok && max_ok
        })
        .collect()
}
```

### Unit test updates — entities/trial.rs (~2039)

```rust
// verify_age_eligibility_handles_sub_year_minimum_age
assert!(verify_age_eligibility(vec![study.clone()], 0.0_f32).is_empty());
assert_eq!(verify_age_eligibility(vec![study], 0.5_f32).len(), 1);

// verify_age_eligibility_handles_sub_year_maximum_age
assert_eq!(verify_age_eligibility(vec![study.clone()], 0.5_f32).len(), 1);
assert!(verify_age_eligibility(vec![study], 1.0_f32).is_empty());
```

### Unit test updates — cli/mod.rs (~5057, ~5448)

```rust
// trial_search_query_summary_includes_geo_filters
age: Some(67.0),

// search_trial_parses_new_filter_flags
assert_eq!(age, Some(0.5_f32));
```

### Fixture/helper updates — entities/trial.rs (~2396, ~2507)

```rust
nci_source_rejects_age_filter => age: Some(67.0)
age_filtered_ctgov_filters() => age: Some(51.0)
```

---

## spec/04-trial.md — New Section

Insert after the existing **Age Filter Count Stability** section in `spec/04-trial.md`
so the trial spec keeps all age-related behavior together:

````markdown
## Fractional Age Filter

Fractional year input matters because ClinicalTrials.gov eligibility often uses
months for pediatric studies. This regression guards the `u32` truncation bug that
silently converted `--age 0.5` into `--age 0`.

```bash
out="$("$(git rev-parse --show-toplevel)/target/release/biomcp" search trial --age 0.5 --count-only)"
echo "$out" | mustmatch like "Total: "
echo "$out" | grep -qE "^Total: [0-9]+"
```
````

---

## Acceptance Criteria

1. `biomcp search trial --age 0.5 --count-only` exits 0 and prints a line matching `Total: [0-9]+`.
2. `biomcp search trial --age 67 --count-only` continues to work (whole-number strings still parse as `f32`, so existing integer workflows remain valid).
3. `biomcp search trial --age abc` emits a clap parse error (non-numeric rejected).
4. `verify_age_eligibility` called with `0.0_f32` excludes studies whose minimum age is `"6 Months"`.
5. `verify_age_eligibility` called with `0.5_f32` includes a study with minimum age `"6 Months"` and a study with maximum age `"6 Months"`.
6. `--help` output for `--age` mentions decimals and gives `0.5` as an example.
7. The existing NCI validation path still rejects `--age` for `--source nci` after the shared filter type change.
8. All existing unit tests pass after the field-type changes.
9. The new `spec/04-trial.md` **Fractional Age Filter** case passes.

---

## Success Checklist Coverage

| Item | Covered by |
|---|---|
| Writes the required ticket state | All u32→f32 changes, helper/test fixture updates, help text, EXAMPLES, and the age-focused spec section defined above |
| Preserves queue consistency | No structural change to TrialSearchFilters layout; f32 is same size as u32 |
| Leaves the operator-visible result clear | EXAMPLES block updated; spec contract is explicit and runnable |

All three checklist items fully addressed.

---

## Proof Matrix

| Layer | Proof |
|---|---|
| Spec | `spec/04-trial.md` Fractional Age Filter — exits 0, output matches `Total: [0-9]+` |
| Unit (entities) | Updated `verify_age_eligibility_handles_sub_year_*` tests prove `0.0_f32` excludes `"6 Months"` and `0.5_f32` includes it; no casts remain |
| Unit (cli parse) | Existing `search_trial_parses_new_filter_flags` case now parses `--age 0.5` and asserts `Some(0.5_f32)` |
| Unit (shared filter fixtures) | `trial_search_query_summary_includes_geo_filters`, `nci_source_rejects_age_filter`, and `age_filtered_ctgov_filters()` compile and preserve prior behavior with `f32` literals |
| Dev smoke | `cargo test` passes; `./target/release/biomcp search trial --age 0.5 --count-only` exits 0 |
| Clippy | `cargo clippy` clean — no `age as f32` casts remain |

---

## Dev Verification Plan

```bash
cd /home/ian/workspace/worktrees/T068-biomcp
cargo test 2>&1 | tail -10
cargo clippy -- -D warnings 2>&1 | tail -5
cargo build --release 2>&1 | tail -3
./target/release/biomcp search trial --age 0.5 --count-only
./target/release/biomcp search trial --age 67 --count-only
./target/release/biomcp search trial --help | grep -A2 '\-\-age'
```
