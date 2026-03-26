---
title: "PubMed MCP Tool for AI Agents | BioMCP"
description: "Search PubMed in BioMCP with PubTator3 annotations, article summaries, and PMC full-text handoff so AI agents can review literature faster."
---

# PubMed

PubMed is the starting point for most biomedical literature work because it gives researchers a shared identifier system, durable abstracts, and the fastest path from a gene, disease, or drug question to the papers that matter. If you want an MCP-friendly literature workflow that still speaks the language of PMIDs, this is the page to start with.

In BioMCP, "PubMed" is an umbrella label. Search and summary retrieval combine PubTator3 with Europe PMC, while full-text resolution uses PMC OA plus the NCBI ID Converter. Semantic Scholar TLDR, citation, reference, and recommendation helpers belong on the [Semantic Scholar](semantic-scholar.md) page because they come from a different provider surface.

## What BioMCP exposes

| Command | What BioMCP gets from this source | Integration note |
|---|---|---|
| `search article` | PMID-ranked literature search results with typed filters | Federated across PubTator3 and Europe PMC under the PubMed umbrella |
| `get article <id>` | Article summary card with identifiers, journal, and abstract context | Uses Europe PMC metadata with BioMCP normalization |
| `get article <id> annotations` | PubTator entity annotations for a paper | PubTator3-only section |
| `get article <id> fulltext` | Open-access full-text handoff with saved Markdown path | Uses PMC OA plus NCBI ID Converter |
| `article entities <pmid>` | Entity-grouped follow-up view for a PMID | Derived from PubTator3 annotation output |

## Example commands

```bash
biomcp search article -g BRAF --limit 3
```

Returns an article table with PMID and title columns for a fast literature scan.

```bash
biomcp get article 22663011
```

Returns an article card with PMID, journal, and summary metadata.

```bash
biomcp get article 22663011 annotations
```

Returns a PubTator annotation section with entity groups and counts.

```bash
biomcp article entities 22663011
```

Returns an entity-grouped follow-up view with separate genes, diseases, and drugs sections.

```bash
biomcp get article 27083046 fulltext
```

Returns a full-text section when PMC OA is available and prints a `Saved to:` cache path.

## API access

Optional `NCBI_API_KEY` for higher NCBI throughput. Set it through the [API Keys](../getting-started/api-keys.md) guide and create one in [My NCBI](https://www.ncbi.nlm.nih.gov/account/settings/).

## Official source

[PubMed](https://pubmed.ncbi.nlm.nih.gov/) is the official NLM literature search surface most researchers already anchor on.

## Related docs

- [Article](../user-guide/article.md)
- [How to find articles](../how-to/find-articles.md)
- [API Keys](../getting-started/api-keys.md)
