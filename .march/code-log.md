# Code Log

## Commands Run

```bash
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
sed -n '1,220p' docs/user-guide/disease.md
sed -n '1,220p' src/entities/disease.rs
sed -n '1,220p' src/transform/disease.rs
sed -n '1240,1415p' src/entities/disease.rs
sed -n '380,520p' src/render/markdown.rs
sed -n '2178,2248p' src/render/markdown.rs
sed -n '1,220p' templates/disease.md.j2
sed -n '1,220p' spec/07-disease.md
rg -n "key_features|DiseasePhenotype|apply_requested_sections|from_mydisease_hit|disease_markdown|disease.md.j2|Sparse Phenotype Coverage Notes|MONDO:0008222|MONDO:0100605|MONDO:0017799" src templates spec docs -S
cargo test disease_markdown_preserves_full_definition_text -- --nocapture
cargo test from_mydisease_hit_collects_hpo_phenotypes -- --nocapture
PATH="$(pwd)/target/debug:$PATH" uv run --extra dev pytest spec/07-disease.md --mustmatch-lang bash --mustmatch-timeout 60 -k "Sparse and Phenotype and Coverage and Notes"
cargo test disease_markdown -- --nocapture
cargo test extract_definition_key_features_ -- --nocapture
cargo test disease_markdown_phenotypes_section_ -- --nocapture
cargo build
./target/debug/biomcp get disease MONDO:0008222 phenotypes
./target/debug/biomcp --json get disease MONDO:0008222 phenotypes
cargo fmt
cargo test extract_definition_key_features_ -- --nocapture
cargo test derive_key_features_ -- --nocapture
cargo test disease_markdown_phenotypes_section_ -- --nocapture
cargo test disease_markdown_preserves_full_definition_text -- --nocapture
BIOMCP_BIN="$(pwd)/target/debug/biomcp" uv run --extra dev pytest spec/07-disease.md --mustmatch-lang bash --mustmatch-timeout 60 -k "Sparse and Phenotype and Coverage and Notes or Disease and Phenotype and Key and Features"
git add docs/user-guide/disease.md spec/07-disease.md src/cli/mod.rs src/entities/disease.rs src/render/markdown.rs src/sources/disgenet.rs src/transform/disease.rs templates/disease.md.j2
git commit -m "Add disease key feature summaries"
make check < /dev/null > /tmp/081-make-check.log 2>&1
tail -n 40 /tmp/081-make-check.log
git status --short
```

## What Changed

- Added `key_features` to `Disease` and exposed it in JSON, with empty values omitted.
- Implemented conservative definition-first feature extraction in `src/transform/disease.rs` using cue phrases such as `characterized by`, `defined by`, `triad of`, and `association of`.
- Added phenotype frequency supplementation for high-signal qualifiers (`obligate`, `very frequent`, `frequent`) when the definition yields too few features.
- Recomputed `key_features` after disease section enrichment so phenotype qualifiers from Monarch can supplement the summary when present.
- Updated phenotype markdown rendering to show `### Key Features` above the existing completeness note, or a definition hint when `key_features` is empty but a definition exists.
- Extended disease specs and renderer/transform unit tests for the new summary behavior and JSON contract.
- Updated the disease user guide to document the difference between `key_features` and the comprehensive phenotype table.

## Proof Added

- Unit: `cargo test extract_definition_key_features_ -- --nocapture`
- Unit: `cargo test derive_key_features_ -- --nocapture`
- Unit: `cargo test disease_markdown_phenotypes_section_ -- --nocapture`
- Regression: `cargo test disease_markdown_preserves_full_definition_text -- --nocapture`
- Spec: `BIOMCP_BIN="$(pwd)/target/debug/biomcp" uv run --extra dev pytest spec/07-disease.md --mustmatch-lang bash --mustmatch-timeout 60 -k "Sparse and Phenotype and Coverage and Notes or Disease and Phenotype and Key and Features"`

## Verification Results

- Focused transform and renderer tests passed after implementation.
- Live Andersen-Tawil phenotype output from `./target/debug/biomcp get disease MONDO:0008222 phenotypes` rendered `### Key Features` before the HPO table.
- Live JSON output from `./target/debug/biomcp --json get disease MONDO:0008222 phenotypes` included a populated `key_features` array.
- `make check < /dev/null 2>&1` passed; captured log: `/tmp/081-make-check.log`.
- The source commit for the code change is `36e6f92` (`Add disease key feature summaries`).

## Deviations From Design

- No implementation deviations.
- The new spec sections use the existing `BIOMCP_BIN` override pattern so executable markdown specs can target the locally built worktree binary deterministically.
