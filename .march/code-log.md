# Code Log

## Commands Run

```bash
checkpoint status
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,220p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
sed -n '1,260p' .march/ticket.md
rg -n "top-mutated|MutationFrequencyResult|read_limited_body_with_limit|MONDO:0100605|phenotype|Saved to:|fulltext" src spec templates Cargo.toml
cargo test -- --list
cargo test --no-run
cargo test sources::pmc_oa::tests::get_full_text_xml_accepts_archive_larger_than_default_body_limit -- --exact
cargo test entities::study::tests::top_mutated_genes_reports_ranked_rows -- --exact
cargo test render::markdown::tests::related_disease_uses_synonym_when_name_is_raw_id -- --exact
cargo test render::markdown::tests::study_top_mutated_markdown_renders_ranked_table -- --exact
cargo test cli::tests::study_top_mutated_parses_limit_flag -- --exact
XDG_CACHE_HOME="$PWD/.cache" PATH="$PWD/target/debug:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/debug:$PATH" pytest spec/13-study.md -k "(Environment and Setup) or (Top and Mutated and Genes)" --mustmatch-lang bash --mustmatch-timeout 60 -v'
XDG_CACHE_HOME="$PWD/.cache" PATH="$PWD/target/debug:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/debug:$PATH" pytest spec/07-disease.md spec/13-study.md -k "(Sparse and Phenotype and Coverage and Notes) or (Top and Mutated and Genes)" --mustmatch-lang bash --mustmatch-timeout 60 -v'
XDG_CACHE_HOME="$PWD/.cache" PATH="$PWD/target/debug:$PATH" uv run --extra dev sh -c 'PATH="$PWD/target/debug:$PATH" pytest spec/06-article.md -k "Large and Article and Full and Text and Saved and Markdown" --mustmatch-lang bash --mustmatch-timeout 120 -v'
cargo fmt
make check < /dev/null > .cache/make-check.log 2>&1
git add Makefile spec/06-article.md src/sources/pmc_oa.rs
git commit -m "Fix large PMC OA fulltext downloads"
git add spec/07-disease.md spec/13-study.md src/cli/list.rs src/cli/list_reference.md src/cli/mod.rs src/entities/study.rs src/render/markdown.rs src/sources/cbioportal_study.rs templates/disease.md.j2
git commit -m "Add study top-mutated and disease literature fallback"
git status --short
git log --oneline -2
```

## What Changed

- Gap 1: increased the PMC OA archive download ceiling in `src/sources/pmc_oa.rs` to reuse the existing `MAX_TGZ_BYTES` limit at the HTTP body read boundary, and added a source test plus a live spec for large fulltext retrieval.
- Gap 2: changed disease phenotype follow-up guidance to use a human-searchable literature term derived from disease name or first synonym instead of echoing a raw ontology ID; updated markdown rendering, template output, and the disease spec.
- Gap 3: added `biomcp study top-mutated --study <id> [--limit <n>]` end to end across CLI parsing, source aggregation, entity serialization, markdown rendering, docs, tests, and fixture-backed spec coverage.
- Operator-facing docs/scripts updated: `src/cli/list.rs`, `src/cli/list_reference.md`, and `Makefile` (to keep the new live fulltext spec out of the PR-blocking spec lane like the existing fulltext heading).

## Tests and Proofs Added/Updated

- Added `sources::pmc_oa::tests::get_full_text_xml_accepts_archive_larger_than_default_body_limit`
- Added `entities::study::tests::top_mutated_genes_reports_ranked_rows`
- Added `sources::cbioportal_study::tests::top_mutated_genes_ranks_by_samples_then_events_then_gene`
- Added `render::markdown::tests::related_disease_uses_synonym_when_name_is_raw_id`
- Added `render::markdown::tests::study_top_mutated_markdown_renders_ranked_table`
- Added `cli::tests::study_top_mutated_parses_limit_flag`
- Added spec heading `Large Article Full Text Saved Markdown`
- Updated spec heading `Sparse Phenotype Coverage Notes`
- Added spec heading `Top Mutated Genes`

## Verification Results

- `cargo test --no-run`: passed
- Focused Rust tests for PMC OA, disease render fallback, study aggregation/rendering, and CLI parsing: passed
- `pytest spec/13-study.md -k "(Environment and Setup) or (Top and Mutated and Genes)" ...`: passed
- `pytest spec/06-article.md -k "Large and Article and Full and Text and Saved and Markdown" ...`: passed
- `make check < /dev/null > .cache/make-check.log 2>&1`: passed

## Deviations From Design

- None from `design-final.md`.
- The original ticket text proposed a preview-plus-path fulltext response, but implementation followed the approved final design instead: preserve the existing `Saved to:` contract and fix the PMC OA body-limit mismatch.
