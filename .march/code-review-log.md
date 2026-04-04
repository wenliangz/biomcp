# Code Review Log — Ticket 148: Tokenize article keyword anchors and compact compounds

## Summary

Clean implementation. No defects found. No fixes needed.

## Design Completeness Audit

All 4 implementation plan items have matching code changes:

1. **Compact compound-name hyphens** — `normalize_compound_hyphens()` added in `src/transform/article.rs:45-50` with `OnceLock<Regex>` pattern matching adjacent code.
2. **Decompose keyword into multiple anchors** — `build_anchor_set()` in `src/entities/article.rs:1097-1127` separates keyword tokenization from structured filters.
3. **Keep `anchor_matches_text()` unchanged** — confirmed no changes to this function.
4. **Public-surface spec** — `spec/06-article.md` new section with `anchor_count == 4` assertion.

All 8 acceptance criteria have corresponding code or tests. No gaps found.

## Test-Design Traceability

All 7 proof matrix entries have matching tests:

| Proof matrix entry | Test found | Verified |
|---|---|---|
| Multi-word keyword becomes multiple anchors | `keyword_tokenization_decomposes_multi_word_into_separate_anchors` | yes |
| Structured/keyword overlap deduplicated | `keyword_tokenization_dedups_structured_filter_overlap` | yes |
| Compound forms normalize to one token | `normalize_article_search_text_compacts_compound_hyphens` | yes |
| Hyphenated query matches compact title | `compound_name_variants_match_symmetrically_in_ranking` | yes |
| Partial multi-token produces nonzero directness | `multi_concept_keyword_partial_match_scores_nonzero` | yes |
| All tokens in title produce tier 3 | `multi_concept_keyword_all_tokens_in_title_scores_tier3` | yes |
| JSON metadata reflects tokenized count | `spec/06-article.md` anchor_count == 4 assertion | yes |

No missing tests.

## Implementation Quality

- **Convention adherence**: Follows existing `OnceLock<Regex>` pattern, reuses `normalize_article_search_text` symmetry, dedup via `HashSet` is consistent with prior code.
- **Test quality**: Tests verify contract behavior (exact anchor vectors, tier levels, hit counts), not implementation details. Would catch regressions.
- **Performance**: `contains('-')` guard avoids regex overhead for the common case. `into_owned()` on `Cow` is idiomatic and bounded to hyphen-containing strings only.
- **No duplication**: Searched repo — no existing functions do similar compound-hyphen normalization or keyword tokenization.

## Security

No concerns. No untrusted input flows into file paths, shell commands, or queries. Regex is compiled once and reused.

## Spec Coverage

The new spec heading tests outside-in behavior: user passes a multi-word keyword query, JSON output reflects tokenized anchor count. Existing markdown rendering tests remain green and cover the rendering surface.

## Residual Concerns for Verify

None.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| — | — | — | None found |
