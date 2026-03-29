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
rg -n "GeneProtein|Protein \\(UniProt\\)|alternative_names|isoforms|PLIN2|PLIN1" src templates spec
sed -n '1,120p' Makefile
cargo test protein_isoforms_prefer_synonyms_and_track_displayed_status
cargo test gene_markdown_renders_protein_isoforms_with_count_and_displayed_length
cargo test gene_markdown_without_isoforms_keeps_protein_lines_contiguous
sed -n '280,470p' src/sources/uniprot.rs
sed -n '60,120p' src/entities/gene.rs
sed -n '550,610p' src/entities/gene.rs
sed -n '60,90p' templates/gene.md.j2
sed -n '4370,5305p' src/render/markdown.rs
sed -n '640,790p' src/sources/uniprot.rs
sed -n '1,260p' src/transform/protein.rs
cargo test alternative_protein_names
cargo test gene_markdown_renders_protein_alternative_names
cargo test gene_markdown_omits_protein_alternative_names_when_absent
cargo build --release
uv run --extra dev pytest spec/02-gene.md --collect-only -q
cargo run --bin biomcp -- get gene PLIN2 protein
cargo run --bin biomcp -- get gene PLIN2 protein --json
BIOMCP_BIN="$PWD/target/debug/biomcp" uv run --extra dev sh -c 'BIOMCP_BIN="$PWD/target/debug/biomcp" pytest spec/02-gene.md -v --mustmatch-lang bash --mustmatch-timeout 60 -k "Gene and Protein and Alternative and Names"'
make check < /dev/null > /tmp/084-make-check.log 2>&1
sed -n '1,320p' /tmp/084-make-check.log
bash -x tools/check-quality-ratchet.sh
cat .march/reality-check/quality-ratchet-summary.json
cargo fmt
make check-quality-ratchet
rm -rf .cache .pytest_cache
```

## What Changed

- Extended UniProt deserialization in `src/sources/uniprot.rs` to parse `proteinDescription.alternativeNames` and `shortNames`, and added `UniProtRecord::alternative_protein_names()` with trim/dedup/source-order behavior.
- Extended `GeneProtein` in `src/entities/gene.rs` with `alternative_names` and populated it from the existing UniProt-backed `fetch_protein_section()` path.
- Rendered `- Also known as:` in `templates/gene.md.j2` when UniProt alternative protein names are present.
- Updated Rust fixture builders and added unit/render coverage in `src/sources/uniprot.rs`, `src/render/markdown.rs`, and `src/transform/protein.rs`.
- Added executable spec coverage for PLIN1/PLIN2 markdown and JSON behavior in `spec/02-gene.md`.

## Proof Added or Updated

- `sources::uniprot::tests::alternative_protein_names_flatten_short_and_full_names_in_source_order`
- `sources::uniprot::tests::alternative_protein_names_trim_deduplicate_and_skip_recommended_name`
- `sources::uniprot::tests::alternative_protein_names_return_empty_when_alternative_names_are_missing`
- `render::markdown::tests::gene_markdown_renders_protein_alternative_names`
- `render::markdown::tests::gene_markdown_omits_protein_alternative_names_when_absent`
- `spec/02-gene.md` heading `Gene Protein Alternative Names`

## Verification

- Focused Rust tests passed for the new UniProt helper and markdown rendering.
- Targeted executable spec passed against `target/debug/biomcp` for the new `Gene Protein Alternative Names` assertions.
- `make check` passed after fixing formatting and the quality-ratchet spec literal length rule.

## Deviations

- No behavioral deviation from the approved design.
- The spec assertion for `ADRP` was written as the longer stable substring `Adipophilin, ADRP` to satisfy the repo's quality-ratchet rule against very short `mustmatch like` literals.
