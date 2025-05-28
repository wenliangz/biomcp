# WeDaita-BioMCP Server

A biomedical data access and analysis server built with MCP (Model-Controller-Provider) architecture, providing comprehensive tools for biomedical research and data analysis.

## Features

- **Variant Search**: Search and retrieve genetic variant information with detailed annotations
- **Clinical Trials**: Access comprehensive clinical trial data including protocols, locations, outcomes, and references
- **Article Search**: Search PubMed articles with structured criteria and access full-text content
- **Resource Access**: Access documentation and resources for researchers and users

## Project Structure

```
src/
├── articles/           # PubMed article search functionality
│   ├── tools.py       # Article-related MCP tools
│   ├── search.py      # Article search implementation
│   ├── getter.py      # Article retrieval and full-text access
│   └── autocomplete.py # Entity autocomplete
├── variants/          # Genetic variant functionality
│   ├── tools.py       # Variant-related MCP tools
│   ├── search.py      # Variant search implementation
│   ├── getter.py      # Variant retrieval
│   └── filters.py     # Variant filtering utilities
├── trials/            # Clinical trial functionality
│   ├── tools.py       # Trial-related MCP tools
│   ├── search.py      # Trial search implementation
│   ├── getter.py      # Trial retrieval
│   └── filters.py     # Trial filtering utilities
├── resources/         # Documentation and resources
│   ├── tools.py       # Resource access tools
│   ├── instructions.md # User instructions
│   └── researcher.md  # Researcher documentation
└── server.py          # Main MCP server implementation
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   ```bash
   HOST=0.0.0.0        # Server host (default: 0.0.0.0)
   PORT=8000           # Server port (default: 8000)
   TRANSPORT=sse       # Transport mode (default: sse)
   ```

3. **Run the Server**:
   ```bash
   python -m src.server
   ```

## Docker Deployment

1. **Build the Image**:
   ```bash
   docker build -t wedaita-biomcp:latest .
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

## Available MCP Tools

### Variant Tools
- `search_variants_tool`: Search for genetic variants with semantic search
- `get_variant_tool`: Get detailed variant information and annotations
- `variant_filters`: Apply advanced filtering to variant search results

### Trial Tools
- `search_trials_tool`: Search for clinical trials with semantic search
- `get_trial_tool`: Get detailed trial information
- `trial_protocol_tool`: Retrieve core protocol information including:
  - Trial identification and status
  - Sponsor and collaborators
  - Study design and eligibility
  - Interventions and conditions
- `trial_locations_tool`: Get contact and location details including:
  - Facility names and addresses
  - Contact information
  - Site status
- `trial_outcomes_tool`: Access outcome measures and results including:
  - Primary and secondary outcomes
  - Participant flow
  - Results tables
  - Adverse event summaries
- `trial_references_tool`: Get associated publications and references including:
  - Citations
  - PubMed IDs
  - Reference types

### Article Tools
- `search_articles_tool`: Search PubMed articles with structured criteria:
  - Filter by chemicals
  - Filter by diseases
  - Filter by genes
  - Filter by variants
  - Use custom keywords
- `article_details_tool`: Get full article information including:
  - Title and abstract
  - Full text (if available)
  - Authors and journal
  - Publication date
  - DOI and PMC ID

### Resource Tools
- `get_instructions_tool`: Access user instructions and guidelines
- `get_researcher_tool`: Access researcher documentation and workflows

## Example Usage

### Python SDK
```python
from src.variants.search import VariantQuery, search_variants
from src.trials.search import TrialQuery, search_trials
from src.articles.search import PubmedRequest, search_articles

# Search for pathogenic TP53 variants
query = VariantQuery(gene="TP53", significance="pathogenic", size=5)
results = await search_variants(query, output_json=True)

# Search for melanoma trials
query = TrialQuery(
    conditions=["Melanoma"],
    interventions=["Pembrolizumab"],
    recruiting_status=RecruitingStatus.OPEN,
    phase=TrialPhase.PHASE3
)
results = await search_trials(query, output_json=True)

# Search for articles about BRAF mutations
request = PubmedRequest(
    genes=["BRAF"],
    diseases=["Melanoma"],
    keywords=["V600E mutation"]
)
results = await search_articles(request, output_json=True)
```

### MCP Integration
```python
from mcp.client.session import ClientSession

async with ClientSession() as session:
    # Search for variants
    result = await session.call_tool(
        "search_variants_tool",
        {"query": "BRAF", "limit": 3}
    )
    
    # Get trial protocol
    result = await session.call_tool(
        "trial_protocol_tool",
        {"nct_id": "NCT04280705"}
    )
    
    # Get article details
    result = await session.call_tool(
        "article_details_tool",
        {"pmid": 34397683}
    )
    
    # Search for articles
    result = await session.call_tool(
        "search_articles_tool",
        {
            "genes": ["BRAF"],
            "diseases": ["Melanoma"],
            "keywords": ["V600E mutation"]
        }
    )
    
    # Get trial outcomes
    result = await session.call_tool(
        "trial_outcomes_tool",
        {"nct_id": "NCT04280705"}
    )
```

## Development

1. **Code Organization**:
   - Each module has its own `tools.py` for MCP tool definitions
   - Core functionality is separated from tool implementations
   - Consistent error handling across all tools
   - Modular design for easy extension

2. **Adding New Tools**:
   - Create tool in module's `tools.py`
   - Register tool in module's `register_*_tools` function
   - Add tool registration to `server.py`
   - Update documentation in relevant markdown files

3. **Testing**:
   - Example scripts in `example_scripts/`
   - Integration tests with MCP client
   - Direct SDK usage examples

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
