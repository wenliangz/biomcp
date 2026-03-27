# Guide Workflow Docs Contract

This spec protects the public docs page that mirrors the embedded BioMCP guide
workflows. It asserts the stable docs surfaces only: rendered markdown
structure, exact command lines, workflow guardrails, and the discoverability
links that route new users to the page.

These checks are intentionally doc-only. They do not invoke `biomcp`.

## Page Structure

The public page should keep the three workflow sections plus the evidence
discipline section that tells readers how to keep claims traceable.

```bash
doc="$(cat "$(git rev-parse --show-toplevel)/docs/how-to/guide-workflows.md")"
echo "$doc" | mustmatch like "# How to: follow guide workflows"
echo "$doc" | mustmatch like "## Variant Pathogenicity Workflow"
echo "$doc" | mustmatch like "## Drug Safety Workflow"
echo "$doc" | mustmatch like "## Broad Gene-Disease Workflow"
echo "$doc" | mustmatch like "## Evidence Discipline"
```

## Exact Workflow Commands

The public docs must keep the same deterministic command lines the embedded
guide teaches.

```bash
doc="$(cat "$(git rev-parse --show-toplevel)/docs/how-to/guide-workflows.md")"
echo "$doc" | mustmatch like 'biomcp get variant "<id>" clinvar predictions population'
echo "$doc" | mustmatch like 'biomcp get variant "<id>" civic cgi'
echo "$doc" | mustmatch like 'biomcp variant trials "<id>"'
echo "$doc" | mustmatch like 'biomcp variant articles "<id>"'
```

```bash
doc="$(cat "$(git rev-parse --show-toplevel)/docs/how-to/guide-workflows.md")"
echo "$doc" | mustmatch like 'biomcp get drug <name> label interactions approvals'
echo "$doc" | mustmatch like 'biomcp drug adverse-events <name>'
echo "$doc" | mustmatch like 'biomcp search adverse-event --drug <name> --outcome death --limit 10'
echo "$doc" | mustmatch like 'Do not write `biomcp drug adverse-events <name> --outcome ...`.'
```

```bash
doc="$(cat "$(git rev-parse --show-toplevel)/docs/how-to/guide-workflows.md")"
echo "$doc" | mustmatch like 'biomcp search all --gene <gene> --disease "<disease>" --counts-only'
echo "$doc" | mustmatch like 'biomcp get gene <gene> pathways diseases protein druggability civic'
echo "$doc" | mustmatch like 'biomcp search drug --target <gene> --indication "<disease>" --limit 10'
echo "$doc" | mustmatch like 'biomcp search trial -c "<disease>" --mutation "<gene>" --status recruiting --limit 10'
echo "$doc" | mustmatch like 'biomcp search article -g <gene> -d "<disease>" --sort citations --limit 10'
```

## Guardrails and Evidence Traceability

The page should keep the same workflow constraints and teach readers to carry
forward rerunnable evidence IDs.

```bash
doc="$(cat "$(git rev-parse --show-toplevel)/docs/how-to/guide-workflows.md")"
echo "$doc" | mustmatch like 'do not run both `search drug <gene>` and `search drug --target <gene>` in the same investigation'
echo "$doc" | mustmatch like 'do not `get variant` on exon-level free text like `"Exon 19 Deletion"`'
echo "$doc" | mustmatch like 'keep the IDs that make the evidence rerunnable, such as variant IDs, PMIDs, and NCT IDs'
echo "$doc" | mustmatch like 'prefer source-tied phrasing'
```

## Discoverability Surfaces

The skills onboarding page and the docs nav should both route a newcomer to
the public workflow page.

```bash
skills="$(cat "$(git rev-parse --show-toplevel)/docs/getting-started/skills.md")"
echo "$skills" | mustmatch like "## Learn the workflows"
echo "$skills" | mustmatch like "../how-to/guide-workflows.md"
```

```bash
nav="$(cat "$(git rev-parse --show-toplevel)/mkdocs.yml")"
echo "$nav" | mustmatch like "Guide Workflows: how-to/guide-workflows.md"
```
