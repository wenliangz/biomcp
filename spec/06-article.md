# Article Queries

Article commands provide literature retrieval and annotation-focused enrichment for entity extraction. This spec validates both retrieval modes and PubTator annotation surfaces. Assertions are anchored to headings, IDs, and table schemas that remain stable over time.

| Section | Command focus | Why it matters |
|---|---|---|
| Gene search | `search article -g BRAF` | Confirms gene-linked literature lookup |
| Keyword search | `search article -k immunotherapy` | Confirms free-text discovery |
| Article detail | `get article 22663011` | Confirms canonical article card output |
| Annotation section | `get article ... annotations` | Confirms PubTator integration |
| Entity helper | `article entities 22663011` | Confirms entity extraction pivot |

## Searching by Gene

Gene-based literature search is a common evidence collection step in variant and disease workflows. We assert on heading context and table columns.

```bash
out="$(biomcp search article -g BRAF --limit 3)"
echo "$out" | mustmatch like "# Articles: gene=BRAF"
echo "$out" | mustmatch like "| PMID | Title |"
```

## Searching by Keyword

Keyword search supports broad discovery before narrowing to specific entities. The output should echo keyword context and include PMID-centric table output.

```bash
out="$(biomcp search article -k immunotherapy --limit 3)"
echo "$out" | mustmatch like "keyword=immunotherapy"
echo "$out" | mustmatch like "PMID"
```

## Getting Article Details

The article detail card should preserve stable bibliographic anchors for reproducible referencing. We assert on PMID and journal markers.

```bash
out="$(biomcp get article 22663011)"
echo "$out" | mustmatch like "PMID: 22663011"
echo "$out" | mustmatch like "Journal:"
```

## Article Annotations

Annotation output summarizes entity classes detected by PubTator. The assertions target section heading and gene summary marker.

```bash
out="$(biomcp get article 22663011 annotations)"
echo "$out" | mustmatch like "## PubTator Annotations"
echo "$out" | mustmatch like "Genes:"
```

## Article to Entities

`article entities` exposes actionable next-command pivots by entity class. We check top-level heading and genes subsection marker.

```bash
out="$(biomcp article entities 22663011)"
echo "$out" | mustmatch like "# Entities in PMID 22663011"
echo "$out" | mustmatch like "## Genes"
```
