# Skill Workflows

BioMCP skills package repeatable, multi-step investigation flows as runnable guidance. This file validates skill discovery and loading, then checks two representative commands used by the variant-to-treatment workflow. Assertions prioritize workflow headers and stable structural outputs.

| Section | Command focus | Why it matters |
|---|---|---|
| List skills | `biomcp skill list` | Confirms workflow catalog availability |
| Open numeric skill | `biomcp skill 01` | Confirms index-based skill retrieval |
| Open slug skill | `biomcp skill variant-to-treatment` | Confirms slug-based retrieval |
| Variant interpretation step | `get variant "BRAF V600E" clinvar` | Confirms clinical interpretation building block |
| Trial pivot step | `variant trials "BRAF V600E"` | Confirms treatment-option discovery building block |

## Listing Skills

Skill listing is the workflow entrypoint and should expose stable names for navigation. We assert on two canonical skill slugs.

```bash
out="$(biomcp skill list)"
echo "$out" | mustmatch like "variant-to-treatment"
echo "$out" | mustmatch like "drug-investigation"
```

## Viewing a Skill by Number

Numeric addressing is convenient for quick access from documentation and dispatch logs. The loaded skill should render pattern heading and workflow section labels.

```bash
out="$(biomcp skill 01)"
echo "$out" | mustmatch like "# Pattern: Variant to Treatment"
echo "$out" | mustmatch like "## Full Workflow"
```

## Viewing a Skill by Slug

Slug addressing is stable across environments where numeric ordering may change. This check verifies the same workflow can be loaded by canonical slug.

```bash
out="$(biomcp skill variant-to-treatment)"
echo "$out" | mustmatch like "# Pattern: Variant to Treatment"
echo "$out" | mustmatch like "biomcp variant trials"
```

## Workflow Step: Variant Interpretation

The variant-to-treatment pattern starts with variant interpretation and clinical evidence context. We assert on ClinVar section rendering and the stable rsID marker.

```bash
out="$(biomcp get variant "BRAF V600E" clinvar)"
echo "$out" | mustmatch like "## ClinVar"
echo "$out" | mustmatch like "Variant ID:"
```

## Workflow Step: Trial Pivot

After interpretation, the workflow pivots into mutation-aligned trial search. The output should preserve mutation query context and the trial table schema.

```bash
out="$(biomcp variant trials "BRAF V600E" --limit 3)"
echo "$out" | mustmatch like "Query: mutation=BRAF V600E"
echo "$out" | mustmatch like "|NCT ID|Title|Status|Phase|Conditions|"
```
