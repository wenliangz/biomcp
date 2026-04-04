# Code Review Log — Ticket 145: Fix PubMed E-utilities query construction AND NOT bug

## Summary

Clean implementation. No defects found. No fixes needed.

## Design Completeness Audit

All 6 design changes verified in the diff:

| Design Item | Status | Location in Diff |
|---|---|---|
| Change 1: Fix `build_pubmed_search_term` | Present | article.rs:1403-1411 |
| Change 2: Update multi-filter regression test | Present | article.rs:3339 |
| Change 3: New standalone NOT unit test | Present | `build_pubmed_search_term_uses_standalone_not_for_retraction_filter` |
| Change 4: Wiremock request-path test | Present | `search_pubmed_page_sends_standalone_not_retraction_term` |
| Change 5: Federated participation test | Present | `federated_search_includes_pubmed_rows_in_matched_sources` |
| Change 6: Europe PMC unchanged | Confirmed | No Europe PMC code in diff |

No design items are missing from the implementation.

## Test-Design Traceability

All 8 proof matrix items verified:

| Proof Matrix Item | Test/Proof | Found |
|---|---|---|
| Simple PubMed term uses standalone NOT | `build_pubmed_search_term_uses_standalone_not_for_retraction_filter` | Yes |
| Multi-filter term keeps aliases + standalone NOT | `build_pubmed_esearch_params_reuses_article_type_aliases` (updated) | Yes |
| `search_pubmed_page` sends corrected upstream term | `search_pubmed_page_sends_standalone_not_retraction_term` | Yes |
| Europe PMC retraction syntax unchanged | `build_search_query_excludes_retracted_when_requested` (unmodified) | Yes |
| Federated search surfaces PubMed participation | `federated_search_includes_pubmed_rows_in_matched_sources` | Yes |
| Live `--source pubmed` returns results | Verified in code-log via CLI | Yes |
| Live federated includes PubMed in `matched_sources` | Verified in code-log via CLI | Yes |
| `make check` passes | Independently confirmed during review | Yes |

## Implementation Quality

- **Fix is minimal and correct**: Positive clauses joined with `" AND "`, then retraction clause appended with standalone `" NOT "`. Matches PubMed E-utilities boolean grammar.
- **Empty-base guard**: Defensive branch for unreachable-in-practice case where no positive clauses exist. Returns `"NOT retracted publication[pt]"` without leading space. Matches design rationale.
- **No new abstractions**: Fix stays within `build_pubmed_search_term`. No helpers, utilities, or structural changes.
- **Convention adherence**: Code follows existing patterns in the file (early returns, string formatting, test structure).
- **Europe PMC isolation**: Searched for `AND NOT` in src/. Europe PMC uses `AND NOT PUB_TYPE:` (Solr syntax) — correct and unchanged. Trial code uses `AND NOT` in boolean expression parsing — unrelated.

## Security

No concerns. Search filters are validated upstream before reaching `build_pubmed_search_term`. No untrusted input flows into shell commands, file paths, or queries without validation.

## Performance

N/A. String construction at search request time. No algorithmic concerns.

## Spec Coverage

- `spec/06-article.md` lines 126-133 cover live `--source pubmed` smoke test (existing, should now pass with the fix).
- **Spec gap noted in design**: No stable spec assertion for federated `matched_sources` containing PubMed. The deterministic wiremock test (`federated_search_includes_pubmed_rows_in_matched_sources`) covers this locally. This is acceptable — live federated results are non-deterministic due to ranking.

## Residual Concerns for Verify

None. The implementation is complete and all proof matrix items are covered.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| — | — | — | None found |
