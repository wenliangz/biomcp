# Code Log

## Summary

Implemented the new `Sources` docs section for the approved high-value SEO batch:

- added `docs/sources/index.md`
- added eight source landing pages:
  - `docs/sources/pubmed.md`
  - `docs/sources/clinicaltrials-gov.md`
  - `docs/sources/clinvar.md`
  - `docs/sources/openfda.md`
  - `docs/sources/uniprot.md`
  - `docs/sources/gnomad.md`
  - `docs/sources/reactome.md`
  - `docs/sources/semantic-scholar.md`
- updated `mkdocs.yml` to add the `Sources` nav section between `User Guide` and `How-To`
- added a repo-native docs contract test at `tests/test_source_pages_docs_contract.py`

## Commands Run

- `checkpoint status`
- `sed -n '1,220p' .march/ticket.md`
- `sed -n '1,260p' .march/design-draft.md`
- `sed -n '1,520p' .march/design-final.md`
- `sed -n '1,260p' mkdocs.yml`
- `sed -n '1,220p' docs/reference/sources.json`
- `sed -n '1,240p' docs/reference/data-sources.md`
- `sed -n '1,220p' docs/reference/source-licensing.md`
- `sed -n '1,220p' docs/getting-started/api-keys.md`
- `sed -n '1,260p' docs/user-guide/article.md`
- `sed -n '1,260p' docs/user-guide/trial.md`
- `sed -n '1,260p' docs/user-guide/variant.md`
- `sed -n '1,260p' docs/user-guide/adverse-event.md`
- `sed -n '1,260p' docs/user-guide/drug.md`
- `sed -n '1,260p' docs/user-guide/gene.md`
- `sed -n '1,260p' docs/user-guide/pathway.md`
- `sed -n '1,260p' docs/user-guide/protein.md`
- `sed -n '1,220p' /home/ian/workspace/marketing/biomcp/plan.md`
- `uv sync --extra dev --no-install-project`
- `.venv/bin/python -m pytest tests/test_source_pages_docs_contract.py -v`
- `cargo build --release --locked`
- `.venv/bin/mkdocs build --strict`
- `rg -n '<title>|meta name="description"' site/sources/index.html site/sources/*/index.html`
- `make check`
- `git status --short`

### Live example verification

Ran the published source-page examples against `target/release/biomcp`:

- PubMed: `search article -g BRAF --limit 3`, `get article 22663011`, `get article 22663011 annotations`, `article entities 22663011`, `get article 27083046 fulltext`
- ClinicalTrials.gov: `search trial -c melanoma --status recruiting --limit 3`, `search trial -c melanoma --mutation "BRAF V600E" --limit 3`, `get trial NCT02576665`, `get trial NCT02576665 eligibility`, `get trial NCT02576665 locations --limit 3`
- ClinVar: `get variant rs113488022`, `get variant rs113488022 clinvar`, `get variant "BRAF V600E" clinvar`, `search variant -g BRCA1 --significance pathogenic --limit 5`
- OpenFDA: `search adverse-event --drug pembrolizumab --limit 3`, `search adverse-event --type recall --drug metformin --limit 3`, `search adverse-event --type device --device "insulin pump" --limit 3`, `get drug vemurafenib label`, `get drug dabrafenib approvals`
- UniProt: `search protein BRAF --limit 3`, `get protein P15056`, `get gene BRAF protein`, `get protein P15056 structures`
- gnomAD: `get gene BRAF constraint`, `get variant rs113488022 population`, `get variant "chr7:g.140453136A>T" population`, `search variant -g BRCA1 --max-frequency 0.01 --limit 5`
- Reactome: `search pathway "MAPK signaling" --limit 5`, `get pathway R-HSA-5673001`, `get pathway R-HSA-5673001 genes`, `get pathway R-HSA-5673001 events`, `get gene BRAF pathways`
- Semantic Scholar: `get article 22663011 tldr`, `article citations 22663011 --limit 3`, `article references 22663011 --limit 3`, `article recommendations 22663011 --limit 3`

## Proof Added

- Added `tests/test_source_pages_docs_contract.py`
- Verified the new contract failed before implementation and passed after implementation

## Tests and Verification

- `.venv/bin/python -m pytest tests/test_source_pages_docs_contract.py -v` passed
- `cargo build --release --locked` passed
- `.venv/bin/mkdocs build --strict` passed
- `rg` against `site/sources/*.html` confirmed rendered `<title>` and `<meta name="description">` entries for the new pages
- `make check` passed

## Deviations

- No design deviations in file set or nav placement
- Semantic Scholar's unauthenticated helper path hit a live provider rate limit during verification, so the final proof used the configured `S2_API_KEY` path for the published Semantic Scholar examples
