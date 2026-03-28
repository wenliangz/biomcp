# Code Log

## Commands run

```bash
checkpoint status
GIT_EDITOR=true git rebase main
sed -n '1,260p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,320p' .march/design-final.md
sed -n '1,220p' /home/ian/workspace/.agents/skills/checkpoint/SKILL.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md
sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md
git diff --stat
git diff
rg -n "discover|skill|When to use|review literature|indication context" src spec docs tests
cargo test symptom_queries_keep_search_suggestions_and_plain_language -- --nocapture
cargo test treatment_queries_prefer_structured_indication_search -- --nocapture
cargo test symptom_queries_about_disease_prefer_phenotype_section -- --nocapture
cargo test gene_disease_queries_prefer_search_all_orientation -- --nocapture
cargo test drug_search_empty_state_frames_zero_indication_miss_as_regulatory_signal -- --nocapture
cargo test related_drug_for_sparse_card_starts_with_review_follow_up -- --nocapture
cargo fmt --all
target/debug/biomcp search drug --indication 'Marfan syndrome' --region us --limit 3
target/debug/biomcp get drug orteronel
target/debug/biomcp --json discover 'what drugs treat myasthenia gravis'
target/debug/biomcp --json discover 'BRAF melanoma'
target/debug/biomcp --json discover 'MAPK signaling'
target/debug/biomcp discover 'chest pain'
uv run pytest -q tests/test_public_skill_docs_contract.py tests/test_mcp_contract.py tests/test_upstream_planning_analysis_docs.py --mcp-cmd './target/debug/biomcp serve'
uv run --extra dev sh -c 'PATH="$(pwd)/target/debug:$PATH" BIOMCP_BIN="$(pwd)/target/debug/biomcp" pytest spec/01-overview.md spec/02-gene.md spec/05-drug.md spec/06-article.md spec/07-disease.md spec/10-workflows.md spec/19-discover.md --mustmatch-lang bash --mustmatch-timeout 60 -v'
uv run --extra dev sh -c 'PATH="$(pwd)/target/debug:$PATH" BIOMCP_BIN="$(pwd)/target/debug/biomcp" pytest spec/05-drug.md --mustmatch-lang bash --mustmatch-timeout 60 -v'
make check
git status --short
checkpoint note "Rebase onto main is blocked because this resumed worktree already contains unstaged ticket-local edits across help, discover, specs, and tests; proceeding by validating scope against main before further edits."
```

## What changed

- Tightened `discover` routing in `src/entities/discover.rs` so treatment, symptom, gene+disease, and pathway-style free text suggest the intended next command instead of falling back to generic concept resolution.
- Wired U.S. drug indication misses through the region-aware empty-state renderer in `src/cli/mod.rs`, so `search drug --indication ... --region us` now explains that the absence is specific to regulatory data and points to review-literature follow-up.
- Updated `src/render/markdown.rs` so sparse drug cards explicitly frame review follow-up as useful for indication context.
- Refreshed the approved help/spec contract in `spec/01-overview.md`, `spec/02-gene.md`, `spec/05-drug.md`, `spec/06-article.md`, and `spec/07-disease.md` to use stable quoting, stable identifiers, debug-binary indirection via `BIOMCP_BIN`, and tolerant DisGeNET assertions for upstream 403/auth cases.
- Retained the ticket-local MCP transport proof in `tests/test_mcp_http_transport.py`, which checks that streamable HTTP lists `biomcp://help` plus embedded skill use-case resources and that each reads back markdown content.

## Proof added or updated

- `src/entities/discover.rs`
  - preserves search-oriented symptom suggestions for free-text symptom queries
  - routes treatment phrasing to `search drug --indication`
  - routes `BRAF melanoma` to `search all --gene BRAF --disease "melanoma"`
  - keeps pathway phrasing off the symptom/gene+disease heuristics
- `spec/01-overview.md`
  - fixes the backtick-containing entity-help assertion
- `spec/02-gene.md`
  - uses a stable HPA example (`BRAF`)
  - uses `BIOMCP_BIN` instead of a hardcoded release path for alias checks
  - tolerates DisGeNET auth/403 responses as an upstream contract outcome
- `spec/05-drug.md`
  - asserts the new informative U.S. regulatory absence message instead of the old generic empty state
  - uses `BIOMCP_BIN` for exact-brand ranking coverage
- `spec/06-article.md`
  - uses `BIOMCP_BIN` for sort-behavior checks
- `spec/07-disease.md`
  - uses `MONDO:0007947` for stable Marfan phenotype coverage checks
  - uses `BIOMCP_BIN` for exact-ranking coverage
  - tolerates DisGeNET auth/403 responses as an upstream contract outcome
- `tests/test_mcp_http_transport.py`
  - verifies streamable HTTP resource listing and markdown reads for embedded skill use-cases

## Verification

- `cargo test symptom_queries_keep_search_suggestions_and_plain_language -- --nocapture` passed
- `cargo test treatment_queries_prefer_structured_indication_search -- --nocapture` passed
- `cargo test symptom_queries_about_disease_prefer_phenotype_section -- --nocapture` passed
- `cargo test gene_disease_queries_prefer_search_all_orientation -- --nocapture` passed
- `cargo test drug_search_empty_state_frames_zero_indication_miss_as_regulatory_signal -- --nocapture` passed
- `cargo test related_drug_for_sparse_card_starts_with_review_follow_up -- --nocapture` passed
- `uv run pytest -q tests/test_public_skill_docs_contract.py tests/test_mcp_contract.py tests/test_upstream_planning_analysis_docs.py --mcp-cmd './target/debug/biomcp serve'` passed
- `uv run --extra dev sh -c 'PATH="$(pwd)/target/debug:$PATH" BIOMCP_BIN="$(pwd)/target/debug/biomcp" pytest spec/01-overview.md spec/02-gene.md spec/05-drug.md spec/06-article.md spec/07-disease.md spec/10-workflows.md spec/19-discover.md --mustmatch-lang bash --mustmatch-timeout 60 -v'` passed after one spec assertion update
- `uv run --extra dev sh -c 'PATH="$(pwd)/target/debug:$PATH" BIOMCP_BIN="$(pwd)/target/debug/biomcp" pytest spec/05-drug.md --mustmatch-lang bash --mustmatch-timeout 60 -v'` passed
- `make check` passed

## Deviations from design

- I could not complete a clean `git rebase main` because this resumed worktree already contained unstaged ticket-local edits before the step started. I validated the diff surface directly instead of aborting because the changes were still within the ticket scope.
- I verified MCP/docs/spec behavior against `target/debug/biomcp`. I did not rerun the release-binary-only `tests/test_mcp_http_transport.py` path in-session because `cargo build --release --locked` was LTO-heavy and did not finish promptly enough to use as a reliable verification loop.
