# Code Log

## Commands Run

```text
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md
rg -n "fetch_protein_section|GeneProtein|protein_isoforms|function_summary|ALTERNATIVE PRODUCTS|ALTERNATIVE_PRODUCTS" src/sources/uniprot.rs src/entities/gene.rs src/render/markdown.rs templates/gene.md.j2 spec/02-gene.md
sed -n '1,260p' src/sources/uniprot.rs
sed -n '1,260p' src/entities/gene.rs
sed -n '1650,1760p' src/render/markdown.rs
sed -n '1,220p' templates/gene.md.j2
sed -n '1,260p' spec/02-gene.md
sed -n '539,700p' src/sources/uniprot.rs
sed -n '1464,1585p' src/entities/gene.rs
cargo test record_helpers_extract_display_function_and_structures -- --nocapture
cargo test gene_markdown_includes_evidence_links -- --nocapture
cargo test markdown_detail_outputs_label_gene_drug_and_disease_sources -- --nocapture
cargo test related_gene_prioritizes_localization_deepening_when_supported -- --nocapture
curl -fsS https://rest.uniprot.org/uniprotkb/P01116.json | jq -r '.primaryAccession, (.comments[]? | select(.commentType=="ALTERNATIVE PRODUCTS") | .isoforms | length)'
sed -n '1,220p' docs/user-guide/gene.md
sed -n '1,140p' docs/sources/uniprot.md
cargo test protein_isoforms_prefer_synonyms_and_track_displayed_status -- --nocapture
cargo test gene_markdown_renders_protein_isoforms_with_count_and_displayed_length -- --nocapture
rg -n "GeneProtein \{" src
sed -n '1,220p' src/transform/protein.rs
cargo fmt
cargo build
PATH="$(pwd)/target/debug:$PATH" biomcp get gene KRAS protein | sed -n '1,40p'
BIOMCP_BIN="$(pwd)/target/debug/biomcp" uv run --extra dev pytest spec/02-gene.md --mustmatch-lang bash --mustmatch-timeout 60 -v -k Isoforms
make check < /dev/null > "$tmp_log" 2>&1
bash tools/check-quality-ratchet.sh
cat .march/reality-check/quality-ratchet-summary.json
git diff --stat
git diff -- src/sources/uniprot.rs src/entities/gene.rs templates/gene.md.j2
git diff -- src/render/markdown.rs spec/02-gene.md docs/user-guide/gene.md docs/sources/uniprot.md src/transform/protein.rs
```

## What Changed

- Extended `src/sources/uniprot.rs` to deserialize UniProt `ALTERNATIVE PRODUCTS` isoforms and added `UniProtRecord::protein_isoforms()` to derive display labels plus displayed-status from the existing record fetch.
- Extended `src/entities/gene.rs` with `GeneProteinIsoform` and surfaced `protein.isoforms` in the gene protein section without adding extra UniProt requests.
- Updated `templates/gene.md.j2` to render `- Isoforms (N): ...` between the existing Length and Function lines.
- Added unit coverage in `src/sources/uniprot.rs` and `src/render/markdown.rs`.
- Added CLI spec coverage in `spec/02-gene.md` for KRAS, TP73, BRAF, and JSON output.
- Updated `docs/user-guide/gene.md` and `docs/sources/uniprot.md` to document the new protein-section behavior.
- Updated the direct `UniProtComment` fixture in `src/transform/protein.rs` and existing `GeneProtein` fixtures in `src/render/markdown.rs` to match the new contract.

## Proof Added Or Updated

- Red proof:
  `cargo test protein_isoforms_prefer_synonyms_and_track_displayed_status -- --nocapture`
  `cargo test gene_markdown_renders_protein_isoforms_with_count_and_displayed_length -- --nocapture`
- Green proof:
  `cargo test protein_isoforms_prefer_synonyms_and_track_displayed_status -- --nocapture`
  `cargo test gene_markdown_renders_protein_isoforms_with_count_and_displayed_length -- --nocapture`
  `cargo test markdown_detail_outputs_label_gene_drug_and_disease_sources -- --nocapture`
  `BIOMCP_BIN="$(pwd)/target/debug/biomcp" uv run --extra dev pytest spec/02-gene.md --mustmatch-lang bash --mustmatch-timeout 60 -v -k Isoforms`
  `make check < /dev/null > "$tmp_log" 2>&1`

## Results

- The new red proofs initially failed because `GeneProtein.isoforms`, `GeneProteinIsoform`, and the UniProt isoform helper did not exist.
- After implementation, the new unit tests and the targeted spec slice passed.
- `make check` passed after tightening three new spec literals to satisfy the quality-ratchet minimum-length rule.

## Deviations From Design

- None in behavior.
- The spec examples use the existing `BIOMCP_BIN` override pattern so the targeted spec run can pin the local binary explicitly.
