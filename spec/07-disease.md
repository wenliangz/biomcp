# Disease Queries

Disease commands normalize labels to ontology-backed identifiers and provide cross-entity pivots. This file validates melanoma-centric workflows plus canonical MONDO-ID disease-gene paths for somatic and germline coverage. Assertions focus on stable schema and identifier markers rather than dynamic counts.

| Section | Command focus | Why it matters |
|---|---|---|
| Disease search | `search disease melanoma` | Confirms disease normalization output |
| Disease detail | `get disease melanoma` | Confirms canonical disease card |
| Disease genes | `get disease melanoma genes` | Confirms association section rendering |
| Sparse phenotype guidance | `get disease MONDO:0100605 phenotypes` | Confirms truthful completeness note and review follow-up |
| Disease to trials | `disease trials melanoma` | Confirms trial helper path |
| Disease to articles | `disease articles melanoma` | Confirms literature helper path |
| Disease to drugs | `disease drugs melanoma` | Confirms treatment helper path |

## Searching by Name

Search should return ontology-backed disease rows and canonical MONDO identifiers. We assert table schema and the melanoma MONDO ID marker.

```bash
out="$(biomcp search disease melanoma --limit 3)"
echo "$out" | mustmatch like "| ID | Name | Synonyms |"
echo "$out" | mustmatch like "MONDO:0005105"
```

## Getting Disease Details

The disease detail card should resolve the query label to a normalized concept. This check targets heading and canonical ID line.

```bash
out="$(biomcp get disease melanoma)"
echo "$out" | mustmatch like "# melanoma"
echo "$out" | mustmatch like "ID: MONDO:0005105"
echo "$out" | mustmatch like "Genes (Open Targets): CDKN2A (OT"
```

## Disease Crosswalk Identifier Resolution

Crosswalkable identifiers such as MeSH should resolve through MyDisease xrefs
and return the same canonical disease card path as the free-text lookup.

```bash
mesh_id="$(biomcp --json get disease melanoma | jq -r '.xrefs.MeSH')"
test -n "$mesh_id"
test "$mesh_id" != "null"
out="$(biomcp get disease "MESH:${mesh_id}")"
echo "$out" | mustmatch like "# melanoma"
echo "$out" | mustmatch like "ID: MONDO:0005105"
```

## Full Disease Definitions

Disease detail output should preserve the full curated definition text so characterization clauses remain available without falling back to phenotype dumps.

```bash
bin="${BIOMCP_BIN:-biomcp}"
out="$("$bin" get disease MONDO:0100605)"
echo "$out" | mustmatch like "hypogonadotropic hypogonadism"
echo "$out" | mustmatch like "neurodevelopmental delay or regression"
echo "$out" | mustmatch not like "It is characterized by the association of…"
```

```bash
bin="${BIOMCP_BIN:-biomcp}"
out="$("$bin" get disease MONDO:0017799)"
echo "$out" | mustmatch like "pleural effusion, ascites and non-malignant ovarian neoplasm"
echo "$out" | mustmatch like "surgical resection of the ovarian mass"
echo "$out" | mustmatch not like "Prognosis is favorable following…"
```

## Disease Genes

Associated-gene expansion is central for translating phenotype-level queries into molecular follow-up. We assert on section heading and table structure.

```bash
out="$(biomcp get disease melanoma genes)"
echo "$out" | mustmatch like "## Associated Genes"
echo "$out" | mustmatch like "| Gene | Relationship | Source | OpenTargets |"
echo "$out" | mustmatch '/overall [0-9.]+/'
```

## Canonical CLL Disease Genes

Canonical MONDO IDs should surface OpenTargets-contributed cancer genes directly in the disease-gene table rather than only in the compact summary.

```bash
bin="${BIOMCP_BIN:-biomcp}"
out="$("$bin" get disease MONDO:0003864 genes)"
echo "$out" | mustmatch like "## Associated Genes"
echo "$out" | mustmatch like "| Gene | Relationship | Source | OpenTargets |"
echo "$out" | mustmatch like "| TP53 | associated with disease |"
echo "$out" | mustmatch like "| ATM | associated with disease |"
echo "$out" | mustmatch like "| NOTCH1 | associated with disease |"
echo "$out" | mustmatch like "OpenTargets"
echo "$out" | mustmatch '/overall [0-9.]+/'
```

## Canonical T-PLL Disease Genes

Sparse canonical MONDO cards should recover a human-readable disease label and associated genes through the OLS4-to-OpenTargets path.

```bash
bin="${BIOMCP_BIN:-biomcp}"
out="$("$bin" get disease MONDO:0019468 genes)"
echo "$out" | mustmatch like "# T-cell prolymphocytic leukemia"
echo "$out" | mustmatch like "## Associated Genes"
echo "$out" | mustmatch like "| ATM | associated with disease |"
echo "$out" | mustmatch like "| JAK3 | associated with disease |"
echo "$out" | mustmatch like "| STAT5B | associated with disease |"
echo "$out" | mustmatch like "OpenTargets"
```

## Canonical Parkinson Disease Genes

Germline-oriented diseases should still render a populated genes table with stable Parkinson anchors.

```bash
bin="${BIOMCP_BIN:-biomcp}"
out="$("$bin" get disease MONDO:0005180 genes)"
echo "$out" | mustmatch like "## Associated Genes"
echo "$out" | mustmatch like "| SNCA | causes |"
```

## Canonical CMT1A Disease Genes

Narrow Mendelian diseases should keep their focused Monarch-style signal instead of regressing into unrelated OT noise.

```bash
bin="${BIOMCP_BIN:-biomcp}"
out="$("$bin" get disease MONDO:0007309 genes)"
echo "$out" | mustmatch like "## Associated Genes"
echo "$out" | mustmatch like "| PMP22 | causes |"
```

## Disease Top Variant Summary

Variant expansions should expose the top-ranked disease-to-variant anchor directly in both JSON and markdown, while keeping the full table intact.

```bash
out="$(biomcp --json get disease melanoma variants)"
echo "$out" | jq -e '.top_variant.variant | type == "string"' > /dev/null
echo "$out" | jq -e '.top_variant.source | type == "string"' > /dev/null
echo "$out" | jq -e '.top_variant.evidence_count | type == "number"' > /dev/null
```

```bash
out="$(biomcp get disease melanoma variants)"
echo "$out" | mustmatch like "## Variants"
echo "$out" | mustmatch like "Top Variant:"
```

## Disease to Trials

Disease helper commands should map directly into trial search with condition context retained. The check asserts query echo and trial columns.

```bash
out="$(biomcp disease trials melanoma --limit 3)"
echo "$out" | mustmatch like "condition=melanoma"
echo "$out" | mustmatch like "|NCT ID|Title|Status|Phase|Conditions|"
```

## Disease to Articles

Disease-linked literature retrieval supports rapid evidence triage. Assertions check heading context and the article table schema.

```bash
out="$(biomcp disease articles melanoma --limit 3)"
echo "$out" | mustmatch like "# Articles: disease=melanoma"
echo "$out" | mustmatch like "| PMID | Title |"
```

## Disease to Drugs

Disease-to-drug pivoting provides treatment-oriented context when starting from diagnosis. The output should include indication heading and compact drug table.

```bash
out="$(biomcp disease drugs melanoma --limit 3)"
echo "$out" | mustmatch like "# Drugs: indication=melanoma"
echo "$out" | mustmatch like "|Name|Mechanism|Target|"
```

## Sparse Phenotype Coverage Notes

When phenotype rows are present but limited, BioMCP should say the section is source-backed and may be incomplete for the full disease presentation, then suggest a review-literature follow-up.

```bash
out="$(biomcp get disease MONDO:0100605 phenotypes)"
echo "$out" | mustmatch like "source-backed"
echo "$out" | mustmatch like "may be incomplete for the full disease presentation"
echo "$out" | mustmatch like 'biomcp search article -d "4H leukodystrophy" --type review --limit 5'
```

## Disease Phenotype Key Features

Section-only phenotype output should distinguish the classic disease summary from the comprehensive HPO table.

```bash
bin="${BIOMCP_BIN:-biomcp}"
out="$("$bin" get disease MONDO:0008222 phenotypes)"
echo "$out" | mustmatch like "### Key Features"
echo "$out" | mustmatch '/periodic muscle paralysis/i'
echo "$out" | mustmatch '/QT interval/i'
echo "$out" | mustmatch like "source-backed"
```

## Disease Phenotype Key Features JSON

Structured disease output should expose the same compact summary as `key_features`.

```bash
bin="${BIOMCP_BIN:-biomcp}"
out="$("$bin" --json get disease MONDO:0008222 phenotypes)"
echo "$out" | jq -e '.key_features | length >= 3' > /dev/null
echo "$out" | jq -e '.key_features | any(test("periodic muscle paralysis"; "i"))' > /dev/null
```

## Exact Disease Ranking

Exact disease labels should be reranked to the front of the returned page even when upstream ordering is noisy. This regression checks that the canonical colorectal cancer node appears in the surfaced result set.

```bash
bin="${BIOMCP_BIN:-biomcp}"
out="$("$bin" search disease "colorectal cancer" --limit 10)"
echo "$out" | mustmatch like "| ID | Name | Synonyms |"
echo "$out" | mustmatch like "| MONDO:0024331 | colorectal carcinoma |"
```

## Disease DisGeNET Associations

DisGeNET scored disease-gene associations require `DISGENET_API_KEY`. The section heading and table schema are stable invariants; individual scores and row counts vary by API tier.

```bash
status=0
out="$(biomcp get disease melanoma disgenet 2>&1)" || status=$?
if [ "$status" -eq 0 ] && ! printf '%s\n' "$out" | grep -qi '403 Forbidden'; then
  echo "$out" | mustmatch like "## DisGeNET"
  echo "$out" | mustmatch like "| Gene | Entrez ID | Score | PMIDs | Trials | EL | EI |"
else
  echo "$out" | mustmatch '/(403 Forbidden|forbidden|DISGENET_API_KEY|Unauthorized)/'
fi
```

```bash
status=0
out="$(biomcp get disease melanoma disgenet --json 2>&1)" || status=$?
if [ "$status" -eq 0 ] && ! printf '%s\n' "$out" | grep -qi '403 Forbidden'; then
  echo "$out" | jq -e '.disgenet.associations | length > 0' > /dev/null
else
  echo "$out" | mustmatch '/(403 Forbidden|forbidden|DISGENET_API_KEY|Unauthorized)/'
fi
```
