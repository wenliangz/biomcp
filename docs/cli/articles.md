# Articles CLI Documentation

The Articles CLI module provides commands for searching and retrieving biomedical research articles from PubMed.

> **API Documentation**: For details about the underlying API, see the [PubTator3 API Documentation](../apis/pubtator3_api.md).

## Search Command

Search for biomedical research articles based on various filters.

### Usage

```bash
biomcp article search [OPTIONS]
```

### Options

- `-g, --gene [GENE]`: Gene name to search for (can specify multiple times)
- `-v, --variant [VARIANT]`: Genetic variant to search for (can specify multiple times)
- `-d, --disease [DISEASE]`: Disease to search for (can specify multiple times)
- `-c, --chemical [CHEMICAL]`: Chemical or drug to search for (can specify multiple times)
- `-k, --keyword [KEYWORD]`: Additional keyword to search for (can specify multiple times)
- `-p, --page INTEGER`: Page number for pagination (starts at 1) [default: 1]
- `--help`: Show help message and exit

### Examples

Search for articles about the BRAF gene:

```bash
biomcp article search --gene BRAF
```

Search for articles about the BRAF V600E mutation in melanoma:

```bash
biomcp article search --gene BRAF --variant "BRAF V600E" --disease Melanoma
```

Search with multiple filters:

```bash
biomcp article search --gene BRAF --gene KRAS --disease Melanoma
```

Go to page 2 of results:

```bash
biomcp article search --gene BRAF --page 2
```

## Get Command

Retrieve articles by their PubMed ID (PMID).

### Usage

```bash
biomcp article get [OPTIONS] PMIDS...
```

### Arguments

- `PMIDS`: PubMed IDs of articles to retrieve (one or more required)

### Options

- `-f, --full`: Retrieve full text instead of just abstract
- `--help`: Show help message and exit

### Examples

Get article abstract by PMID:

```bash
biomcp article get 21717063
```

Get multiple articles:

```bash
biomcp article get 21717063 22301848
```

Get full text (when available):

```bash
biomcp article get 21717063 --full
```
