# Code Log

## Summary

Implemented the approved documentation-consistency pass as a docs-only change
set across the public landing copy, how-to pages, entity guides,
source/reference docs, examples, and operator-facing READMEs. Added a
ticket-specific docs-contract test file, updated the two spec-backed how-to
pages, and completed a review repair sweep against `.march/design-final.md`.

That review sweep fixed four issues in the resumed worktree:

- `README.md` still used stale `.mcpb` wording instead of the approved
  Anthropic Directory / JSON-config split
- the new docs-contract file did not lock that README install guidance
- the staged chart-blog contract had been retargeted away from
  `docs/blog/biomcp-kuva-charts.md`
- two out-of-scope blog intro rewrites and one entity-guide ordering drift were
  still present in the worktree

## Commands Run

- `checkpoint status`
- `sed -n '1,260p' .march/design-draft.md`
- `sed -n '1,520p' .march/design-final.md`
- `sed -n '1,220p' /home/ian/workspace/.agents/skills/checkpoint/SKILL.md`
- `sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/rust-standards/SKILL.md`
- `sed -n '1,220p' /home/ian/workspace/planning/flows/build/skills/testing-mindset/SKILL.md`
- `git status --short`
- `git status --short --untracked-files=all`
- `git status --short --ignored`
- `git diff --cached --stat`
- `git diff --cached -- tests/test_documentation_consistency_audit_contract.py tests/test_public_skill_docs_contract.py spec/17-cross-entity-pivots.md spec/17-guide-workflows.md`
- `git diff --cached -- README.md docs/index.md docs/getting-started/api-keys.md docs/getting-started/claude-desktop.md docs/reference/error-codes.md docs/reference/source-licensing.md docs/sources/oncokb.md docs/charts/bar.md`
- `git diff --cached -- docs/user-guide/gene.md docs/user-guide/cli-reference.md docs/user-guide/disease.md docs/user-guide/trial.md docs/user-guide/adverse-event.md docs/user-guide/pgx.md docs/user-guide/gwas.md docs/user-guide/phenotype.md docs/user-guide/pathway.md docs/user-guide/protein.md docs/user-guide/variant.md docs/user-guide/drug.md docs/user-guide/discover.md`
- `git diff --cached -- docs/how-to/annotate-variants.md docs/how-to/cross-entity-pivots.md docs/how-to/find-articles.md docs/how-to/find-trials.md docs/how-to/guide-workflows.md docs/how-to/predict-effects.md docs/how-to/reproduce-papers.md docs/how-to/search-all-workflow.md docs/how-to/skill-validation.md`
- `git diff --cached -- examples/README.md examples/geneagent/README.md examples/genegpt/README.md examples/pubmed-beyond/README.md examples/trialgpt/README.md scripts/README.md paper/README.md benchmarks/bioasq/README.md docs/blog/we-deleted-35-tools.md docs/troubleshooting.md docs/reference/data-sources.md`
- `sed -n '1,240p' docs/user-guide/gene.md`
- `sed -n '1,220p' tests/test_public_search_all_docs_contract.py`
- `sed -n '1,220p' tests/test_source_licensing_docs_contract.py`
- `sed -n '1,260p' tests/test_source_pages_docs_contract.py`
- `sed -n '1,220p' tests/test_directory_submission_contract.py`
- `sed -n '1,220p' tests/test_docs_changelog_refresh.py`
- `apply_patch` to update docs/tests and write the March logs
- `checkpoint note "Code review found three repair items: restore the biomcp-kuva-charts public-skill contract, revert out-of-scope blog intro rewrites, and move gene error-handling back before JSON mode."`
- `uv run --extra dev pytest tests/test_documentation_consistency_audit_contract.py tests/test_public_search_all_docs_contract.py tests/test_source_licensing_docs_contract.py tests/test_source_pages_docs_contract.py tests/test_directory_submission_contract.py tests/test_public_skill_docs_contract.py tests/test_docs_changelog_refresh.py -q`
- `uv run mkdocs build --strict`
- `cargo build --release --locked`
- `PATH="$(pwd)/target/release:$PATH" uv run --extra dev pytest spec/17-cross-entity-pivots.md spec/17-guide-workflows.md --mustmatch-lang bash --mustmatch-timeout 60 -q`
- `make check`
- `find site .pytest_cache .ruff_cache spec/__pycache__ tests/__pycache__ target -mindepth 1 -delete 2>/dev/null; rmdir site .pytest_cache .ruff_cache spec/__pycache__ tests/__pycache__ target 2>/dev/null || true`
- `git add -A`
- `git diff --cached --stat`
- `git diff --cached`
- `checkpoint done 1`
- `checkpoint done 2`
- `checkpoint done 3`
- `checkpoint done 4`
- `checkpoint done 5`
- `checkpoint done 6`
- `checkpoint note "Code review is complete: fixed the approved-design drift, no separate out-of-scope follow-up issues remain, and all required docs proofs passed."`
- `checkpoint status`

## Changes Made

- Shared public copy:
  - added `discover <query>` to the `README.md` command grammar
  - harmonized the README/docs-index article-search and study bullets to the
    approved shared sentences
  - kept the README configuration table as the directory-specific three-key
    surface while completing the broader env-var inventory in
    `docs/index.md`, `docs/getting-started/api-keys.md`,
    `docs/reference/data-sources.md`, and `docs/reference/error-codes.md`
  - rewrote the README Claude Desktop note to the approved stable wording:
    Anthropic Directory first, JSON config for local/manual setups
  - clarified the `ONCOKB_TOKEN` naming and explicit helper usage without
    renaming the env var

- Guide normalization:
  - standardized the nine how-to H1s to `# How to: ...`
  - updated `spec/17-cross-entity-pivots.md` and `spec/17-guide-workflows.md`
    to match those public headings
  - aligned the entity guides to the approved section flow by adding or
    renaming `Helper commands` / `Practical tips` blocks and by adding explicit
    search-only/helper-less note sections where needed
  - kept the positional gene search teaching path, added
    `biomcp get gene BRAF all`, and moved the gene error-handling section back
    before `## JSON mode`
  - rewrote the discover guide opener into direct imperative copy and added
    related guides
  - replaced the `--date-from` article example in the search-all workflow with
    `--since`

- Reference, examples, and operator docs:
  - corrected the CIViC surfaced-command list in
    `docs/reference/source-licensing.md`
  - expanded `docs/reference/error-codes.md` to the full current public env-var
    inventory
  - updated `docs/blog/we-deleted-35-tools.md` for the approved tool-count
    framing, primary install path, `SKILL.md` docs link, and `## Try it`
  - removed the standalone terminal-output block from `docs/charts/bar.md`
    instead of expanding that pattern to other chart pages
  - removed unexplained jargon from `examples/README.md`, added prerequisites
    and runtime guidance to the example READMEs, and replaced vague scoring
    wording with plain-language checks
  - simplified `scripts/README.md`, removed stale temporal wording from
    `paper/README.md`, and standardized the BioASQ public-ingester commands to
    `uv run --quiet --script ...`

- Review repairs:
  - restored the existing public-skill chart-blog contract to
    `docs/blog/biomcp-kuva-charts.md`
  - reverted the out-of-scope intro rewrites in the untouched blog posts
  - extended the new docs-contract file so the repaired README Claude Desktop
    wording is locked by tests

## Proof / Tests Added or Updated

- Added:
  - `tests/test_documentation_consistency_audit_contract.py`

- Updated:
  - `spec/17-cross-entity-pivots.md`
  - `spec/17-guide-workflows.md`

## Verification

- `uv run --extra dev pytest tests/test_documentation_consistency_audit_contract.py tests/test_public_search_all_docs_contract.py tests/test_source_licensing_docs_contract.py tests/test_source_pages_docs_contract.py tests/test_directory_submission_contract.py tests/test_public_skill_docs_contract.py tests/test_docs_changelog_refresh.py -q`
  - passed: `50 passed`
- `uv run mkdocs build --strict`
  - passed
- `PATH="$(pwd)/target/release:$PATH" uv run --extra dev pytest spec/17-cross-entity-pivots.md spec/17-guide-workflows.md --mustmatch-lang bash --mustmatch-timeout 60 -q`
  - passed: `23 passed, 1 skipped`
- `make check`
  - passed

## Deviations / Notes

- Implemented against `.march/design-final.md`, not the earlier draft. Two
  approved-design decisions that materially changed the final diff:
  - keep both chart blog posts; do not delete either file
  - normalize chart docs by trimming `docs/charts/bar.md` to the compact shared
    shape instead of expanding terminal-output sections across every chart page
- `uv run mkdocs build --strict` still prints the existing informational nav
  note for `docs/blog/biomcp-kuva-charts.md`, `docs/charts/scatter.md`, and
  `docs/charts/waterfall.md`, plus the upstream Material/MkDocs 2.0 advisory.
  The build passes and the approved scope explicitly left nav work alone.
