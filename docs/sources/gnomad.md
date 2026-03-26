---
title: "gnomAD MCP Tool for Variant Frequency Analysis | BioMCP"
description: "Use BioMCP to pull gnomAD population frequencies and gene constraint metrics for variant interpretation, rarity checks, and gene-level context."
---

# gnomAD

gnomAD is the quickest way to answer the question that often changes an interpretation: how rare is this variant, and how constrained is this gene in population data? It matters because frequency and constraint are among the fastest filters for separating plausible signals from common background variation.

In BioMCP, gene constraint comes from the gnomAD source path directly, while variant population output is rendered as gnomAD-backed population context even though the current variant workflow surfaces those fields through MyVariant.info payloads. That distinction matters if you are tracing provenance or comparing the gene and variant views side by side.

## What BioMCP exposes

| Command | What BioMCP gets from this source | Integration note |
|---|---|---|
| `get gene <symbol> constraint` | Gene-level constraint metrics such as LOEUF-style context | Direct gnomAD-backed gene section |
| `get variant <id> population` | Population frequency lines and subpopulation context | Rendered from gnomAD-backed fields in the MyVariant payload |
| `search variant -g <gene> --max-frequency <value>` | Rarity-filtered variant search rows | Search filter uses population-frequency context aligned with gnomAD fields |

## Example commands

```bash
biomcp get gene BRAF constraint
```

Returns a constraint section with gnomAD provenance and LOEUF-style metrics.

```bash
biomcp get variant rs113488022 population
```

Returns a population section with a gnomAD AF line and related population context.

```bash
biomcp get variant "chr7:g.140453136A>T" population
```

Returns the same population section for HGVS input.

```bash
biomcp search variant -g BRCA1 --max-frequency 0.01 --limit 5
```

Returns variant rows constrained by a rarity filter.

## API access

No BioMCP API key required.

## Official source

[gnomAD](https://gnomad.broadinstitute.org/) is the official Broad Institute population-resource homepage behind these frequency and constraint views.

## Related docs

- [Gene](../user-guide/gene.md)
- [Variant](../user-guide/variant.md)
- [Source Licensing and Terms](../reference/source-licensing.md)
