# Pattern: Symptom / phenotype lookup

Use this when the question is "what symptoms or phenotypes are linked to X?"

```bash
biomcp get disease "Marfan syndrome" phenotypes
biomcp search article -d "Marfan syndrome" --type review --limit 5
```

Interpretation:
- Start with the phenotype section for normalized HPO-backed findings.
- Supplement with review literature when the phenotype list is short or the question needs fuller clinical presentation.
