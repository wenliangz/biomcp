# Pattern: Gene-in-disease orientation

Use this when the question names both a gene and a disease but the next pivot is still unclear.

```bash
biomcp search all --gene BRAF --disease "melanoma"
biomcp get gene BRAF protein hpa
biomcp search article -g BRAF -d "melanoma" --type review --limit 5
```

Interpretation:
- `search all` gives the first cross-entity map.
- Deepen into the gene card only after the orientation step tells you which surface matters next.
