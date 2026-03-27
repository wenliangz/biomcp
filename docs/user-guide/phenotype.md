# Phenotype

Use phenotype commands to search HPO terms and phenotype-gene associations from the Monarch Initiative.

## Search phenotypes

By HPO identifiers (space-separated):

```bash
biomcp search phenotype "HP:0001250 HP:0001263"
```

By name or keyword:

```bash
biomcp search phenotype seizure
```

Multiple terms with limit:

```bash
biomcp search phenotype "HP:0001250 HP:0001263" --limit 20
```

The positional `terms` argument accepts HPO IDs or keywords, space-separated or
comma-separated. Use `--limit` and `--offset` when you need bounded paging.

## Get records

Phenotype is search-only. There is no `get phenotype` subcommand.

## Request sections

Phenotype search rows do not expose extra section names. Use `search disease`
or `get disease <id> phenotypes` when you want a normalized disease follow-up.

## Helper commands

Phenotype is search-only. Start with `search phenotype` for HPO term sets or
keyword discovery, then switch to disease commands once you have the right
normalized concept.

## JSON mode

```bash
biomcp --json search phenotype "HP:0001250"
```

## Practical tips

- Use HPO IDs for precise lookups when you know the exact term.
- Use plain-text keywords for exploratory searches across phenotype names.
- Combine multiple HPO IDs in a single query to retrieve a phenotype set.

## Related guides

- [Gene](gene.md)
- [Disease](disease.md)
- [GWAS](gwas.md)
