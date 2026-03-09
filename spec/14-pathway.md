# Pathway Queries

Pathway search should normalize a small set of confirmed alias phrases before querying Reactome. These checks focus on the long-form MAPK regression without relying on unstable upstream totals.

| Section | Command focus | Why it matters |
|---|---|---|
| Long-form alias search | `search pathway 'mitogen activated protein kinase'` | Confirms alias normalization to MAPK |

## Long-Form MAPK Alias

The confirmed long-form MAPK phrase should return MAPK-named pathways instead of unrelated protein kinase results. This guards the narrow alias-normalization fix introduced for pathway search.

```bash
out="$(/home/ian/workspace/worktrees/P028-biomcp/target/release/biomcp search pathway "mitogen activated protein kinase" --limit 5)"
echo "$out" | mustmatch like "# Pathways: mitogen activated protein kinase"
echo "$out" | mustmatch like "| ID | Name |"
echo "$out" | mustmatch like "MAPK"
```
