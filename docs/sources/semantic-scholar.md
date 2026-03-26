---
title: "Semantic Scholar MCP Tool for Citation Graphs | BioMCP"
description: "Use BioMCP to add Semantic Scholar TLDRs, citations, references, and recommendations to literature-review workflows for AI agents."
---

# Semantic Scholar

Semantic Scholar matters when you already have the paper and need the graph around it: the TLDR, the follow-up literature, the references it builds on, and the related papers worth checking next. It turns a flat article lookup into a literature-review workflow that an agent can keep extending without losing the thread.

In BioMCP, `search article` does not expose `--source semantic-scholar`. Instead, Semantic Scholar is an automatic optional search leg when the filter set is compatible. The dedicated helper commands on this page are the direct reason to come here: `get article <id> tldr`, `article citations`, `article references`, and `article recommendations`.

## What BioMCP exposes

| Command | What BioMCP gets from this source | Integration note |
|---|---|---|
| `search article` | Optional compatible search-leg enrichment | Semantic Scholar joins article search automatically when the filter set allows it |
| `get article <id> tldr` | TLDR text, influence counts, and related article metadata | Dedicated Semantic Scholar helper |
| `article citations <id>` | Citation graph rows | Dedicated Semantic Scholar helper |
| `article references <id>` | Reference graph rows | Dedicated Semantic Scholar helper |
| `article recommendations <id>` | Related-paper recommendations | Dedicated Semantic Scholar helper |

## Example commands

```bash
biomcp get article 22663011 tldr
```

Returns a Semantic Scholar section with TLDR text and influence metadata.

```bash
biomcp article citations 22663011 --limit 3
```

Returns a citation graph table with intents, influential flags, and context columns.

```bash
biomcp article references 22663011 --limit 3
```

Returns a reference graph table with the same citation-context fields.

```bash
biomcp article recommendations 22663011 --limit 3
```

Returns a recommendations table with PMID, title, journal, and year columns.

## API access

Optional `S2_API_KEY` for dedicated quota and higher reliability. Configure it with the [API Keys](../getting-started/api-keys.md) guide and request one from the [Semantic Scholar API page](https://www.semanticscholar.org/product/api).

## Official source

[Semantic Scholar](https://www.semanticscholar.org/) is the official literature-graph product behind BioMCP's TLDR and citation helper workflows.

## Related docs

- [Article](../user-guide/article.md)
- [How to find articles](../how-to/find-articles.md)
- [API Keys](../getting-started/api-keys.md)
