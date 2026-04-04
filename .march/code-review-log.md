# Code Review Log — Ticket 149: Add Article Ranking Calibration Fixtures

## Critique

### Design Completeness Audit

All six architecture decisions from `design-final.md` have corresponding code
changes:

1. **AD1** — `mod ranking_calibration` with `lb100_mesh_synonym_fixture()` and
   `lb100_anchor_count_fixture()` builders: present in `src/entities/article.rs`
2. **AD2** — Two baseline tests (`mesh_synonym_gap_records_pubmed_tier0_baseline`,
   `anchor_count_gap_records_pubmed_title_hit_deficit_baseline`): present
3. **AD3** — `benchmarks/bioasq/ranking-calibration/README.md` with verified
   scenarios and historical leads: present and well-structured
4. **AD4** — Discoverability links in `benchmarks/bioasq/README.md` and
   `docs/reference/bioasq-benchmark.md`: both present
5. **AD5** — Contract test extensions in `tests/test_bioasq_benchmark_contract.py`:
   two new test functions covering all five required assertions
6. **AD6** — No new spec: confirmed, no spec changes in diff

No design items are missing from the implementation.

### Test-Design Traceability

Every proof matrix entry has a matching test:

| Proof Matrix Item | Test Location | Verified |
|---|---|---|
| Mode A fixture tier-0 baseline | `article.rs:5699` | yes |
| Mode B fixture anchor-count baseline | `article.rs:5736` | yes |
| Positive control PubMed win | `article.rs:4170` (pre-existing) | yes |
| Calibration docs discoverable | `test_bioasq_benchmark_contract.py:27,47` | yes |
| Existing live JSON contract | `spec/06-article.md` (pre-existing, no new spec per design) | yes |
| `make check` | Ran independently, all green | yes |

No gaps found between design proof matrix and test coverage.

### Quality Checks

- **Implementation quality**: Code follows existing test module conventions.
  The `calibration_row` builder properly extends the existing `row()` helper.
  The nested `mod ranking_calibration` keeps the calibration surface
  well-scoped.
- **Test quality**: Tests assert ranking contract behavior (tier assignment,
  anchor hit counts, sort ordering). Position-based assertions correctly
  capture the baseline for ticket 150 to flip.
- **Performance**: N/A — test-only code and documentation.
- **Data completeness**: Calibration README covers all design-required sections.
  Contract tests verify content strings.
- **Security**: No user input handling, network calls, or shell commands.
- **Duplication**: `row_by_pmid` helper is new and scoped to the calibration
  module. No pre-existing equivalent in the test module.

### Spec Coverage

The design explicitly excludes new spec coverage (AD6). The existing structural
proof at `spec/06-article.md::Keyword Anchors Tokenize In JSON Ranking Metadata`
covers ranking metadata on the live JSON path. Ranking-order assertions against
live article responses are intentionally kept in Rust fixtures rather than specs,
per design rationale.

## Fixes Applied

None required. The implementation is correct and complete.

## Residual Concerns

None for verify to watch. The calibration surface is well-isolated from shipped
ranking behavior.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| — | — | — | None found |
