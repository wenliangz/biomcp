# BioASQ Ranking Calibration

This directory documents the repo-local calibration surface for article-ranking
tuning. It does not create a new benchmark lane or change shipped ranking
behavior; it records the current LB-100 lexical baseline so future ranking work
can compare rescue logic against stable fixtures.

## Verified automated scenarios

All verified automated cases live in the `#[cfg(test)]` module of
`src/entities/article.rs`.

| Scenario | Fixture surface | Rust test | Current baseline |
|---|---|---|---|
| LB-100 MeSH synonym gap | `lb100_mesh_synonym_fixture()` around PMID `31832001` | `mesh_synonym_gap_records_pubmed_tier0_baseline` | The PubMed answer stays `directness_tier == 0` and ranks below a literal-match Europe PMC row |
| LB-100 anchor-count asymmetry | `lb100_anchor_count_fixture()` around PMID `31832001` | `anchor_count_gap_records_pubmed_title_hit_deficit_baseline` | The PubMed answer and Europe PMC row both land in tier 1, but Europe PMC wins on `title_anchor_hits` |
| Positive control | Existing mixed-federation candidate set | `pubmed_unique_row_survives_first_page_in_mixed_federation` | Strong lexical PubMed coverage still ranks first without any rescue signal |

## Public bundle regeneration

Regenerate the recommended public historical bundle with the repo-standard
command:

```bash
uv run --quiet --script benchmarks/bioasq/ingest_public.py --bundle hf-public-pre2026
```

Use that bundle when you want to compare future ranking rescue logic against the
public BioASQ lane after the unit-test fixtures are green.

## Provenance pointers

- `benchmarks/bioasq/datasets/manifest.json`
- `benchmarks/bioasq/datasets/README.md`
- `docs/reference/bioasq-benchmark.md`

Those files remain authoritative for bundle ids, output layout, provenance
boundaries, and the public-lane versus official-lane runbook.

## Existing live JSON proof

The existing structural ranking-metadata proof remains
`spec/06-article.md::Keyword Anchors Tokenize In JSON Ranking Metadata`.
Ticket 149 does not add a new live ranking-order spec because upstream article
responses drift; the stable calibration surface is these Rust fixtures plus the
benchmark docs.

## Historical leads

These leads remain useful context, but they are not part of the mandatory
automated fixture set in ticket 149.

| Lead | Expected PMID(s) | Status |
|---|---|---|
| WDR5 / pancreatic cancer | `28741490` | Historical context only; not promoted to an automated fixture in this ticket |
| RUNX1T1 / m6A methylation | `32589708`, `25412662` | Historical context only; not promoted to an automated fixture in this ticket |
| Pds5b / Cornelia de Lange | unresolved | Historical lead; answer PMID is unresolved in current repo artifacts |
| etanercept / anti-TNF | unresolved | Historical lead; answer PMID is unresolved in current repo artifacts |
