# Python SDK Guide (Library Usage)

Beyond its command-line interface, BioMCP is structured as a Python library, allowing you to integrate its data access capabilities directly into your Python applications and workflows.

## Installation

Ensure `biomcp-python` is installed in your Python environment. See the [Installation Guide](installation.md).

```bash
pip install biomcp-python
```

## Core Concepts

**Asynchronous Operations:** Most data fetching functions in BioMCP are async because they perform network requests. You will need to use Python's `asyncio` library (or another async framework like `anyio`) to run them.

**Pydantic Models for Input:** Search functions typically accept Pydantic models as input (`VariantQuery`, `TrialQuery`, `PubmedRequest`). This provides data validation and clarity on required/optional parameters.

**Output Format:** By default, functions usually return results as Markdown strings, suitable for display. Many functions also accept an `output_json=True` argument to return results as a JSON string, which is easier to parse programmatically. Check function signatures for availability.

## Importing

Import the necessary functions and models from the relevant submodules:

```python
import asyncio

# Variant functions and models
from biomcp.variants.search import search_variants, VariantQuery
from biomcp.variants.getter import get_variant

# Trial functions and models
from biomcp.trials.search import search_trials, TrialQuery, RecruitingStatus, TrialPhase
from biomcp.trials.getter import get_trial, Module as TrialModule

# Article functions and models
from biomcp.articles.search import search_articles, PubmedRequest
from biomcp.articles.fetch import fetch_articles

# For parsing JSON results
import json
```

## Examples

Here are examples demonstrating how to call the core functions programmatically.

### Working with Variants

#### Searching Variants

```python
async def find_pathogenic_tp53():
    query = VariantQuery(
        gene="TP53",
        significance="pathogenic",
        size=5 # Number of results to return
    )
    # Get results as Markdown (default)
    markdown_output = await search_variants(query)
    print("--- Pathogenic TP53 Variants (Markdown) ---")
    print(markdown_output)

    # Get results as JSON string
    json_output_str = await search_variants(query, output_json=True)
    print("\n--- Pathogenic TP53 Variants (JSON) ---")
    # Parse the JSON string
    data = json.loads(json_output_str)
    print(f"Found {len(data)} variants.")
    if data:
        print(f"First variant ID: {data[0].get('_id')}")
        # Process the list of variant dictionaries (data)
        # ...

# Run the async function
asyncio.run(find_pathogenic_tp53())
```

#### Getting Specific Variant Details

```python
async def get_braf_v600e_details():
    variant_id = "rs113488022" # Can also use "chr7:g.140453136A>T"

    # Get results as Markdown
    markdown_output = await get_variant(variant_id)
    print(f"--- Details for {variant_id} (Markdown) ---")
    print(markdown_output)

    # Get results as JSON string
    json_output_str = await get_variant(variant_id, output_json=True)
    print(f"\n--- Details for {variant_id} (JSON) ---")
    data = json.loads(json_output_str)
    # Data is typically a list containing one variant dictionary
    if data:
         print(f"Gene: {data[0].get('dbnsfp', {}).get('genename')}")
         print(f"ClinVar Significance: {data[0].get('clinvar', {}).get('rcv', {}).get('clinical_significance')}")
         # Process the variant dictionary (data[0])
         # ...

asyncio.run(get_braf_v600e_details())
```

### Working with Clinical Trials

#### Searching Trials

```python
async def find_melanoma_trials():
    query = TrialQuery(
        conditions=["Melanoma"],
        interventions=["Pembrolizumab"],
        recruiting_status=RecruitingStatus.OPEN,
        phase=TrialPhase.PHASE3
    )

    # Get results as Markdown
    markdown_output = await search_trials(query)
    print("--- Recruiting Phase 3 Pembrolizumab Melanoma Trials (Markdown) ---")
    print(markdown_output)

    # Get results as JSON string
    json_output_str = await search_trials(query, output_json=True)
    print("\n--- Recruiting Phase 3 Pembrolizumab Melanoma Trials (JSON) ---")
    data = json.loads(json_output_str)
    # Process the trial search results (list of dicts or error dict)
    if isinstance(data, list) and data:
         print(f"Found {len(data)} trials on this page.")
         print(f"First trial NCT ID: {data[0].get('NCT Number')}")
         # ...
    elif isinstance(data, dict) and 'error' in data:
         print(f"Error: {data['error']}")

asyncio.run(find_melanoma_trials())
```

#### Getting Specific Trial Details

```python
async def get_specific_trial_info():
    nct_id = "NCT04280705" # Example trial

    # Get Protocol information (default module)
    protocol_md = await get_trial(nct_id)
    print(f"--- Protocol for {nct_id} (Markdown) ---")
    print(protocol_md)

    # Get Locations as JSON
    locations_json_str = await get_trial(nct_id, module=TrialModule.LOCATIONS, output_json=True)
    print(f"\n--- Locations for {nct_id} (JSON) ---")
    locations_data = json.loads(locations_json_str)
    # Process locations data
    if isinstance(locations_data, dict) and 'protocolSection' in locations_data:
        loc_module = locations_data['protocolSection'].get('contactsLocationsModule', {})
        sites = loc_module.get('locations', [])
        print(f"Found {len(sites)} locations/sites.")
        # ...

asyncio.run(get_specific_trial_info())
```

### Working with Articles

#### Searching Articles

```python
async def find_egfr_articles():
    query = PubmedRequest(
        genes=["EGFR"],
        diseases=["Non-small cell lung cancer"],
        keywords=["resistance"]
    )

    # Get results as Markdown
    markdown_output = await search_articles(query)
    print("--- EGFR NSCLC Resistance Articles (Markdown) ---")
    print(markdown_output)

    # Get results as JSON string
    json_output_str = await search_articles(query, output_json=True)
    print("\n--- EGFR NSCLC Resistance Articles (JSON) ---")
    data = json.loads(json_output_str)
    # Process article search results (list of dicts or error dict)
    if isinstance(data, list) and data:
        print(f"Found {len(data)} articles.")
        print(f"First article PMID: {data[0].get('pmid')}")
        # ...
    elif isinstance(data, dict) and 'error' in data:
         print(f"Error: {data['error']}")

asyncio.run(find_egfr_articles())
```

#### Fetching Article Details

```python
async def get_specific_articles():
    pmids_to_fetch = [34397683, 37296959] # Example PMIDs

    # Get abstracts only (Markdown)
    abstracts_md = await fetch_articles(pmids_to_fetch, full=False)
    print("--- Article Abstracts (Markdown) ---")
    print(abstracts_md)

    # Get abstracts as JSON
    abstracts_json_str = await fetch_articles(pmids_to_fetch, full=False, output_json=True)
    print("\n--- Article Abstracts (JSON) ---")
    abstracts_data = json.loads(abstracts_json_str)
    # Process the list of article details
    if isinstance(abstracts_data, list):
        for article in abstracts_data:
            print(f"PMID: {article.get('pmid')}, Title: {article.get('title')}")
            # ...

    # Attempt to get full text (if available) as JSON
    full_json_str = await fetch_articles(pmids_to_fetch, full=True, output_json=True)
    print("\n--- Article Full Text Attempt (JSON) ---")
    full_data = json.loads(full_json_str)
    # Process potentially including 'full_text' field
    # ...

asyncio.run(get_specific_articles())
```

## Handling Results

**Markdown:** Useful for direct display or logging. Parsing Markdown programmatically can be fragile.

**JSON:** The recommended format for programmatic use. Use Python's `json.loads()` to parse the JSON string into Python dictionaries and lists. You can then access specific fields as needed. Be sure to handle potential errors indicated within the JSON structure (e.g., an `{'error': ...}` dictionary might be returned instead of a list of results).

This guide provides a starting point for using BioMCP as a Python library. Refer to the specific function signatures and Pydantic models within the source code (`src/biomcp/*/*.py`) for the most detailed information on parameters and return types.
