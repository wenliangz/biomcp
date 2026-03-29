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
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/cli-design/SKILL.md
rg -n "related_gene\\(|related_disease\\(|related_command_description\\(|next_commands_validity|cross-entity-see-also|evidence-urls" src spec
sed -n '10377,10760p' src/cli/mod.rs
sed -n '1054,1455p' src/render/markdown.rs
sed -n '5180,5515p' src/render/markdown.rs
sed -n '1,240p' spec/21-cross-entity-see-also.md
sed -n '1,120p' spec/11-evidence-urls.md
sed -n '1,260p' Makefile
cargo build --release --locked
cargo test related_gene_prioritizes_localization_deepening_when_supported -- --nocapture
cargo test related_disease_suggests_review_when_phenotypes_are_sparse -- --nocapture
cargo test gene_next_commands_parse -- --nocapture
cargo test disease_next_commands_parse -- --nocapture
PATH="$PWD/target/release:$PATH" biomcp get gene TP53
PATH="$PWD/target/release:$PATH" biomcp search pgx -g TP53 --limit 3
PATH="$PWD/target/release:$PATH" biomcp search drug --indication melanoma --limit 5
uv run --extra dev pytest spec/21-cross-entity-see-also.md --collect-only -q
uv run --extra dev pytest spec/21-cross-entity-see-also.md --mustmatch-lang bash --mustmatch-timeout 60 -v
uv run --extra dev pytest spec/11-evidence-urls.md --mustmatch-lang bash --mustmatch-timeout 60 -v
cargo test gene_json_next_commands_parse -- --nocapture
cargo test disease_json_next_commands_parse -- --nocapture
cargo run --bin biomcp -- get gene TP53
cargo run --bin biomcp -- get disease melanoma
make check < /dev/null 2>&1
make spec-pr
git status --short
git status --short --untracked-files=all
git diff -- src/render/markdown.rs
git add -A
git diff --cached
git commit -m "Fix gene and disease see-also pivots"
```

## What Changed

- Updated `src/render/markdown.rs` so gene cards emit `biomcp search pgx -g <symbol>` instead of `biomcp get pgx <symbol>`.
- Updated `src/render/markdown.rs` so disease cards emit `biomcp search drug --indication <disease>` instead of positional `biomcp search drug <disease>`.
- Extended `related_command_description()` to describe `search pgx -g` as `pharmacogenomics interactions` and `search drug --indication` as `treatment options for this condition`.
- Updated Rust proof coverage in `src/render/markdown.rs` and `src/cli/mod.rs` for the repaired command shapes.
- Updated operator-facing specs in `spec/21-cross-entity-see-also.md` and `spec/11-evidence-urls.md` to match the approved See-also contract and to prove graceful empty-state / indication-oriented behavior.

## Proof Added Or Updated

- `src/render/markdown.rs`
  - `related_gene_prioritizes_localization_deepening_when_supported`
  - `related_disease_suggests_review_when_phenotypes_are_sparse`
- `src/cli/mod.rs`
  - `next_commands_validity::gene_next_commands_parse`
  - `next_commands_validity::disease_next_commands_parse`
- `spec/21-cross-entity-see-also.md`
  - Gene to PGx now proves `search pgx -g` output, JSON alignment, graceful empty state, and absence of stale BRAF `get pgx`.
  - Disease to Drug now proves `search drug --indication`, JSON alignment, treatment-oriented results, and absence of stale positional search.
- `spec/11-evidence-urls.md`
  - Representative gene evidence card now expects the repaired `search pgx -g BRAF` See-also command.

## Verification

- `cargo test related_gene_prioritizes_localization_deepening_when_supported -- --nocapture` passed.
- `cargo test related_disease_suggests_review_when_phenotypes_are_sparse -- --nocapture` passed.
- `cargo test gene_next_commands_parse -- --nocapture` passed.
- `cargo test disease_next_commands_parse -- --nocapture` passed.
- `cargo test gene_json_next_commands_parse -- --nocapture` passed.
- `cargo test disease_json_next_commands_parse -- --nocapture` passed.
- `make check < /dev/null 2>&1` passed.
- `make spec-pr` passed.

## Deviations From Design

- Kept the existing `biomcp get pgx ` description mapping in `related_command_description()` even though gene cards no longer emit it, matching the approved final design and avoiding unrelated cleanup.
- The spec harness does not support `mustmatch unlike`, so the negative assertions use `grep -F ... >/dev/null` with explicit failure messages instead.
