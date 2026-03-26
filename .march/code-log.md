# Code Log

## Commands Run

```bash
checkpoint status
sed -n '1,220p' .march/ticket.md
sed -n '1,260p' .march/design-draft.md
sed -n '1,260p' .march/design-final.md
sed -n '1,260p' tests/test_upstream_planning_analysis_docs.py
sed -n '1,260p' design/technical/source-integration.md
sed -n '1,320p' design/technical/overview.md
rg -n "region|after_help|get drug|search drug" src/cli/mod.rs src/cli/list.rs src/cli/list_reference.md docs/user-guide/cli-reference.md docs/user-guide/drug.md spec/05-drug.md
rg -n "Semantic Scholar|search article|source all|open-access|--type|InvalidArgument|PMCID|DOI|arXiv|paper IDs|recommendations|citations|references" src/entities/article.rs src/cli/health.rs docs/user-guide/article.md docs/reference/data-sources.md src/cli/search_all.rs tests/article_usage_stderr.rs spec/06-article.md
rg -n "version-sync|deploy docs|pages|workflow_dispatch|install.sh|releases/latest|tag_name|mkdocs build --strict|pytest tests/" .github/workflows/ci.yml .github/workflows/release.yml scripts/check-version-sync.sh install.sh
uv run --no-project --with pytest --with mcp python -m pytest tests/test_upstream_planning_analysis_docs.py -k 'technical_and_ux_docs_match_current_cli_and_workflow_contracts or source_integration_architecture_doc_captures_repo_contract' -v
uv sync --extra dev
uv run pytest tests/test_upstream_planning_analysis_docs.py -v
uv run mkdocs build --strict
git status --short
git diff -- design/technical/overview.md design/technical/source-integration.md tests/test_upstream_planning_analysis_docs.py
```

## What Changed

- Updated `design/technical/source-integration.md` with a new
  `Local Runtime Sources and File-Backed Assets` section that separates EMA
  local runtime readiness from BioASQ benchmark assets.
- Added an `Entity-Specific Command Modifiers` section to
  `design/technical/source-integration.md` so the `get <entity> <id> [section...]`
  grammar, named modifiers, alignment surfaces, and fast-fail validation rules
  have one architecture-level source of truth.
- Updated `design/technical/overview.md` with an
  `Article Federation and Front-Door Validation` section that matches the
  shipped article planner, strict-filter routing, identifier validation, and
  Semantic Scholar helper boundary.
- Expanded the `Release Pipeline` section in
  `design/technical/overview.md` so tag authority, version-sync, docs deploy,
  and `install.sh` behavior are explicit.
- Tightened the `biomcp health` architecture notes in
  `design/technical/overview.md` to include EMA local-data behavior under
  `--apis-only`.
- Extended `tests/test_upstream_planning_analysis_docs.py` in place so the
  existing architecture-doc contract proves the new EMA/BioASQ, modifier,
  article federation, and release-authority text.

## Tests And Proof

- Proof-first failing check before the docs changes:
  `uv run --no-project --with pytest --with mcp python -m pytest tests/test_upstream_planning_analysis_docs.py -k 'technical_and_ux_docs_match_current_cli_and_workflow_contracts or source_integration_architecture_doc_captures_repo_contract' -v`
- Repo-native architecture-doc contract:
  `uv run pytest tests/test_upstream_planning_analysis_docs.py -v`
- Strict docs build:
  `uv run mkdocs build --strict`

## Deviations

- I used a lightweight `uv run --no-project ... pytest` command for the initial
  failing proof because the existing repo-native `uv run pytest ...` path builds
  the editable Rust package first, which was unnecessary to demonstrate a
  text-only docs failure. Final verification still used the repo-native
  `uv sync --extra dev`, `uv run pytest ...`, and `uv run mkdocs build --strict`
  flow.
- No runtime code, specs, user-guide pages, workflows, or scripts needed
  changes after the architecture docs were aligned with the already-shipped
  behavior.
