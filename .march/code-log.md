# Code Log: Ticket 074

## Commands Run

```bash
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,240p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
rg -n "fn related_(drug|gene|disease)|related_command_description|drug_search_markdown_with_region|disease_search_markdown_with_footer|empty_drug_indication_search_body" src templates spec
sed -n '1180,1705p' src/render/markdown.rs
sed -n '2000,3305p' src/render/markdown.rs
sed -n '1,240p' src/sources/cbioportal_study.rs
sed -n '1,220p' templates/disease_search.md.j2
sed -n '1,220p' templates/drug_search.md.j2
sed -n '4920,5215p' src/render/markdown.rs
sed -n '6460,6555p' src/render/markdown.rs
bash spec/fixtures/setup-study-spec-fixture.sh "$PWD"
cargo test -q related_ -- --nocapture
cargo test -q drug_search_ -- --nocapture
cargo test -q format_sections_block_keeps_gene_ontology_in_top_more_entries -- --nocapture
cargo test -q discover_try_line_quotes_shell_sensitive_queries -- --nocapture
cargo test -q list_study_lookup_rows_includes_clinical_cancer_labels -- --nocapture
cargo fmt --all
cargo build --quiet
./target/debug/biomcp get gene TP53
./target/debug/biomcp get drug warfarin
./target/debug/biomcp search disease definitelynotarealdisease --limit 3
./target/debug/biomcp search drug definitelynotarealdrugname --region us --limit 3
./target/debug/biomcp get disease "breast cancer" genes
BIOMCP_STUDY_DIR="$(mktemp -d)" ./target/debug/biomcp get disease melanoma genes
git add src/render/markdown.rs src/sources/cbioportal_study.rs templates/disease_search.md.j2 templates/drug_search.md.j2 spec/21-cross-entity-see-also.md
git commit -m "Add cross-entity see-also links"
make check < /dev/null 2>&1
git status --short --branch
git show --stat --oneline --no-patch HEAD
cargo test render::markdown::tests::related_disease_oncology_with_local_match_prefers_top_mutated --lib -- --exact --nocapture
make check < /dev/null 2>&1
git status --short
git diff --cached --stat
```

## What Changed

- Added cross-entity follow-up commands in `src/render/markdown.rs`:
  - `get drug` now suggests `search pgx -d ...`
  - `get gene` now suggests `get pgx ...`
  - oncology `get disease ...` now suggests either a locally matched `study top-mutated --study ...` command or `study download --list`
- Added executable-command descriptions for the new see-also entries.
- Added shell-safe `discover` hint generation and threaded it through disease/drug zero-result search output, including EU/all-region and indication-specific drug empty states.
- Added local study lookup support in `src/sources/cbioportal_study.rs` so render logic can match oncology diseases to locally installed studies using metadata plus clinical sample cancer labels.
- Added focused user-facing spec coverage in `spec/21-cross-entity-see-also.md`.
- Added unit coverage for:
  - drug/gene PGx follow-ups
  - oncology study matching and fallback
  - zero-result discover hints
  - gene `More:` ordering keeping `ontology` in the top trio
  - study lookup rows including clinical cancer labels

## Proof Added or Updated

- `spec/21-cross-entity-see-also.md`
- `src/render/markdown.rs` unit tests for new related-command and empty-state behavior
- `src/sources/cbioportal_study.rs` unit test for study lookup row extraction

## Verification Results

- `cargo test -q related_ -- --nocapture` passed
- `cargo test -q drug_search_ -- --nocapture` passed
- `cargo test -q format_sections_block_keeps_gene_ontology_in_top_more_entries -- --nocapture` passed
- `cargo test -q discover_try_line_quotes_shell_sensitive_queries -- --nocapture` passed
- `cargo test -q list_study_lookup_rows_includes_clinical_cancer_labels -- --nocapture` passed
- `cargo build --quiet` passed
- Direct CLI spot checks showed:
  - `get gene TP53` includes `biomcp get pgx TP53`
  - `get drug warfarin` includes `biomcp search pgx -d warfarin`
  - `search disease definitelynotarealdisease` includes a `discover` hint
  - `search drug definitelynotarealdrugname --region us` includes a `discover` hint
  - `get disease "breast cancer" genes` includes `study top-mutated --study brca_tcga_pan_can_atlas_2018`
  - `get disease melanoma genes` with an empty `BIOMCP_STUDY_DIR` includes `study download --list`
- `make check < /dev/null 2>&1` passed
- Resume verification:
  - `cargo test render::markdown::tests::related_disease_oncology_with_local_match_prefers_top_mutated --lib -- --exact --nocapture` passed
  - `make check < /dev/null 2>&1` passed again on the resumed worktree

## Deviations From Design

- The implementation matches the approved design.
- The new spec uses `definitelynotarealdrugname` instead of `MK-3475` for the zero-result drug proof because current U.S. search returns a non-empty total for `MK-3475`, which makes it a brittle empty-state assertion even though the zero-result discover behavior itself is implemented.
