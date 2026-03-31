# Code Log

## Commands Run

```bash
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,520p' .march/design-final.md
cargo test parse_disease_lookup_input_distinguishes_canonical_crosswalk_and_text -- --nocapture
cargo test preferred_crosswalk_hit_prefers_mondo_then_doid_then_lexicographic_id -- --nocapture
cargo test disease_search_empty_state_includes_discover_hint -- --nocapture
uv run --extra dev pytest 'spec/07-disease.md::Searching by Name (line 19) [bash]' 'spec/07-disease.md::Disease Crosswalk Identifier Resolution (line 41) [bash]' --mustmatch-lang bash --mustmatch-timeout 60 -v
uv run --extra dev pytest 'spec/19-discover.md::Gene Alias (line 24) [bash]' 'spec/19-discover.md::JSON Metadata (line 119) [bash]' --mustmatch-lang bash --mustmatch-timeout 60 -v
uv run --extra dev pytest 'spec/07-disease.md::Disease Search Discover Fallback (line 31) [bash]' 'spec/07-disease.md::Disease Search No Fallback (line 87) [bash]' --mustmatch-lang bash --mustmatch-timeout 60 -v
cargo test fallback_candidates_rank_specific_crosswalkable_disease_ahead_of_generic_rows -- --nocapture
cargo test fallback_candidate_source_ids_prefer_primary_then_ranked_xrefs -- --nocapture
cargo test disease_search_empty_state_uses_raw_query_in_discover_hint -- --nocapture
cargo test disease_search_fallback_renders_provenance_columns -- --nocapture
cargo test search_disease_parses_no_fallback_flag -- --nocapture
cargo test disease_search_json_includes_fallback_meta_and_provenance -- --nocapture
cargo test disease_search_json_omits_meta_for_direct_hits -- --nocapture
cargo run --quiet --bin biomcp -- search disease "Arnold Chiari syndrome"
cargo run --quiet --bin biomcp -- search disease "Arnold Chiari syndrome" --no-fallback
cargo run --quiet --bin biomcp -- discover "Arnold Chiari syndrome"
cargo run --quiet --bin biomcp -- discover "T-cell prolymphocytic leukemia"
cargo run --quiet --bin biomcp -- get disease MESH:D015461
cargo run --quiet --bin biomcp -- get disease ICD10CM:C91.60
cargo run --quiet --bin biomcp -- get disease ICD10CM:C91.6
cargo fmt
make check < /dev/null > .march/make-check.log 2>&1
BIOMCP_BIN=/home/ian/workspace/worktrees/091-fallback-to-discover-when-search-disease-returns-zero-results/target/debug/biomcp uv run --extra dev pytest 'spec/07-disease.md::Disease Search Discover Fallback (line 41) [bash]' 'spec/07-disease.md::Disease Search Discover Fallback Synonym (line 68) [bash]' 'spec/07-disease.md::Disease Search Discover Fallback for T-PLL (line 81) [bash]' 'spec/07-disease.md::Disease Search Fallback Miss (line 94) [bash]' 'spec/07-disease.md::Disease Search No Fallback (line 107) [bash]' --mustmatch-lang bash --mustmatch-timeout 60 -v
git status --short
git diff --stat
```

## What Changed

- Moved discover resolver ownership from `src/cli/discover.rs` into `src/entities/discover.rs` so disease search can reuse it without a CLI-layer dependency.
- Added disease zero-result fallback orchestration in `src/entities/disease.rs`:
  - rank discover disease candidates
  - normalize supported fallback IDs
  - resolve rows through MyDisease xref lookups
  - dedupe and paginate fallback rows
  - degrade cleanly back to the existing empty state on discover/xref failures
- Extended `DiseaseSearchResult` with optional `resolved_via` and `source_id` provenance fields.
- Added disease-specific JSON serialization in `src/cli/mod.rs` so fallback responses emit `_meta.fallback_used` while direct-hit responses keep the old shape.
- Added disease-only `--no-fallback` CLI parsing and disease-search wiring in `src/cli/mod.rs`.
- Updated disease markdown rendering and template branching to:
  - separate raw query from display summary
  - keep the discover hint free of `offset=...`
  - show provenance columns for fallback results
- Added/updated user-facing executable spec coverage in `spec/07-disease.md` for:
  - Arnold Chiari fallback
  - Chiari synonym fallback
  - T-PLL fallback
  - fallback miss
  - `--no-fallback`
- Added focused Rust tests for fallback ranking, renderer behavior, CLI parsing, and disease search JSON metadata.

## Proof / Verification

- `make check` passed after formatting.
- New targeted disease fallback spec slice passed against the current debug binary:
  - `Disease Search Discover Fallback`
  - `Disease Search Discover Fallback Synonym`
  - `Disease Search Discover Fallback for T-PLL`
  - `Disease Search Fallback Miss`
  - `Disease Search No Fallback`
- Focused Rust tests passed for:
  - fallback candidate ranking
  - fallback source-id normalization/order
  - raw-query discover hint rendering
  - fallback provenance markdown rendering
  - disease search JSON fallback metadata
  - disease search direct-hit JSON stability
  - `--no-fallback` CLI parsing

## Deviations From Design

- Live T-PLL discover results exposed a canonical `MONDO:0019468` disease ID but its `MESH`/`ICD10CM` xrefs did not resolve through `MyDisease` xref lookup. To satisfy the approved acceptance criteria, the fallback now also accepts discover-provided canonical `MONDO`/`DOID` IDs directly and marks those rows as `MONDO canonical` / `DOID canonical`.
- The markdown spec collector in this repo only executed the first bash block under a heading, so disease-search JSON fallback coverage was kept in Rust unit tests instead of additional executable markdown blocks.
