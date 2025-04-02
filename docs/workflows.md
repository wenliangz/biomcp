# BioMCP Common Workflows

This document outlines common workflows that span multiple BioMCP tools and
APIs, demonstrating how to effectively combine different components to
accomplish complex research tasks using the CLI.

## Finding Clinical Trials Related to a Specific Gene Variant

This workflow demonstrates how to find clinical trials that are investigating a
specific gene variant, like BRAF V600E.

### Step 1: Identify the Variant

First, search for the variant of interest using the Variants CLI to confirm its details and identifiers:

```bash
biomcp variant search --gene BRAF --hgvsp p.V600E
```

This will return information about the BRAF V600E variant, including its standard ID (e.g., chr7:g.140453136A>T), clinical significance, and population frequencies. Note the precise identifiers if needed for subsequent searches.

### Step 2: Find Articles Mentioning the Variant

Search for articles that discuss this variant:

```bash
biomcp article search --gene BRAF --variant "BRAF V600E"
```

Review the articles to understand the clinical context, treatment landscape, and ongoing research related to the variant.

### Step 3: Find Clinical Trials for the Variant

Search for clinical trials related to this variant, using terms identified from the previous steps. Ensure the status is set appropriately (e.g., OPEN for recruiting trials):

```bash
biomcp trial search --term "BRAF V600E" --status OPEN
```

This will provide a list of clinical trials that are actively recruiting or soon to recruit participants for studies involving the BRAF V600E variant. You might refine the search further using `--condition` or `--intervention` based on your research focus.

## Researching Disease Treatments

This workflow demonstrates how to research treatments for a specific disease, like Melanoma.

### Step 1: Find Articles About the Disease

Search for recent articles discussing the disease:

```bash
biomcp article search --disease "Melanoma"
```

Review these articles to understand the current research landscape, standard-of-care treatments, and emerging therapies.

### Step 2: Identify Key Treatments and Research Them

From the articles, identify key treatments or drugs (e.g., Vemurafenib). Then search for articles specific to those treatments within the disease context:

```bash
biomcp article search --disease "Melanoma" --chemical "Vemurafenib"
```

### Step 3: Find Clinical Trials for the Treatments

Search for clinical trials investigating these treatments for the specific disease:

```bash
biomcp trial search --condition "Melanoma" --intervention "Vemurafenib" --status OPEN
```

### Step 4: Explore Genetic Variants Related to Treatment Response

If applicable (e.g., targeted therapies), search for genetic variants known to be associated with treatment response or resistance:

```bash
# Example: Find pathogenic BRAF variants relevant to melanoma treatment
biomcp variant search --gene BRAF --significance pathogenic --sources civic
```

## Exploring Genetic Variants Associated with a Disease

This workflow demonstrates how to research genetic variants associated with a
specific disease, like Cystic Fibrosis.

### Step 1: Search for Articles About the Disease-Gene Association

```bash
biomcp article search --disease "Cystic Fibrosis" --gene "CFTR"
```

### Step 2: Identify Specific Variants

From the articles or prior knowledge, identify specific variants of interest. Search for detailed information on known pathogenic variants in the gene:

```bash
biomcp variant search --gene CFTR --significance Pathogenic
```

### Step 3: Explore Clinical Trials Targeting These Variants or the Pathway

Search for clinical trials targeting treatments related to these variants or the affected pathway:

```bash
biomcp trial search --condition "Cystic Fibrosis" --term "CFTR modulator" --status OPEN
```

## Integration with External Tools

BioMCP data can be easily exported in JSON format for use with other bioinformatics tools or scripts. Use the `--json` flag with most search or get commands.

### Export Variant Data for Analysis

```bash
biomcp variant search --gene TP53 --significance Pathogenic --json > tp53_variants.json
```

### Export Clinical Trial Details

```bash
biomcp trial get NCT04267848 --json > trial_details.json
```

### Export Article Information

```bash
biomcp article search --gene BRAF --variant "V600E" --json > braf_articles.json
```

## Advanced Data Integration

For advanced users, BioMCP commands can be combined using shell scripts or pipelines.

### Comprehensive Gene Research Script (Bash Example)

```bash
#!/bin/bash
GENE="BRAF"
PROTEIN_CHANGE="p.V600E"
DISEASE="Melanoma"

echo "--- Finding Variant Information for $GENE $PROTEIN_CHANGE ---"
biomcp variant search --gene "$GENE" --hgvsp "$PROTEIN_CHANGE" --size 1

echo -e "\n--- Finding Recent Articles (Max 5) ---"
biomcp article search --gene "$GENE" --variant "$GENE $PROTEIN_CHANGE"

echo -e "\n--- Finding Active Clinical Trials ---"
biomcp trial search --condition "$DISEASE" --term "$GENE $PROTEIN_CHANGE" --status OPEN
```

### Programmatic Integration (Python Example)

BioMCP can also be used as a Python library. This allows for more complex integrations and data processing within Python scripts. (See [Python SDK Guide](python_sdk.md) for details).

```python
import asyncio

# Import necessary functions and models
from biomcp_python.variants.search import search_variants, VariantQuery
from biomcp_python.trials.search import search_trials, TrialQuery
from biomcp_python.articles.search import search_articles, PubmedRequest

async def research_braf_v600e():
    gene = "BRAF"
    protein_change = "p.V600E"
    disease = "Melanoma"
    variant_term = "BRAF V600E" # Term for article/trial search

    print(f"--- Researching {variant_term} in {disease} ---")

    # 1. Get Variant Info (as JSON)
    print("\nFetching Variant Details...")
    variant_query = VariantQuery(gene=gene, hgvsp=protein_change, size=1)
    # Assuming search_variants returns Markdown by default
    variant_md = await search_variants(variant_query)
    print(variant_md) # Print Markdown directly

    # 2. Find Articles (as JSON)
    print("\nFetching Related Articles...")
    article_query = PubmedRequest(genes=[gene], variants=[variant_term], diseases=[disease], limit=5)
    # Assume function can return JSON directly if needed, here using Markdown
    article_md = await search_articles(article_query)
    print(article_md)

    # 3. Find Trials (as JSON)
    print("\nFetching Clinical Trials...")
    trial_query = TrialQuery(conditions=[disease], terms=[variant_term], recruiting_status="OPEN")
    # Assume function can return JSON directly if needed, here using Markdown
    trial_md = await search_trials(trial_query)
    print(trial_md)

if __name__ == "__main__":
    asyncio.run(research_braf_v600e())
```

## Best Practices for Multi-Tool Workflows

- **Start Specific, then Broaden (or vice-versa):** Depending on your goal, either start with a specific entity (like a variant) and find related info, or start broad (like a disease) and narrow down to specific treatments or genes.

- **Use Consistent Terminology:** Employ standardized names for genes (e.g., BRAF), diseases (e.g., Melanoma), and variants (e.g., p.V600E for protein, BRAF V600E as a search term) across searches where appropriate.

- **Leverage Identifiers:** Use specific identifiers returned by one command (like a variant's HGVS ID or an article's PMID) as input for subsequent commands (variant get, article get) for precise retrieval.

- **Use --json for Integration:** When piping output to other tools or processing results programmatically, use the `--json` flag for structured data.

- **Combine Filters:** Use multiple filter options within a single command (`--condition`, `--intervention`, `--status` for trials; `--gene`, `--significance`, `--max-frequency` for variants) to refine results efficiently.

- **Check --help:** Use `biomcp [command] --help` (e.g., `biomcp trial search --help`) to see all available filters and options for any command.

- **Rate Limit Awareness:** Be mindful of potential rate limits of the underlying public APIs (ClinicalTrials.gov, PubTator3, MyVariant.info) when running many commands in quick succession, especially in automated scripts. BioMCP includes caching to help mitigate this.
