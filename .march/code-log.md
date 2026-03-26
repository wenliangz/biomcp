# Code Log

## Summary

Completed the remaining source SEO landing pages by:

- adding 10 new source guides in `docs/sources/`
- expanding the `Sources` nav in `mkdocs.yml`
- updating `docs/sources/index.md` metadata and source table
- extending `tests/test_source_pages_docs_contract.py` so the repo enforces the full 18-page source surface

## Commands Run

- `checkpoint status`
- `sed -n '1,240p' .march/ticket.md`
- `sed -n '1,260p' .march/design-draft.md`
- `sed -n '1,520p' .march/design-final.md`
- `sed -n '1,260p' tests/test_source_pages_docs_contract.py`
- `sed -n '1,220p' docs/sources/index.md`
- `sed -n '1,220p' docs/sources/pubmed.md`
- `sed -n '1,220p' docs/sources/reactome.md`
- `sed -n '1,220p' docs/sources/clinvar.md`
- `sed -n '1,220p' docs/sources/semantic-scholar.md`
- `rg -n "OpenTargets|ChEMBL|CIViC|OncoKB|cBioPortal|EMA|KEGG|PharmGKB|CPIC|Human Protein Atlas|Monarch" docs/user-guide docs/reference src/cli/list_reference.md src/cli/list.rs docs/troubleshooting.md`
- `sed -n '1,260p' docs/user-guide/drug.md`
- `sed -n '1,260p' docs/user-guide/gene.md`
- `sed -n '1,260p' docs/user-guide/disease.md`
- `sed -n '1,260p' docs/user-guide/variant.md`
- `sed -n '1,260p' docs/user-guide/pgx.md`
- `sed -n '1,220p' docs/user-guide/pathway.md`
- `sed -n '1,220p' docs/user-guide/phenotype.md`
- `sed -n '1,220p' docs/reference/civic-sections.md`
- `sed -n '1,220p' docs/reference/data-sources.md`
- `sed -n '320,390p' docs/user-guide/cli-reference.md`
- `sed -n '1,140p' src/cli/list_reference.md`
- `uv run --no-project --with pytest python -m pytest tests/test_source_pages_docs_contract.py -q --noconftest`
- `uv run --no-project --with mkdocs-material --with pymdown-extensions mkdocs build --strict`
- `make check`
- `git status --short`

## Changes Made

- Added:
  - `docs/sources/chembl.md`
  - `docs/sources/opentargets.md`
  - `docs/sources/civic.md`
  - `docs/sources/oncokb.md`
  - `docs/sources/cbioportal.md`
  - `docs/sources/ema.md`
  - `docs/sources/kegg.md`
  - `docs/sources/pharmgkb.md`
  - `docs/sources/human-protein-atlas.md`
  - `docs/sources/monarch-initiative.md`
- Updated `docs/sources/index.md`:
  - expanded the SEO description to list all 18 source guides
  - appended the 10 new rows to the source table in the approved order
- Updated `mkdocs.yml`:
  - added the 10 new source pages to the `Sources` nav block
- Updated `tests/test_source_pages_docs_contract.py`:
  - added the 10 new `SOURCE_PAGE_SPECS`
  - expanded the expected source file set
  - expanded the expected `Sources` nav block
  - updated the overview-page description assertion

## Proof / Tests Added

- Updated the existing repo-native proof in `tests/test_source_pages_docs_contract.py` to cover the new source pages and nav/overview contract.

## Verification

- `uv run --no-project --with pytest python -m pytest tests/test_source_pages_docs_contract.py -q --noconftest`
  - passed
- `uv run --no-project --with mkdocs-material --with pymdown-extensions mkdocs build --strict`
  - passed
- `make check`
  - passed

## Deviations

- No design deviations.
- The focused docs-contract test was run with `--noconftest` in a no-project env because the repo `conftest.py` pulls unrelated runtime dependencies; the full repo gate was still validated with `make check`.
