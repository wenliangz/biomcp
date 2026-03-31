# Code Log — Ticket 089

## Commands Run

```text
checkpoint status
git status --short
GIT_EDITOR=true git rebase main
git diff --stat main..HEAD | tail -1
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md
uv run --extra dev pytest -q tests/test_public_skill_docs_contract.py
cargo test -q query_sets_fields_and_size -- --nocapture
cargo test -q normalize_disease_id_basic -- --nocapture
cargo test -q planner_rejects_pubtator_with_unsupported_strict_filters -- --nocapture
cargo fmt
cargo test -q lookup_disease_by_xref_queries_exact_mesh_fields -- --nocapture
cargo test -q parse_disease_lookup_input_distinguishes_canonical_crosswalk_and_text -- --nocapture
cargo test -q preferred_crosswalk_hit_prefers_mondo_then_doid_then_lexicographic_id -- --nocapture
cargo test -q article_type_limitation_note_is_emitted_for_all_and_europepmc -- --nocapture
cargo test -q article_search_json_includes_query_and_ranking_context -- --nocapture
cargo test -q article_search_markdown_preserves_rank_order_and_shows_rationale -- --nocapture
cargo test -q build_article_debug_plan_includes_article_type_limitation_note -- --nocapture
cargo build --locked
XDG_CACHE_HOME="$PWD/.cache" uv run --extra dev sh -c 'PATH="$PWD/target/debug:$PATH" pytest spec/06-article.md -k "Type and Filter and Warns and Restriction" --mustmatch-lang bash --mustmatch-timeout 60 -v'
XDG_CACHE_HOME="$PWD/.cache" uv run --extra dev sh -c 'PATH="$PWD/target/debug:$PATH" pytest spec/07-disease.md -k "Disease and Crosswalk and Identifier and Resolution" --mustmatch-lang bash --mustmatch-timeout 60 -v'
XDG_CACHE_HOME="$PWD/.cache" uv run --extra dev sh -c 'PATH="$PWD/target/debug:$PATH" pytest spec/06-article.md -k "Article and Debug and Plan" --mustmatch-lang bash --mustmatch-timeout 60 -v'
make check < /dev/null > .march/make-check.log 2>&1
git diff --stat
rm -f .march/make-check.log
```

## What Changed

- Taught the embedded BioMCP skill and article docs to prefer `article batch`, use `batch gene`, resolve weak disease names through `discover`, and treat `--type` as Europe-PMC-only when recall matters.
- Added MyDisease xref lookup support for `MESH:`, `OMIM:`, and `ICD10CM:` disease inputs, with deterministic MONDO/DOID preference before the existing disease-card flow runs.
- Expanded MyDisease free-text disease search to include synonym fields.
- Added an article-search limitation note for `--type` and threaded it through markdown, JSON, and debug-plan output while keeping strict Europe PMC routing unchanged.
- Refreshed article and disease specs plus the public skill/doc contract test to cover the new behavior.

## Tests / Proof

- `uv run --extra dev pytest -q tests/test_public_skill_docs_contract.py`
- `cargo test -q lookup_disease_by_xref_queries_exact_mesh_fields -- --nocapture`
- `cargo test -q parse_disease_lookup_input_distinguishes_canonical_crosswalk_and_text -- --nocapture`
- `cargo test -q preferred_crosswalk_hit_prefers_mondo_then_doid_then_lexicographic_id -- --nocapture`
- `cargo test -q article_type_limitation_note_is_emitted_for_all_and_europepmc -- --nocapture`
- `cargo test -q article_search_json_includes_query_and_ranking_context -- --nocapture`
- `cargo test -q article_search_markdown_preserves_rank_order_and_shows_rationale -- --nocapture`
- `cargo test -q build_article_debug_plan_includes_article_type_limitation_note -- --nocapture`
- `XDG_CACHE_HOME="$PWD/.cache" uv run --extra dev sh -c 'PATH="$PWD/target/debug:$PATH" pytest spec/06-article.md -k "Type and Filter and Warns and Restriction" --mustmatch-lang bash --mustmatch-timeout 60 -v'`
- `XDG_CACHE_HOME="$PWD/.cache" uv run --extra dev sh -c 'PATH="$PWD/target/debug:$PATH" pytest spec/07-disease.md -k "Disease and Crosswalk and Identifier and Resolution" --mustmatch-lang bash --mustmatch-timeout 60 -v'`
- `XDG_CACHE_HOME="$PWD/.cache" uv run --extra dev sh -c 'PATH="$PWD/target/debug:$PATH" pytest spec/06-article.md -k "Article and Debug and Plan" --mustmatch-lang bash --mustmatch-timeout 60 -v'`
- `make check < /dev/null > .march/make-check.log 2>&1`

## Deviations

- The out-of-repo eval-project follow-up from the design is not implemented here: `users-guide-skill.md` still needs the mirrored skill wording in that separate repo.
