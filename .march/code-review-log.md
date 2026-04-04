# Code Review Log — Ticket 147: Separate article source position from merge order

## Summary

Clean implementation. No defects found. No fixes needed.

## Design Completeness Audit

All 9 acceptance criteria from `design-final.md` have corresponding code changes:

| AC | Description | Status | Location |
|---|---|---|---|
| 1 | `source_local_position` field with `#[serde(skip)]` | Present | `article.rs:175-176` |
| 2 | `finalize_article_candidates` no overwrite | Present | `article.rs:2421-2423` |
| 3 | `merge_article_candidate` preserves min | Present | `article.rs:1032-1034` |
| 4 | `rank_articles_by_directness` tiebreaker | Present | `article.rs:1235` |
| 5 | Explicit per-leg counter in all 4 sources | Present | All four search functions |
| 6 | PubMed pre-offset positions preserved | Present | Position assigned before `visible_skipped` check |
| 7 | No append-order penalty | Present | New test proves it |
| 8 | Deduped rows keep min position | Present | New test proves it |
| 9 | `make check` passes | Confirmed | 1283 tests pass |

No design items are missing from the implementation.

## Test-Design Traceability

All 7 proof matrix items from `design-final.md` verified:

| Proof Matrix Item | Test/Proof | Found |
|---|---|---|
| Field exists, serialization unchanged | `article_search_result_serializes_unknown_retraction_as_null` (existing, passes) | Yes |
| PubMed pre-offset positions | `search_pubmed_page_applies_offset_after_filtering` (extended with position assertions) | Yes |
| Finalization preserves positions | `finalize_article_candidates_preserves_source_local_position` (new) | Yes |
| Dedup keeps min position | `merge_article_candidates_keeps_min_source_local_position` (new) | Yes |
| Federated relevance uses leg-local position | `federated_relevance_uses_source_local_position_not_merge_order` (new) | Yes |
| Existing ranking/merge behavior holds | Updated fixtures + renamed test | Yes |
| `make check` green | Independently verified | Yes |

## Implementation Quality

- **Minimal and correct**: Rename + one removed assignment + four push-site position assignments. No new structs, enums, or helpers.
- **Convention adherence**: Follows existing patterns (explicit counter with `saturating_add`, filter-then-assign-then-push flow).
- **EuropePMC retraction injection**: Replacement row uses `out.len()` for position. At that point `source_position == out.len()` (or `out.len() + 1` after pop), so values are equivalent. Consistent with design rule.
- **Semantic Scholar**: Initial struct sets `source_local_position: 0`, then overwrites with counter before push. Correct — initial value never reaches ranking.
- **No duplication**: 1:1 rename of existing field. No parallel tracking.

## Security

No concerns. `source_local_position` is `#[serde(skip)]` — no external input, no injection surface, no auth implications.

## Performance

No impact. O(1) position assignments at push sites. Same sort comparator structure.

## Spec Coverage

No new `spec/` file required. The changed behavior is an internal relevance tiebreaker using a `#[serde(skip)]` field — no stable CLI/documentation surface to assert with executable markdown. Intentional gap per approved design.

## Residual Concerns for Verify

- Architecture docs (`overview.md`, `source-integration.md`) still reference `insertion_index` in their problem-description sections. These are accurate as historical descriptions and out of scope for this ticket.
- The `weak_rows` fixture in `directness_ranking_uses_full_title_and_token_boundaries` was changed from `insertion_index: 0` to `source_local_position: 3`. Cosmetic only — the test outcome is determined by title-anchor coverage, not position.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| — | — | — | None found |
