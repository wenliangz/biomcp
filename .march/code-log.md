# Code Log

## Commands Run

```bash
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
rg -n "variant_targets|enrich_targets|add_civic_section|section_sources|truncate\\(260\\)|protein.function|Targets \\(ChEMBL / Open Targets\\)|OPTIONAL_SAFETY_TIMEOUT|get drug <name> targets|rindopepimut|OPA1|EGFRvIII" -S src templates spec docs .march
cargo test gene_markdown_ -- --nocapture
cargo test variant_provenance_includes_gwas_when_requested_section_is_unavailable -- --nocapture
XDG_CACHE_HOME="$PWD/.cache" PATH="$PWD/target/release:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest spec/02-gene.md spec/05-drug.md spec/18-source-labels.md --mustmatch-lang bash --mustmatch-timeout 60 -v --deselect "spec/02-gene.md::Gene to Articles"'
cargo test normalize_variant_target_label_ -- --nocapture
cargo test extract_variant_targets_from_civic_deduplicates_and_filters_by_generic_target -- --nocapture
XDG_CACHE_HOME="$PWD/.cache" PATH="$PWD/target/release:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/release:$PATH" pytest "spec/02-gene.md::Gene Protein Function Full Text (line 172) [bash]" "spec/05-drug.md::Drug Variant Targets (line 216) [bash]" "spec/05-drug.md::Drug Variant Targets (line 222) [bash]" "spec/18-source-labels.md::Markdown Source Labels (line 16) [bash]" "spec/18-source-labels.md::JSON section_sources — Gene, Drug, Disease (line 48) [bash]" --mustmatch-lang bash --mustmatch-timeout 60 -v'
cargo fmt
./tools/check-quality-ratchet.sh
make check < /dev/null > .march/make-check.log 2>&1
git diff --stat
git status --short
```

## What Changed

- Removed the template-only truncation from the gene protein section so `get gene <symbol> protein` now renders the full UniProt function text.
- Added additive `variant_targets` support to `Drug` instead of mutating the existing generic `targets` and `mechanisms` contracts.
- Reused one shared CIViC therapy fetch in the drug section population path so `targets` and explicit `civic` can share the same context.
- Added CIViC variant-target extraction and normalization rules, including the required `EGFR VIII` / `EGFRVIII` -> `EGFRvIII` normalization.
- Updated markdown rendering and provenance so variant-specific targets appear as `Variant Targets (CIViC): ...` and `_meta.section_sources` gets a truthful `variant_targets` entry.
- Updated operator-facing docs and `biomcp list drug` to describe the mixed-source drug target workflow accurately.
- Documented the disease-gap disposition by following the approved design: no disease extraction code was changed for this ticket.

## Proof Added

- Unit: `cargo test gene_markdown_preserves_full_protein_function_text -- --nocapture`
- Unit: `cargo test drug_markdown_renders_variant_targets_as_additive_line -- --nocapture`
- Unit: `cargo test normalize_variant_target_label_ -- --nocapture`
- Unit: `cargo test extract_variant_targets_from_civic_deduplicates_and_filters_by_generic_target -- --nocapture`
- Unit: `cargo test drug_provenance_emits_variant_targets_when_present -- --nocapture`
- Spec: `Gene Protein Function Full Text`
- Spec: `Drug Variant Targets`
- Spec: `Markdown Source Labels`
- Spec: `JSON section_sources — Gene, Drug, Disease`

## Verification Results

- Focused Rust tests for the new gene, drug, and provenance behavior passed.
- Targeted executable markdown specs for OPA1 full-text protein output, rindopepimut variant targets, and variant-target provenance passed with the worktree binary.
- `./tools/check-quality-ratchet.sh` passed after fixing one short `mustmatch like` literal in `spec/18-source-labels.md`.
- `make check < /dev/null 2>&1` passed; captured log: `.march/make-check.log`.

## Deviations From Design

- No implementation deviations.
- For live spec verification, the targeted rerun used `BIOMCP_BIN="$PWD/target/debug/biomcp"` after the worktree binary was rebuilt locally; the repo-wide gate still passed through `make check`.
