# Code Review Log — Ticket 150: Promote PubMed-unique hits with explicit source signals

## Phase 1 — Critique

### Design Completeness Audit

All 13 acceptance criteria from `design-final.md` verified against the diff:

1. Private `ArticleCandidate`/`ArticleSourcePosition` structs preserve per-source positions through dedup — ✓
2. `ArticleRankingMetadata` includes `pubmed_rescue`, `pubmed_rescue_kind`, `pubmed_source_position` — ✓
3. Rescue eligibility: weak-lexical (directness_tier ≤ 1), PubMed position 0, PubMed-unique or strictly led — ✓
4. Shared-source tie at position 0 does not rescue — ✓ (tested)
5. Shared-source trailing PubMed does not rescue — ✓ (tested)
6. PubMed position > 0 does not rescue — ✓ (tested)
7. mesh_synonym calibration fixture flips — ✓
8. anchor_count calibration fixture flips — ✓
9. Merged multi-source PubMed-led row rescues with kind=Led — ✓
10. Markdown explains rescued rows with `pubmed-rescue` text — ✓
11. Markdown and JSON share `ARTICLE_RELEVANCE_RANKING_POLICY` constant — ✓
12. `spec/06-article.md` asserts Ranking line, JSON ranking_policy, JSON pubmed_rescue — ✓
13. `make check` passes — verified independently

### Test-Design Traceability

All 12 proof matrix entries have matching tests:

| Proof Matrix Entry | Test Location | Status |
|---|---|---|
| Per-source positions survive dedup | `article.rs::pubmed_led_rescue_preserves_per_source_positions_through_merge` | ✓ |
| mesh_synonym calibration flip | `article.rs::ranking_calibration::mesh_synonym_pubmed_rescue_surfaces_above_literal_competitor` | ✓ |
| anchor_count calibration flip | `article.rs::ranking_calibration::anchor_count_pubmed_rescue_surfaces_above_higher_title_hit_competitor` | ✓ |
| PubMed-led merged row rescues | `article.rs::ranking_calibration::pubmed_led_row_rescues_when_pubmed_position_is_strictly_best` | ✓ |
| Shared-source tie does not rescue | `article.rs::ranking_calibration::shared_source_tie_does_not_count_as_pubmed_led` | ✓ |
| Trailing PubMed does not rescue | `article.rs::ranking_calibration::shared_source_row_with_better_non_pubmed_position_does_not_rescue` | ✓ |
| PubMed position > 0 does not rescue | `article.rs::ranking_calibration::pubmed_nonfirst_position_does_not_rescue` | ✓ |
| Rescue metadata kind and position | `article.rs::ranking_calibration::rescue_metadata_records_kind_and_position` | ✓ |
| Rescue composes with lexical label | `markdown.rs::article_ranking_why_rescue_composes_with_lexical_reason` | ✓ |
| Markdown ranking policy updated | `markdown.rs::article_search_markdown_preserves_rank_order_and_shows_rationale` + spec | ✓ |
| JSON ranking policy and pubmed_rescue | `cli/mod.rs::article_search_json_includes_query_and_ranking_context` + spec | ✓ |
| Full repo gate green | `make check` | ✓ |

### Quality Assessment

- **Security**: No untrusted input flows into file paths, shell commands, or queries. All changes are internal ranking logic.
- **Duplication**: `ARTICLE_RELEVANCE_RANKING_POLICY` constant properly shared. No reinvented utilities.
- **Performance**: Rescue metadata computation is O(k) per row where k = source count (small constant). No regressions.
- **Implementation conventions**: Follows existing patterns in `article.rs` (private helpers, sort chains, `ensure_matched_sources` guards).
- **Serde compatibility**: `#[serde(default)]` on `pubmed_rescue`, `skip_serializing_if = "Option::is_none"` on optional fields — backward-compatible deserialization.

### Extra Coverage Beyond Proof Matrix

- `rescued_rows_still_use_lexical_and_citation_tiebreaks` — verifies that within the rescue group, the remaining sort chain (title hits, study/review cue, citations) still orders rows deterministically.

## Phase 2 — Fix Plan

No defects found. No fixes needed.

## Phase 3 — Repair

No fixes applied. Implementation is clean.

### Spec Coverage

- `spec/06-article.md` proves the updated ranking policy string and pubmed_rescue field in both markdown and JSON output modes.
- Unit tests cover all rescue eligibility edge cases specified by the design.

## Defect Register

| # | Category | Lintable | Description |
|---|----------|----------|-------------|
| — | — | — | None found |

## Residual Concerns

None. The implementation faithfully follows the design, all proof matrix tests exist and assert the right conditions, and the public surfaces (markdown, JSON, spec, architecture docs) are aligned.
