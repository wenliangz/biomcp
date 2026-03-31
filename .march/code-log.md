# Code Log — Ticket 090

## Commands Run

```text
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,320p' .march/design-final.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md
rg -n "add_genes_section|augment_genes_with_civic|attach_opentargets_scores|resolve_disease_id|Associated Genes" src spec docs
cargo test -q augment_genes_with_opentargets_merges_sources_without_duplicates -- --nocapture
cargo test -q augment_genes_with_opentargets_respects_twenty_gene_cap -- --nocapture
cargo test -q enrich_sparse_disease_identity_prefers_exact_ols4_match -- --nocapture
cargo test -q disease_associated_targets_prefers_efo_hit_when_search_returns_mondo_first -- --nocapture
cargo test -q disease_markdown_renders_ot_only_gene_association_table -- --nocapture
cargo test -q get_disease_genes_promotes_opentargets_rows_for_cll -- --nocapture
cargo test -q get_disease_genes_uses_ols4_label_fallback_for_sparse_mondo_identity -- --nocapture
cargo fmt --all
cargo build --locked
./target/debug/biomcp get disease MONDO:0003864 genes
./target/debug/biomcp get disease MONDO:0019468 genes
./target/debug/biomcp get disease MONDO:0005180 genes
./target/debug/biomcp get disease MONDO:0007309 genes
rm -rf .cache .pytest_cache
XDG_CACHE_HOME="$PWD/.cache" BIOMCP_BIN="$PWD/target/debug/biomcp" uv run --extra dev pytest spec/07-disease.md --mustmatch-lang bash --mustmatch-timeout 60 -v
bash tools/check-quality-ratchet.sh
make check < /dev/null 2>&1
git status --short
git add src/entities/disease.rs src/sources/opentargets.rs src/render/markdown.rs src/cli/list.rs docs/user-guide/disease.md docs/sources/opentargets.md docs/reference/data-sources.md spec/07-disease.md .march/code-log.md
git diff --cached --stat
git diff --cached
git commit -m "Fix disease gene enrichment for cancer MONDO IDs"
git commit -m "Document repaired disease gene contract"
```

## What Changed

- Repaired sparse canonical disease lookups by backfilling MONDO disease labels and synonyms from OLS4 before disease-section enrichment runs.
- Expanded disease-gene enrichment so OpenTargets results augment, rather than replace, Monarch and CIViC gene rows, with source merging and a 20-row cap that matches the approved design.
- Tightened OpenTargets disease resolution to prefer disease-class `EFO_...` hits when a MONDO search alias would otherwise select a poorer match for cancer terms.
- Added proof coverage for canonical CLL and T-PLL disease-gene output, OT-only markdown rendering, source merging, row caps, and OLS4 sparse-label fallback.
- Updated operator-facing docs and disease specs to describe the repaired canonical disease-gene contract and the expected OpenTargets provenance.

## Tests / Proof

- `cargo test -q augment_genes_with_opentargets_merges_sources_without_duplicates -- --nocapture`
- `cargo test -q augment_genes_with_opentargets_respects_twenty_gene_cap -- --nocapture`
- `cargo test -q enrich_sparse_disease_identity_prefers_exact_ols4_match -- --nocapture`
- `cargo test -q disease_associated_targets_prefers_efo_hit_when_search_returns_mondo_first -- --nocapture`
- `cargo test -q disease_markdown_renders_ot_only_gene_association_table -- --nocapture`
- `cargo test -q get_disease_genes_promotes_opentargets_rows_for_cll -- --nocapture`
- `cargo test -q get_disease_genes_uses_ols4_label_fallback_for_sparse_mondo_identity -- --nocapture`
- `XDG_CACHE_HOME="$PWD/.cache" BIOMCP_BIN="$PWD/target/debug/biomcp" uv run --extra dev pytest spec/07-disease.md --mustmatch-lang bash --mustmatch-timeout 60 -v`
- `bash tools/check-quality-ratchet.sh`
- `make check < /dev/null 2>&1`

## Deviations

- The disease spec examples use longer row-level `mustmatch like` patterns instead of bare gene symbols so they satisfy the repo's quality-ratchet rules while proving the same user-visible contract.
