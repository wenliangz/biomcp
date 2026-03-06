# Skill Workflows

BioMCP now ships one primary agent-facing `SKILL.md` and no embedded use-case catalog files. This file validates the new skill-list behavior, expected not-found responses for legacy use-case lookups, and two representative commands used by investigation workflows.

| Section | Command focus | Why it matters |
|---|---|---|
| List skills | `biomcp skill list` | Confirms empty catalog behavior is explicit |
| Open numeric skill | `biomcp skill 01` | Confirms legacy numeric lookups fail clearly |
| Open slug skill | `biomcp skill variant-to-treatment` | Confirms legacy slug lookups fail clearly |
| Variant interpretation step | `get variant "BRAF V600E" clinvar` | Confirms clinical interpretation building block |
| Trial pivot step | `variant trials "BRAF V600E"` | Confirms treatment-option discovery building block |

## Listing Skills

Skill listing should now clearly indicate there are no embedded use-case files.

```bash
out="$(biomcp skill list)"
echo "$out" | mustmatch like "No skills found"
```

## Viewing a Skill by Number

Numeric addressing previously selected embedded use-cases. With the catalog removed, the command should fail with a clear not-found message.

```bash
out="$(biomcp skill 01 2>&1 || true)"
echo "$out" | mustmatch like "skill '01' not found"
echo "$out" | mustmatch like "Try: biomcp skill list"
```

## Viewing a Skill by Slug

Slug addressing for legacy use-cases should also fail with a clear not-found message.

```bash
out="$(biomcp skill variant-to-treatment 2>&1 || true)"
echo "$out" | mustmatch like "skill 'variant-to-treatment' not found"
echo "$out" | mustmatch like "Try: biomcp skill list"
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
