"""MCP tools for variant search functionality."""

from mcp.server.fastmcp import Context
from src.variants.search import VariantQuery, search_variants
from src.variants.getter import get_variant

async def register_variant_tools(mcp):
    """Register variant-related MCP tools."""
    
    @mcp.tool()
    async def search_variants_tool(ctx: Context, query: str, limit: int = 3) -> str:
        """Search for genetic variants in the MyVariant.info database.

        This tool is specifically for searching genetic variants (mutations, SNPs, etc.) in genes.
        It is NOT for searching general research articles or therapies.
        Use search_articles_tool for searching research papers and therapies.

        Examples of appropriate queries:
        - "BRAF V600E mutation"
        - "TP53 mutations in cancer"
        - "EGFR gene variants"
        - "KRAS mutations"

        Args:
            ctx: The MCP server provided context
            query: Search query string describing the genetic variant you're looking for
            limit: Maximum number of results to return (default: 3)
        """
        try:
            variant_query = VariantQuery(
                gene=query,  # Use the query as a gene name for now
                size=limit
            )
            return await search_variants(variant_query, output_json=True)
        except Exception as e:
            return f"Error searching variants: {str(e)}"

    @mcp.tool()
    async def get_variant_tool(ctx: Context, variant_id: str) -> str:
        """Get detailed information about a specific genetic variant.

        This tool retrieves detailed information about a specific genetic variant
        from the MyVariant.info database. It is NOT for searching general research
        articles or therapies.

        Args:
            ctx: The MCP server provided context
            variant_id: The identifier of the variant to retrieve (e.g., "chr7:g.140453136A>T" or "rs113488022")
        """
        try:
            return await get_variant(variant_id)
        except Exception as e:
            return f"Error retrieving variant: {str(e)}" 