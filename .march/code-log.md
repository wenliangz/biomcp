# Code Log

## Commands Run

```bash
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md
rg -n "legacy_name|ClinVar Name|Legacy Name|from_myvariant_hit|from_myvariant_search_hit|pick_hgvsp|normalize.*protein|search variant -g PLN|get variant" src templates spec Cargo.toml
cargo test transform::variant -- --nocapture
cargo test render::markdown -- --nocapture
cargo run --quiet --bin biomcp -- search variant -g BRAF --limit 1
cargo test transform::variant -- --nocapture   # red after proof update
cargo test render::markdown::tests::variant_search_markdown_renders_legacy_name_column_and_fallback -- --nocapture   # red after proof update
cargo test transform::variant -- --nocapture
cargo test render::markdown -- --nocapture
cargo test render::provenance::tests::variant_provenance_includes_gwas_when_requested_section_is_unavailable -- --nocapture
cargo run --quiet --bin biomcp -- search variant -g PLN --hgvsp L39X --limit 3
cargo run --quiet --bin biomcp -- search variant -g PLN --hgvsp R25C --limit 3
cargo run --quiet --bin biomcp -- get variant 'chr6:g.118880200T>G'
cargo run --quiet --bin biomcp -- --json get variant 'chr6:g.118880200T>G'
cargo test resolve_variant_query_preserves_stop_x_for_hgvsp_flag -- --nocapture
cargo test resolve_variant_query_normalizes_long_form_hgvsp_flag -- --nocapture
make check < /dev/null > /tmp/biomcp-make-check-085.log 2>&1
git status --short
git diff --stat
rm -f G T
```

## What Changed

- Added optional `legacy_name` to `Variant` and `VariantSearchResult`, with JSON omission when absent.
- Extended protein normalization to treat `X` as a stop token.
- Added shared transform logic to derive compact legacy labels from existing `dbnsfp.hgvsp` aliases, gated on ClinVar-backed hits.
- Updated variant markdown/detail rendering to show `Legacy Name:` and variant search tables to show a `Legacy Name` column with `-` fallback.
- Added/updated unit and render tests for stop-gain and missense legacy labels plus non-ClinVar fallback behavior.
- Updated `spec/03-variant.md` to cover search/detail/JSON legacy-name behavior for PLN examples.
- Adjusted CLI `--hgvsp` search normalization so stop-gain filters are sent as `L39X` on the search path, matching live MyVariant behavior while keeping internal stop normalization for derivation.

## Proof / Tests

- Red proof:
  - `cargo test transform::variant -- --nocapture` failed because `legacy_name` did not exist on the variant entities yet.
  - `cargo test render::markdown::tests::variant_search_markdown_renders_legacy_name_column_and_fallback -- --nocapture` failed for the same missing-field reason.
- Green targeted tests:
  - `cargo test transform::variant -- --nocapture`
  - `cargo test render::markdown -- --nocapture`
  - `cargo test render::provenance::tests::variant_provenance_includes_gwas_when_requested_section_is_unavailable -- --nocapture`
  - `cargo test resolve_variant_query_preserves_stop_x_for_hgvsp_flag -- --nocapture`
  - `cargo test resolve_variant_query_normalizes_long_form_hgvsp_flag -- --nocapture`
- Live verification:
  - `cargo run --quiet --bin biomcp -- search variant -g PLN --hgvsp L39X --limit 3`
  - `cargo run --quiet --bin biomcp -- search variant -g PLN --hgvsp R25C --limit 3`
  - `cargo run --quiet --bin biomcp -- get variant 'chr6:g.118880200T>G'`
  - `cargo run --quiet --bin biomcp -- --json get variant 'chr6:g.118880200T>G'`
- Full verification:
  - `make check < /dev/null > /tmp/biomcp-make-check-085.log 2>&1` passed.

## Deviations From Design

- No contract deviation from the approved design.
- Implementation detail added during verification: search-path normalization now preserves `X` for stop-gain `--hgvsp` filters because live MyVariant search returned zero hits for `L39*` but matched the approved `L39X` workflow.
