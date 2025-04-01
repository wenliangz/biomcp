# BioMCP Common Workflows

This document outlines common workflows that span multiple BioMCP tools and
APIs, demonstrating how to effectively combine different components to
accomplish complex research tasks.

## Finding Clinical Trials Related to a Specific Gene Variant

This workflow demonstrates how to find clinical trials that are investigating a
specific gene variant.

### Step 1: Identify the Variant

First, search for the variant of interest using the Variants CLI:

```bash
biomcp variant search --gene BRAF --protein p.V600E
```

This will return information about the BRAF V600E variant, including its ID,
clinical significance, and population frequencies.

### Step 2: Find Articles Mentioning the Variant

Search for articles that discuss this variant:

```bash
biomcp article search --gene BRAF --variant "V600E"
```

Review the articles to understand the clinical context of the variant.

### Step 3: Find Clinical Trials for the Variant

Search for clinical trials related to this variant:

```bash
biomcp trial search --term "BRAF V600E" --status Recruiting
```

This will provide a list of clinical trials that are actively recruiting
participants for studies involving the BRAF V600E variant.

### Integrated Command

The above workflow can be simplified using the related-trials flag in the
variant search command:

```bash
biomcp variant search --gene BRAF --protein p.V600E --related-trials
```

## Researching Disease Treatments

This workflow demonstrates how to research treatments for a specific disease.

### Step 1: Find Articles About the Disease

Search for articles that discuss the disease:

```bash
biomcp article search --disease "Melanoma" --limit 10
```

Review these articles to understand the current research landscape.

### Step 2: Identify Key Treatments

From the articles, identify key treatments or drugs for the disease. Then
search for articles specific to those treatments:

```bash
biomcp article search --disease "Melanoma" --chemical "Vemurafenib"
```

### Step 3: Find Clinical Trials for the Treatments

Search for clinical trials investigating these treatments:

```bash
biomcp trial search --condition "Melanoma" --intervention "Vemurafenib" --status Recruiting
```

### Step 4: Explore Genetic Variants Related to Treatment Response

If applicable, search for genetic variants associated with treatment response:

```bash
biomcp variant search --gene BRAF --significance Pathogenic
```

## Exploring Genetic Variants Associated with a Disease

This workflow demonstrates how to research genetic variants associated with a
specific disease.

### Step 1: Search for Articles About the Disease-Gene Association

```bash
biomcp article search --disease "Cystic Fibrosis" --gene "CFTR"
```

### Step 2: Identify Specific Variants

From the articles, identify specific variants of interest, then search for
detailed information:

```bash
biomcp variant search --gene CFTR --significance Pathogenic
```

### Step 3: Explore Clinical Trials for These Variants

Search for clinical trials targeting these variants:

```bash
biomcp trial search --condition "Cystic Fibrosis" --term "CFTR modulator"
```

## Integration with External Tools

BioMCP data can be easily exported for use with other bioinformatics tools:

### Export Variant Data for Analysis

```bash
biomcp variant search --gene TP53 --significance Pathogenic --format json > tp53_variants.json
```

### Export Clinical Trial Details

```bash
biomcp trial get NCT04267848 --format json > trial_details.json
```

### Export Article Information

```bash
biomcp article search --gene BRAF --variant "V600E" --limit 50 --format json > braf_articles.json
```

## Advanced Data Integration

For advanced users, BioMCP commands can be combined using shell scripts or
pipelines. For example:

### Comprehensive Gene Research Script

```bash
#!/bin/bash
GENE="BRAF"
VARIANT="V600E"
DISEASE="Melanoma"

echo "Finding variant information..."
biomcp variant search --gene $GENE --protein p.$VARIANT

echo "Finding recent articles..."
biomcp article search --gene $GENE --variant $VARIANT --limit 5

echo "Finding active clinical trials..."
biomcp trial search --condition $DISEASE --term "$GENE $VARIANT" --status Recruiting
```

## Best Practices for Multi-Tool Workflows

1. **Start broad, then narrow**: Begin with broader searches, then use the
   results to refine your subsequent searches.

2. **Use consistent terminology**: When searching across different tools, use
   consistent terminology for genes, variants, and diseases.

3. **Save intermediate results**: For complex workflows, consider saving
   intermediate results to files for reference.

4. **Combine command flags efficiently**: Many commands support multiple
   filters - use them together to get more precise results.

5. **Consider output formats**: Use the appropriate output format (markdown,
   json, table) based on your needs.

6. **Rate limit awareness**: Be mindful of API rate limits when running
   multiple commands in sequence, especially for batch operations.

## Learn More

- [Trials CLI Documentation](cli/trials.md)
- [Articles CLI Documentation](cli/articles.md)
- [Variants CLI Documentation](cli/variants.md)
- [ClinicalTrials.gov API Documentation](apis/clinicaltrials_gov.md)
- [PubTator3 API Documentation](apis/pubtator3_api.md)
- [MyVariant.info API Documentation](apis/myvariant_info.md)
