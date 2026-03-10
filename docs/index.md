# BioMCP

**Single-binary CLI and MCP server for querying biomedical databases.**
One command grammar, compact markdown output, 12 entities across 15+ data sources.

## Install

### PyPI tool install

```bash
uv tool install biomcp-cli
# or, inside an active Python environment:
# pip install biomcp-cli
```

Install the `biomcp-cli` package, then use `biomcp` for the commands shown
throughout the docs.

### Binary install

```bash
curl -fsSL https://biomcp.org/install.sh | bash
```

### Install skills

Install guided investigation workflows into your agent directory:

```bash
biomcp skill install ~/.claude --force
```

### For Claude Desktop / Cursor / MCP clients

```json
{
  "mcpServers": {
    "biomcp": {
      "command": "biomcp",
      "args": ["serve"]
    }
  }
}
```

### Remote HTTP server

For shared or remote deployments, start BioMCP over Streamable HTTP instead of
stdio:

```bash
biomcp serve-http --host 127.0.0.1 --port 8080
```

Remote clients connect to `http://127.0.0.1:8080/mcp`. Probe routes are
`/health`, `/readyz`, and `/`. See
[Remote HTTP Server](getting-started/remote-http.md) for setup details and
`demo/streamable_http_client.py` for a runnable client example.

### From source

```bash
cargo build --release --locked
```

## Quick start

```bash
biomcp health --apis-only            # verify API connectivity
biomcp list                          # show all entities and commands
biomcp list gene                     # show gene-specific filters and examples
```

## Command grammar

```
search <entity> [filters]    → discovery
get <entity> <id> [sections] → focused detail
<entity> <helper> <id>       → cross-entity pivots
enrich <GENE1,GENE2,...>     → gene-set enrichment
batch <entity> <id1,id2,...> → parallel gets
```

## Entities and sources

| Entity | Sources | Example |
|--------|---------|---------|
| gene | MyGene.info, UniProt, Reactome, QuickGO, STRING, CIViC | `biomcp get gene BRAF pathways` |
| variant | MyVariant.info, ClinVar, gnomAD, CIViC, OncoKB, cBioPortal, GWAS Catalog, AlphaGenome | `biomcp get variant "BRAF V600E" clinvar` |
| article | PubMed, PubTator3, Europe PMC | `biomcp search article -g BRAF --limit 5` |
| trial | ClinicalTrials.gov, NCI CTS API | `biomcp search trial -c melanoma -s recruiting` |
| drug | MyChem.info, ChEMBL, OpenTargets, Drugs\@FDA, CIViC | `biomcp get drug pembrolizumab targets` |
| disease | Monarch Initiative, MONDO, CIViC, OpenTargets | `biomcp get disease "Lynch syndrome" genes` |
| pathway | Reactome, g:Profiler | `biomcp get pathway R-HSA-5673001 genes` |
| protein | UniProt, InterPro, STRING, PDB/AlphaFold | `biomcp get protein P15056 domains` |
| adverse-event | OpenFDA (FAERS, MAUDE, Recalls) | `biomcp search adverse-event -d pembrolizumab` |
| pgx | CPIC, PharmGKB | `biomcp get pgx CYP2D6 recommendations` |
| gwas | GWAS Catalog | `biomcp search gwas --trait "type 2 diabetes"` |
| phenotype | Monarch Initiative (HPO) | `biomcp search phenotype "HP:0001250"` |

## Cross-entity helpers

Pivot between related entities without rebuilding filters:

```bash
biomcp variant trials "BRAF V600E" --limit 5
biomcp variant articles "BRAF V600E"
biomcp drug adverse-events pembrolizumab
biomcp drug trials pembrolizumab
biomcp disease trials melanoma
biomcp disease drugs melanoma
biomcp disease articles "Lynch syndrome"
biomcp gene trials BRAF
biomcp gene drugs BRAF
biomcp gene articles BRCA1
biomcp gene pathways BRAF
biomcp pathway drugs R-HSA-5673001
biomcp pathway articles R-HSA-5673001
biomcp pathway trials R-HSA-5673001
biomcp protein structures P15056
biomcp article entities 22663011
```

## Gene-set enrichment

```bash
biomcp enrich BRAF,KRAS,NRAS --limit 10
```

## Sections and progressive disclosure

Every `get` command supports selectable sections:

```bash
biomcp get gene BRAF                    # summary card
biomcp get gene BRAF pathways           # add pathway section
biomcp get gene BRAF civic interactions # multiple sections
biomcp get gene BRAF all                # everything

biomcp get variant "BRAF V600E" clinvar population conservation
biomcp get drug pembrolizumab label targets civic approvals
biomcp get disease "Lynch syndrome" genes phenotypes variants
biomcp get trial NCT02576665 eligibility locations outcomes
```

## API keys

Most commands work without credentials. Optional keys improve rate limits:

```bash
export NCBI_API_KEY="..."        # PubTator, PMC OA, NCBI ID converter
export OPENFDA_API_KEY="..."     # OpenFDA rate limits
export NCI_API_KEY="..."         # NCI CTS trial search (--source nci)
export ONCOKB_TOKEN="..."        # OncoKB variant helper
export ALPHAGENOME_API_KEY="..." # AlphaGenome variant effect prediction
```

## Skills

BioMCP ships an embedded guide for agent workflows rather than a built-in
catalog. Read it with `biomcp skill`, install it with
`biomcp skill install ~/.claude --force`, and see
[Skills](getting-started/skills.md) for the current workflow and legacy notes.

## Documentation

- [Installation](getting-started/installation.md)
- [First Query](getting-started/first-query.md)
- [Data Sources](reference/data-sources.md)
- [Quick Reference](reference/quick-reference.md)
- [Troubleshooting](troubleshooting.md)

## License

MIT
