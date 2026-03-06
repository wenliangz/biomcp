# Variant Queries

Variant workflows in BioMCP unify clinical significance, population frequency, and helper pivots to trials and literature. This file validates both broad search behavior and focused retrieval of BRAF V600E context. Assertions emphasize headings, columns, and known durable identifiers.

| Section | Command focus | Why it matters |
|---|---|---|
| Gene-level search | `search variant -g BRAF` | Confirms variant table rendering |
| Protein filter | `search variant -g BRAF --hgvsp V600E` | Confirms targeted query narrowing |
| Detail card | `get variant "BRAF V600E"` | Confirms consolidated variant facts |
| ClinVar section | `get variant ... clinvar` | Confirms clinical interpretation expansion |
| Population section | `get variant ... population` | Confirms frequency context expansion |
| Trial helper | `variant trials ...` | Confirms mutation-centric trial lookup |
| Article helper | `variant articles ...` | Confirms mutation-centric literature lookup |

## Searching by Gene

Gene-scoped variant search is the broad intake step before applying mutation-level filters. The output should include a stable column header set and explicit query echo.

```bash
out="$(biomcp search variant -g BRAF --limit 3)"
echo "$out" | mustmatch like "| ID | Gene | Protein |"
echo "$out" | mustmatch like "Query: gene=BRAF"
```

## Finding a Specific Variant

Adding `--hgvsp` should constrain the result set to a precise protein change. We check for the query marker and V600E appearance in rows.

```bash
out="$(biomcp search variant -g BRAF --hgvsp V600E --limit 3)"
echo "$out" | mustmatch like "hgvsp=V600E"
echo "$out" | mustmatch like "V600E"
```

## Getting Variant Details

The default variant card should include both human-readable and identifier-centric fields. We assert on a stable rsID and pathogenicity marker.

```bash
out="$(biomcp get variant "BRAF V600E")"
echo "$out" | mustmatch like "rs113488022"
echo "$out" | mustmatch like "Significance: Pathogenic"
```

## ClinVar Section

ClinVar-focused expansion is used for clinical interpretation and evidence traceability. The check targets section heading and variant metadata marker.

```bash
out="$(biomcp get variant "BRAF V600E" clinvar)"
echo "$out" | mustmatch like "## ClinVar"
echo "$out" | mustmatch like "Variant ID:"
```

## Population Frequencies

Population frequency context helps distinguish rare versus common variation. We assert on population section labeling and gnomAD field presence.

```bash
out="$(biomcp get variant "BRAF V600E" population)"
echo "$out" | mustmatch like "## Population"
echo "$out" | mustmatch like "gnomAD AF"
```

## Variant to Trials

A mutation-to-trial pivot is central for translational use cases. The trial output should include the expected table schema and mutation query echo.

```bash
out="$(biomcp variant trials "BRAF V600E" --limit 3)"
echo "$out" | mustmatch like "|NCT ID|Title|Status|Phase|Conditions|"
echo "$out" | mustmatch like "Query: mutation=BRAF V600E"
```

## Variant to Articles

Literature helper commands should retain both gene and keyword context in the heading. We verify header context and article table columns.

```bash
out="$(biomcp variant articles "BRAF V600E" --limit 3)"
echo "$out" | mustmatch like "# Articles: gene=BRAF, keyword=V600E"
echo "$out" | mustmatch like "| PMID | Title |"
```
