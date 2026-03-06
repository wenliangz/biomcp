---
name: biomcp
description: Search and retrieve biomedical data - genes, variants, clinical trials, articles, drugs, diseases, pathways, proteins, adverse events, pharmacogenomics, and phenotype-disease matching. Use for gene function, variant pathogenicity, trials, drug safety, pathway context, disease workups, and literature evidence.
---

# BioMCP CLI

## Pick the Narrowest Valid Command

- If the prompt names a specific entity, start with `get` or a helper for that entity.
- Use `search all` only for broad multi-entity investigations.
- If the CLI surface is unclear, run `biomcp list <entity>` before guessing flags or sections.

## Command Grammar

```bash
biomcp search <entity> [filters]
biomcp get <entity> <id> [sections]
biomcp <entity-family> <helper> <id-or-name>
```

Only use documented sections and helper arguments.
If an entity ID or name contains spaces, quote the whole value when using `get` or helper commands.

## Search Patterns

Free-text entities use positional query or `-q`:

```bash
biomcp search gene BRAF --limit 5
biomcp search disease "Lynch syndrome" --limit 5
biomcp search pathway "MAPK" --limit 5
biomcp search protein TP53 --limit 5
```

Structured entities use filters:

```bash
biomcp search variant -g BRAF --significance pathogenic --limit 5
biomcp search article -g BRAF -d melanoma --since 2023-01-01 --limit 5
biomcp search article -k "immunotherapy resistance" --sort citations --limit 5
biomcp search trial -c melanoma --mutation "BRAF V600E" --status recruiting --limit 5
biomcp search drug --target EGFR --indication "non-small cell lung cancer" --limit 5
```

Positional shorthand (single entity + query):

```bash
biomcp search variant BRAF V600E
biomcp search trial melanoma --status recruiting --limit 5
biomcp search all BRAF
```

Drug search uses positional query or `-q/--query`, not `-k/--keyword`.

## Helpers and Pivots

```bash
biomcp variant articles "BRAF V600E"
biomcp variant trials "BRAF V600E"
biomcp gene pathways BRAF
biomcp gene articles BRCA1
biomcp disease trials melanoma
biomcp drug adverse-events pembrolizumab
biomcp protein structures P15056
```

Rules:

- Helpers usually take only the ID/name. Do not invent extra filters for helpers.
- If you need date filters, sort, disease filters, or drug filters, use `search article` or `search trial`.
- For FDA adverse-event filtering, use `search adverse-event --drug <name> ...`. Do not attach filters to `drug adverse-events <name>`.
- When a search result returns a multi-word drug name such as `"erlotinib hydrochloride"`, copy it exactly and quote it in `get drug`.

## Variant Rules

1. Always quote variant IDs in every command, including helpers.

```bash
biomcp get variant "BRAF V600E" clinvar
biomcp get variant "chr7:g.140453136A>T" predictions
biomcp variant trials "chr7:g.140453136A>T"
biomcp variant articles "rs113488022"
```

2. Keep using the original variant ID through the workflow unless the task explicitly requires a different identifier format. Do not switch from `"BRAF V600E"` to HGVS just because the output mentions an HGVS alias.

3. For variant-specific literature, use:

```bash
biomcp variant articles "BRAF V600E"
```

`search article` does not have a variant filter.

4. Do not invent sections. `get variant ... oncokb` is invalid.

5. Avoid token-gated helpers unless the task explicitly requires them and the environment is configured. In this environment, prefer `clinvar`, `predictions`, `population`, `civic`, `cgi`, `cbioportal`, articles, and trials before `variant oncokb`.

6. Exon-level labels and free-text alteration names are not safe `get variant` IDs. Do not write commands like:

```bash
biomcp get variant "EGFR Exon 19 Deletion" ...
```

For exon 19 deletions, exon 20 insertions, or other complex alterations:

- use `search variant ...` first
- only `get variant` if BioMCP returned an exact rsID or HGVS ID
- otherwise summarize from search/article/trial evidence without forcing `get variant`

7. `search variant --consequence` only accepts documented ontology terms. Use values like `missense_variant`, `inframe_deletion`, or `inframe_insertion`. Do not invent generic values like `deletion`, `insertion`, or `mutation`.

## Deterministic Variant Pathogenicity Workflow

For a focused question like "Is variant X pathogenic? What is the clinical evidence?", use this pattern first and stop once supported:

```bash
biomcp get variant "<id>" clinvar predictions population
biomcp get variant "<id>" civic cgi
biomcp variant trials "<id>"
biomcp variant articles "<id>"
```

Only add more commands if a needed claim is still unsupported.

## Deterministic Drug Safety Workflow

For a focused question like "What are the safety concerns with drug X?" use one of these exact patterns:

Quick safety summary:

```bash
biomcp get drug <name> label interactions approvals
biomcp drug adverse-events <name>
```

Filtered FDA adverse-event check:

```bash
biomcp get drug <name> label interactions approvals
biomcp search adverse-event --drug <name> --outcome death --limit 10
```

Do not write `biomcp drug adverse-events <name> --outcome ...`.

## Deterministic Broad Gene-Disease Workflow

For questions like "Tell me everything relevant about EGFR in NSCLC", use one orienting pass and then a small number of focused follow-ups:

```bash
biomcp search all --gene <gene> --disease "<disease>" --counts-only
biomcp get gene <gene> pathways diseases protein druggability civic
biomcp search drug --target <gene> --indication "<disease>" --limit 10
biomcp search trial -c "<disease>" --mutation "<gene>" --status recruiting --limit 10
biomcp search article -g <gene> -d "<disease>" --sort citations --limit 10
```

Rules:

- do not run `search disease` unless you need an ontology ID or phenotype sections
- do not use free-text `search drug` when `--target` or `--indication` is enough
- do not run both `search drug <gene>` and `search drug --target <gene>` in the same investigation
- `get variant` only for simple substitutions or exact IDs copied from search results
- do not `get variant` on exon-level free text like `"Exon 19 Deletion"`
- for EGFR/NSCLC, cover exon 19 deletions and exon 20 insertions from disease, drug, trial, or article evidence unless an exact variant ID is surfaced
- if you need a variant deep dive, choose at most two exemplar simple substitutions such as `L858R` and `T790M`
- choose at most two exemplar variants for deep follow-up
- choose at most three representative EGFR drugs for deep follow-up; do not fetch near-duplicates like both `erlotinib` and `erlotinib hydrochloride` unless the distinction matters
- fetch only one or two key articles or trials unless the prompt explicitly asks for exhaustive evidence
- stop once you can cover: gene role/pathway, actionable alterations, approved drugs, active trials, and resistance mechanisms

## Deterministic Drug Resistance Workflow

For questions like "What genes does drug X target and what are the resistance mechanisms?", use this compact pattern:

```bash
biomcp search all --drug <name> --counts-only
biomcp get drug <name> targets label civic
biomcp search article --drug <name> -k resistance --type review --sort citations --limit 5
biomcp search article -k "<drug> resistance mechanism" --sort citations --limit 5
biomcp get article <PMID>
biomcp get gene <primary_target> pathways
```

Rules:

- stop after you have 3 to 5 named mechanisms with article support
- do not keep launching near-duplicate keyword searches once the mechanism list is stable
- prefer one review article plus one or two landmark papers over many repetitive searches

## Common Real Sections

- gene: `pathways`, `ontology`, `diseases`, `protein`, `go`, `interactions`, `civic`, `expression`, `druggability`, `clingen`
- variant: `clinvar`, `predict`, `predictions`, `population`, `conservation`, `civic`, `cgi`, `cbioportal`, `gwas`
- article: `annotations`, `fulltext`
- trial: `eligibility`, `locations`, `outcomes`, `arms`, `references`
- drug: `label`, `targets`, `shortage`, `indications`, `interactions`, `approvals`, `civic`
- disease: `genes`, `pathways`, `phenotypes`, `variants`, `models`, `prevalence`, `civic`
- pathway: `genes`, `events`, `enrichment`
- protein: `domains`, `interactions`, `structures`

## Evidence Discipline

- Only claim facts the current outputs support.
- If you need a mechanism, approval, trial criterion, or article detail, fetch the section or article that shows it.
- Prefer source-tied phrasing such as `ClinVar shows...`, `CIViC reports...`, or `the retrieved trials include...`.
- If an exact numeric count or score is not clearly visible in the current output, summarize qualitatively instead of guessing a number.
- Avoid words like `definitive`, `overwhelming`, or `proves` unless the retrieved evidence directly justifies that level of certainty.
- If one command already answers the question, do not keep searching.

## Efficiency Target

Focused tasks should usually take `4-12` BioMCP commands. Broad investigations may need more.
