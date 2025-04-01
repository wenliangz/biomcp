# Variants CLI

## Overview

The Variants CLI allows users to search for and retrieve genetic variant information using the MyVariant.info API. This CLI is useful for quickly finding variant details based on gene name, protein change, genomic location, or other parameters.

> **API Documentation**: For details about the underlying API, see the [MyVariant.info API Documentation](../apis/myvariant_info.md).

## Usage

```bash
biomcp variant [COMMAND] [OPTIONS]
```

### Commands

- `search`: Search for variants based on various parameters
- `get`: Retrieve detailed information about a specific variant

## search

Search for genetic variants using multiple parameters and filters.

### Options

#### Basic Search Parameters

- `-g, --gene [GENE]`: Gene symbol to search for (e.g., BRAF, TP53)
- `-p, --protein [PROTEIN]`: Protein change notation (e.g., p.V600E)
- `-c, --cdna [CDNA]`: cDNA notation (e.g., c.1799T>A)
- `-r, --rsid [RSID]`: dbSNP rsID (e.g., rs113488022)
- `-l, --region [REGION]`: Genomic region in format chr:start-end (e.g., chr7:140453100-140453200)

#### Clinical and Functional Filters

- `-s, --significance [SIGNIFICANCE]`: ClinVar clinical significance (e.g., Pathogenic, Likely_pathogenic)
- `--max-frequency [MAX_FREQUENCY]`: Maximum population frequency threshold (e.g., 0.01)
- `--min-frequency [MIN_FREQUENCY]`: Minimum population frequency threshold (e.g., 0.001)
- `--cadd [CADD]`: Minimum CADD phred score (e.g., 15)
- `--polyphen [POLYPHEN]`: PolyPhen-2 prediction (e.g., probably_damaging, possibly_damaging, benign)
- `--sift [SIFT]`: SIFT prediction (e.g., deleterious, tolerated)

#### Output Options

- `--fields [FIELDS]`: Comma-separated list of fields to return in results
- `--sources [SOURCES]`: Include specific data sources in the results
- `--size [SIZE]`: Number of results to return (default: 10)
- `--from [FROM]`: Result offset for pagination (default: 0)
- `--sort [SORT]`: Field to sort results by (e.g., cadd.phred:desc)
- `--format [FORMAT]`: Output format (markdown, json, table)

#### Integration Options

- `--related-articles`: Search for related articles for each variant
- `--related-trials`: Search for related clinical trials for each variant

### Examples

Search for a variant by gene and protein change:

```bash
biomcp variant search --gene BRAF --protein p.V600E
```

Search for pathogenic variants in a gene:

```bash
biomcp variant search --gene TP53 --significance Pathogenic
```

Search with complex filtering:

```bash
biomcp variant search --gene BRAF --max-frequency 0.01 --cadd 20 --related-articles
```

Search by genomic region:

```bash
biomcp variant search --region chr7:140453100-140453200
```

## get

Retrieve detailed information about a specific variant by its identifier.

### Options

- `--id [ID]`: Variant ID in HGVS format (e.g., chr7:g.140453136A>T)
- `--rsid [RSID]`: dbSNP rsID (alternative to ID, e.g., rs113488022)
- `--fields [FIELDS]`: Comma-separated list of fields to return
- `--sources [SOURCES]`: Include specific data sources in the results
- `--format [FORMAT]`: Output format (markdown, json, table)
- `--related-articles`: Include related articles in the output
- `--related-trials`: Include related clinical trials in the output

### Examples

Get a variant by HGVS ID:

```bash
biomcp variant get --id chr7:g.140453136A>T
```

Get a variant by rsID with related articles:

```bash
biomcp variant get --rsid rs113488022 --related-articles
```

## Output

By default, the CLI outputs variant information in Markdown format for easy reading. The default fields included are:

- Variant ID (HGVS format)
- dbSNP rsID
- Gene name
- Clinical significance
- CADD phred score
- gnomAD exome allele frequency
- ExAC allele frequency

Example output:

```
## Variant: chr7:g.140453136A>T (BRAF V600E)

### Basic Information
- **ID**: chr7:g.140453136A>T
- **dbSNP**: rs113488022
- **Gene**: BRAF
- **cDNA Change**: c.1799T>A
- **Protein Change**: p.V600E

### Clinical Information
- **ClinVar Significance**: Pathogenic
- **CADD Phred**: 32.0
- **PolyPhen-2**: Probably_damaging (0.998)
- **SIFT**: Deleterious (0.01)

### Population Frequency
- **gnomAD Exome**: 0.00000397994
- **ExAC**: 0.00001647
```

## Advanced Usage

### Combining Multiple Parameters

You can combine multiple search parameters to create complex queries:

```bash
biomcp variant search --gene BRAF --protein p.V600E --cadd 20 --max-frequency 0.001
```

### Using Field Selection

Specify which fields to include in the output:

```bash
biomcp variant search --gene BRAF --fields "_id,dbsnp.rsid,dbnsfp.genename,clinvar.clinical_significance"
```

### Integration with Other Tools

Find variants and related information in one command:

```bash
biomcp variant search --gene BRAF --significance Pathogenic --related-articles --related-trials
```
